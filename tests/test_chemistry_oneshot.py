import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import physics_oneshot as physics
import chemistry_oneshot as chemistry
import run_chemistry_oneshot_codex as runner


class ChemistryOneShotTests(unittest.TestCase):
    def test_arm_is_isolated_and_model_locked(self):
        self.assertEqual(physics.MODEL, "gpt-6.1-sol")
        self.assertIn("physics", str(physics.ARM_ROOT))
        self.assertIn("chemistry", str(chemistry.shared.ARM_ROOT))
        self.assertIsNot(chemistry.shared, physics)
        self.assertIs(runner.dispatcher.protocol, chemistry.shared)
        self.assertEqual(chemistry.MODEL, "gpt-6.1-sol")
        self.assertEqual(chemistry.REASONING_EFFORT, "high")

    def test_sixty_fresh_requests_expose_only_the_question(self):
        requests = [chemistry.expected_request(i) for i in chemistry.PREDICTION_IDS]
        self.assertEqual(len(requests), 60)
        self.assertEqual(len({r["independence_label"] for r in requests}), 60)
        for r in requests:
            self.assertEqual(r["dispatch_payload"]["input"],
                             [{"role": "user", "content": chemistry.EXACT_PROMPT}])
            self.assertEqual(r["dispatch_payload"]["tools"], [])
            self.assertIsNone(r["dispatch_payload"]["previous_response_id"])
            self.assertFalse(r["execution_requirements"]["allow_additional_model_visible_context"])

    def test_dispatch_audit_rejects_tool_events(self):
        _, _, rejected = runner.dispatcher.parse_events(
            '{"type":"item.completed","item":{"type":"command_execution"}}\n')
        self.assertEqual(rejected, ["command_execution"])


if __name__ == "__main__":
    unittest.main()
