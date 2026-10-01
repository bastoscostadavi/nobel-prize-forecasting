from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location(
    "run_terra_committee_codex", ROOT / "scripts" / "run_terra_committee_codex.py"
)
assert SPEC and SPEC.loader
dispatcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dispatcher)


class TerraCommitteeDispatcherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sim = dispatcher.simulation_path("gpt-6-sol", 2, 4)

    def test_default_ready_tranche_has_thirty_simulations(self) -> None:
        sims = dispatcher.selected_simulations(dispatcher.LISTS, range(1, 4), range(1, 6))
        self.assertEqual(len(sims), 30)
        self.assertEqual(len(set(sims)), 30)

    def test_full_design_has_sixty_simulations_and_1980_requests(self) -> None:
        sims = dispatcher.selected_simulations(dispatcher.LISTS, range(1, 7), range(1, 6))
        requests_per_sim = sum(len(dispatcher.stage_members(stage)) for stage in dispatcher.STAGES)
        self.assertEqual(len(sims), 60)
        self.assertEqual(requests_per_sim, 33)
        self.assertEqual(len(sims) * requests_per_sim, 1980)

    def test_stage_evidence_boundaries(self) -> None:
        member = "danielsson-ulf"
        labels = {
            stage: [dispatcher.relative_label(path) for path in dispatcher.evidence_paths(self.sim, stage, member)]
            for stage in dispatcher.STAGES
        }
        self.assertEqual(len(labels["opening"]), 2)
        self.assertTrue(labels["opening"][0].endswith(f"/{member}/profile.md"))
        self.assertTrue(labels["opening"][1].endswith("/longlist.json"))
        self.assertEqual(len(labels["round1"]), 10)
        self.assertTrue(all("/opening/" in item for item in labels["round1"][2:]))
        self.assertEqual(len(labels["chair"]), 10)
        self.assertTrue(all("/round1/" in item for item in labels["chair"][2:]))
        self.assertEqual(len(labels["round2"]), 11)
        self.assertTrue(labels["round2"][-1].endswith("chair_summary_round1.json"))
        self.assertEqual(len(labels["final"]), 11)
        self.assertTrue(all("/round2/" in item for item in labels["final"][2:-1]))
        self.assertTrue(labels["final"][-1].endswith("proposal_slate.json"))
        serialized = json.dumps(labels)
        for forbidden in ("ballot_map.json", "candidates.json", "nominations/"):
            self.assertNotIn(forbidden, serialized)

    def test_codex_command_is_ephemeral_model_locked_and_toolless(self) -> None:
        command = dispatcher.build_codex_command(
            Path("/codex"), Path("/empty-workspace"), Path("/tmp/last.json")
        )
        joined = " ".join(map(str, command))
        self.assertIn("--ephemeral", command)
        self.assertIn("--ignore-user-config", command)
        self.assertIn("--ignore-rules", command)
        self.assertIn(dispatcher.MODEL, command)
        self.assertIn(f"model_reasoning_effort={dispatcher.EFFORT}", command)
        self.assertIn("read-only", command)
        for feature in (
            "apps", "browser_use", "computer_use", "multi_agent", "plugins",
            "shell_tool", "unified_exec", "workspace_dependencies",
        ):
            self.assertIn(f"--disable {feature}", joined)
        self.assertEqual(command[-1], "-")

    def test_json_response_must_be_bare_object(self) -> None:
        self.assertEqual(dispatcher.parse_json_response('{"ok": true}\n'), {"ok": True})
        with self.assertRaises(ValueError):
            dispatcher.parse_json_response('```json\n{"ok": true}\n```')
        with self.assertRaises(ValueError):
            dispatcher.parse_json_response("[]")

    def test_number_selectors(self) -> None:
        self.assertEqual(dispatcher.parse_number_selector("1-3,5", range(1, 7), "runs"), (1, 2, 3, 5))
        with self.assertRaises(SystemExit):
            dispatcher.parse_number_selector("0-3", range(1, 7), "runs")
        with self.assertRaises(SystemExit):
            dispatcher.parse_number_selector("3-1", range(1, 7), "runs")


if __name__ == "__main__":
    unittest.main()
