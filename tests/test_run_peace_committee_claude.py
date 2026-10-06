"""Claude runtime audit and isolation tests; never make model calls."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import run_peace_committee_claude as runner


def runtime(*, model='claude-sonnet-5-5', content=None, tools=None, error=False):
    events = [
        {'type': 'system', 'subtype': 'init', 'session_id': 'isolated',
         'model': model, 'tools': tools or [], 'mcp_servers': []},
        {'type': 'assistant', 'message': {'model': model, 'content': content or [{'type': 'text', 'text': '{}'}]}},
        {'type': 'result', 'subtype': 'error_during_execution' if error else 'success',
         'is_error': error, 'result': '{}', 'modelUsage': {model: {}},
         'usage': {'input_tokens': 10, 'output_tokens': 4,
                   'cache_read_input_tokens': 3, 'cache_creation_input_tokens': 2}},
    ]
    return '\n'.join(json.dumps(event) for event in events) + '\n'


class ClaudePeaceTests(unittest.TestCase):
    def setUp(self):
        runner.configure()

    def test_cli_locks_model_and_disables_tools_and_customizations(self):
        cmd = runner.build_claude_command(Path('/claude'))
        self.assertEqual(cmd[cmd.index('--model')+1], 'claude-sonnet-5-5')
        self.assertEqual(cmd[cmd.index('--effort')+1], 'high')
        self.assertEqual(cmd[cmd.index('--tools')+1], '')
        self.assertEqual(json.loads(cmd[cmd.index('--mcp-config')+1]), {'mcpServers': {}})
        for option in ('--strict-mcp-config', '--safe-mode', '--disable-slash-commands', '--no-session-persistence'):
            self.assertIn(option, cmd)
        self.assertNotIn('--fallback-model', cmd)
        self.assertEqual(cmd[cmd.index('--setting-sources')+1], '')

    def test_runtime_uses_actual_model_and_preserves_provider_usage(self):
        audit = runner.parse_events(runtime())
        self.assertEqual(audit['errors'], [])
        self.assertEqual(audit['actual_models'], ['claude-sonnet-5-5'])
        self.assertEqual(audit['usage']['total_tokens'], 19)
        self.assertEqual(audit['usage']['cached_input_tokens'], 3)
        self.assertEqual(audit['raw_response'], '{}')

    def test_model_drift_and_tool_activity_are_rejected(self):
        for raw in (runtime(model='claude-opus-5-5'), runtime(tools=['Read']),
                    runtime(content=[{'type': 'tool_use', 'name': 'Read'}]), runtime(error=True)):
            with self.subTest(raw=raw):
                self.assertTrue(runner.parse_events(raw)['errors'])
        self.assertTrue(runner.parse_events('{}')['errors'])

    def test_claude_protocol_is_private_and_does_not_change_codex_model(self):
        import peace_committee
        import run_peace_committee_codex
        self.assertEqual(peace_committee.MODEL, 'gpt-5.6-terra')
        self.assertEqual(run_peace_committee_codex.protocol.MODEL, 'gpt-5.6-terra')
        self.assertEqual(runner.protocol.MODEL, 'claude-sonnet-5-5')
        self.assertIsNot(runner.dispatch, run_peace_committee_codex.dispatch)

    def test_rejected_validation_preserves_audit_and_removes_canonical_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sim, destination, attempt = root/'sim-01', root/'opening/member.json', root/'attempt-001'
            attempt.mkdir()
            completed = subprocess.CompletedProcess([], 0, runtime(), '')
            with mock.patch.object(runner.dispatch, 'output_path', return_value=destination), \
                 mock.patch.object(runner.cohort, 'build_prompt', return_value=('isolated prompt', [{'path': 'allowed'}])), \
                 mock.patch.object(runner.dispatch, 'runtime_directory', return_value=root/'runtime'), \
                 mock.patch.object(runner.dispatch, 'next_attempt', return_value=attempt), \
                 mock.patch.object(runner.dispatch, 'validate_member_output', side_effect=ValueError('bad schema')):
                with self.assertRaisesRegex(RuntimeError, 'bad schema'):
                    runner.run_request(sim, 'opening', 'member', Path('/claude'), 1, runner=mock.Mock(return_value=completed))
            self.assertFalse(destination.exists())
            self.assertEqual((attempt/'runtime.jsonl').read_text(), completed.stdout)
            self.assertEqual((attempt/'prompt.txt').read_text(), 'isolated prompt')
            execution = json.loads((attempt/'execution.json').read_text())
            self.assertEqual(execution['status'], 'failed')
            self.assertEqual(execution['provider'], 'anthropic')
            self.assertTrue((attempt/'rejected-output.json').exists())

    def test_model_drift_never_publishes_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            destination, attempt = root/'result.json', root/'attempt-001'
            attempt.mkdir()
            completed = subprocess.CompletedProcess([], 0, runtime(model='fallback'), '')
            with mock.patch.object(runner.dispatch, 'output_path', return_value=destination), \
                 mock.patch.object(runner.cohort, 'build_prompt', return_value=('prompt', [])), \
                 mock.patch.object(runner.dispatch, 'runtime_directory', return_value=root/'runtime'), \
                 mock.patch.object(runner.dispatch, 'next_attempt', return_value=attempt):
                with self.assertRaisesRegex(RuntimeError, 'differ from locked model'):
                    runner.run_request(root/'sim', 'opening', 'member', Path('/claude'), 1, runner=mock.Mock(return_value=completed))
            self.assertFalse(destination.exists())


if __name__ == '__main__':
    unittest.main()
