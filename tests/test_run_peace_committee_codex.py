"""Peace dispatcher boundaries and aggregation; no model requests."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import run_peace_committee_codex as runner


class PeaceDispatchTests(unittest.TestCase):
    def setUp(self):
        runner.configure()

    def test_stage_evidence_is_scoped_to_assigned_persona_and_permitted_rounds(self):
        sim = Path('/private/tmp/isolated-peace/sim-01')
        member = 'toje-asle'
        for stage in runner.STAGES:
            paths = runner.evidence_paths(sim, stage, member)
            profiles = [p for p in paths if p.name == 'profile_terra_v1.md']
            self.assertEqual(len(profiles), 1)
            self.assertEqual(profiles[0].parent.name, member)
            self.assertFalse(any(p.name in {'metadata.json', 'ballot_map.json', 'candidates.json', 'decision.json'} for p in paths))
            self.assertFalse(any('final_ballots' in p.parts for p in paths))
        self.assertEqual(runner.evidence_paths(sim, 'opening', member)[1:], [sim/'longlist.json'])
        self.assertFalse(any('opening' in p.parts for p in runner.evidence_paths(sim, 'round2', member)))
        self.assertFalse(any('round1' in p.parts for p in runner.evidence_paths(sim, 'final', member)))

    def test_runtime_reuses_ephemeral_tools_disabled_model_locked_command(self):
        cmd = runner.dispatch.build_codex_command(Path('/codex'), Path('/empty'), Path('/last.json'))
        self.assertIn('--ephemeral', cmd)
        self.assertIn('--ignore-user-config', cmd)
        self.assertIn('--ignore-rules', cmd)
        self.assertEqual(cmd[cmd.index('-m')+1], 'gpt-5.6-terra')
        self.assertIn('model_reasoning_effort=high', cmd)
        self.assertIn('web_search="disabled"', cmd)
        disabled = [cmd[i+1] for i, item in enumerate(cmd[:-1]) if item == '--disable']
        self.assertTrue({'multi_agent', 'shell_tool', 'unified_exec', 'apps', 'plugins'} <= set(disabled))

    def test_assigned_variant_is_the_only_profile_in_evidence_and_runtime_audit(self):
        sim = Path('/private/tmp/assigned-peace-sim')
        with mock.patch.object(runner.protocol, 'simulation_profile_version', return_value='neutral-terra-v4'):
            runner.configure_simulation(sim)
            for stage in runner.STAGES:
                profile = runner.evidence_paths(sim, stage, 'toje-asle')[0]
                self.assertEqual(profile.name, 'profile_terra_v4.md')
            self.assertEqual(runner.dispatch.PROFILE_VERSION, 'neutral-terra-v4')
            self.assertEqual(runner.dispatch.PROFILE_FILENAME, 'profile_terra_v4.md')

    def test_equal_profile_weight_is_not_pooled_run_frequency(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sims = [root/f'sim-{n:02d}' for n in range(1, 5)]
            for sim in sims:
                sim.mkdir(); (sim/'decision.json').write_text('{}')
            def decision(sim):
                cid = 'CH022' if sim != sims[-1] else 'CH043'
                return {'winner': {'prize_parts': [{'candidate_id': cid, 'discovery': cid, 'laureates': ['A']}]}}
            def version(sim):
                return 'neutral-terra-v1' if sim != sims[-1] else 'neutral-terra-v2'
            with mock.patch.object(runner, 'ROOT', root), mock.patch.object(runner, 'SUMMARY', root/'summary.json'), mock.patch.object(runner.protocol, 'validate_sim', side_effect=decision), mock.patch.object(runner.protocol, 'simulation_profile_version', side_effect=version):
                value = runner.summarize(sims)
            self.assertEqual(value['configurations'][0]['frequency_among_completed'], .75)
            equal = value['equal_profile_weight_summary']
            self.assertTrue(equal['available'])
            self.assertEqual([c['mean_frequency'] for c in equal['configurations']], [.5, .5])

    def test_summary_merges_same_configuration_across_different_ballot_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sims = [root/'sim-01', root/'sim-02']
            for sim in sims:
                sim.mkdir()
                (sim/'decision.json').write_text('{}')
            def decision(sim):
                return {'winner': {'prize_parts': [{'ballot_id': 'B001' if sim == sims[0] else 'B042',
                        'candidate_id': 'M048', 'discovery': 'Unfolded protein response',
                        'laureates': ['Peter Walter', 'Kazutoshi Mori'] if sim == sims[0] else ['Kazutoshi Mori', 'Peter Walter']}]}}
            with mock.patch.object(runner, 'ROOT', root), mock.patch.object(runner, 'SUMMARY', root/'summary.json'), mock.patch.object(runner.protocol, 'validate_sim', side_effect=decision):
                value = runner.summarize(sims)
            self.assertEqual(len(value['configurations']), 1)
            self.assertEqual(value['configurations'][0]['count'], 2)
            self.assertEqual(value['configurations'][0]['frequency_among_completed'], 1)
            self.assertNotIn('ballot_id', value['configurations'][0]['prize_parts'][0])

    def test_failure_progress_preserves_original_error_when_decision_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sim = root/'sim-01';sim.mkdir();(sim/'decision.json').write_text('{}')
            with mock.patch.object(runner, 'PROGRESS', root/'progress.json'), mock.patch.object(runner.protocol, 'validate_sim', side_effect=SystemExit('invalid decision')):
                runner.progress([sim], 'failed', sim, 'original failure')
            value = json.loads((root/'progress.json').read_text())
            self.assertEqual(value['error'], 'original failure')
            self.assertEqual(value['simulations']['sim-01']['status'], 'failed')

    def test_capacity_retry_waits_and_keeps_same_model_and_stage(self):
        sim = Path('/private/tmp/capacity-test')
        with mock.patch.object(runner.dispatch, 'run_stage', side_effect=[RuntimeError('capacity'), None]) as run, mock.patch.object(runner, 'missing_requests_hit_capacity', return_value=True), mock.patch.object(runner.time, 'sleep') as sleep:
            runner.run_stage_with_capacity_retry(sim, 'final', Path('/codex'), 1, 2)
        self.assertEqual(run.call_count, 2)
        self.assertEqual(run.call_args_list[0], run.call_args_list[1])
        sleep.assert_called_once_with(60)

    def test_noncapacity_failures_are_not_automatically_retried(self):
        with mock.patch.object(runner.dispatch, 'run_stage', side_effect=RuntimeError('invalid output')) as run, mock.patch.object(runner, 'missing_requests_hit_capacity', return_value=False), mock.patch.object(runner.time, 'sleep') as sleep:
            with self.assertRaises(RuntimeError):
                runner.run_stage_with_capacity_retry(Path('/sim'), 'final', Path('/codex'), 1, 2)
        self.assertEqual(run.call_count, 1)
        sleep.assert_not_called()


if __name__ == '__main__':
    unittest.main()
