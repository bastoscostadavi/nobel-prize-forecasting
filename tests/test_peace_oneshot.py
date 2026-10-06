import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import physics_oneshot as physics
import peace_oneshot as peace
import run_peace_oneshot_codex as runner


class PeaceOneShotTests(unittest.TestCase):
    def test_arm_is_isolated_and_model_locked(self):
        self.assertEqual(physics.MODEL, "gpt-6.1-sol")
        self.assertIn("physics", str(physics.ARM_ROOT))
        self.assertIn("peace", str(peace.shared.ARM_ROOT))
        self.assertIsNot(peace.shared, physics)
        self.assertIs(runner.dispatcher.protocol, peace.shared)
        self.assertEqual(peace.MODEL, "gpt-6.1-sol")
        self.assertEqual(peace.REASONING_EFFORT, "high")

    def test_fifty_fresh_requests_expose_only_the_question(self):
        requests = [peace.expected_request(i) for i in peace.PREDICTION_IDS]
        self.assertEqual(len(requests), 50)
        self.assertEqual(len({r["independence_label"] for r in requests}), 50)
        for r in requests:
            self.assertEqual(r["dispatch_payload"]["input"],
                             [{"role": "user", "content": peace.EXACT_PROMPT}])
            self.assertEqual(r["dispatch_payload"]["tools"], [])
            self.assertIsNone(r["dispatch_payload"]["previous_response_id"])
            self.assertFalse(r["execution_requirements"]["allow_additional_model_visible_context"])

    def test_dispatch_audit_rejects_tool_events(self):
        _, _, rejected = runner.dispatcher.parse_events(
            '{"type":"item.completed","item":{"type":"command_execution"}}\n')
        self.assertEqual(rejected, ["command_execution"])


if __name__ == "__main__":
    unittest.main()
