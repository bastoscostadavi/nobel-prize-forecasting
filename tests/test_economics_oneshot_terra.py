"""Verify the Terra comparison arm matches the question and remains isolated."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import economics_oneshot as sol
import economics_oneshot_terra as terra
import economics_committee as committee
import run_economics_oneshot_terra_codex as runner


class TerraOneShotTests(unittest.TestCase):
    def test_matches_committee_execution_and_sol_question(self):
        self.assertEqual(terra.MODEL, committee.MODEL)
        self.assertEqual(terra.REASONING_EFFORT, committee.EFFORT)
        self.assertEqual(terra.PROMPT_PATH.read_bytes(), sol.PROMPT_PATH.read_bytes())
        self.assertEqual(terra.EXACT_PROMPT, sol.EXACT_PROMPT)
        self.assertEqual(len(terra.PREDICTION_IDS), 25)

    def test_shared_protocol_and_dispatcher_are_isolated(self):
        self.assertIsNot(terra.shared, sol.shared)
        self.assertIs(runner.dispatcher.protocol, terra.shared)
        self.assertEqual(sol.shared.MODEL, 'gpt-6.1-sol')
        self.assertEqual(terra.shared.MODEL, 'gpt-5.6-terra')
        self.assertNotEqual(terra.ARM_ROOT, sol.ARM_ROOT)
        self.assertTrue(terra.RETURNED_MODEL_RE.fullmatch('gpt-5.6-terra'))
        self.assertFalse(terra.RETURNED_MODEL_RE.fullmatch('gpt-6.1-sol'))

    def test_requests_are_fresh_with_only_the_unchanged_question(self):
        labels = set()
        for pid in terra.PREDICTION_IDS:
            request = terra.expected_request(pid)
            labels.add(request['independence_label'])
            self.assertEqual(request['prompt_file'], 'prompts/economics_oneshot_gpt_5_6_terra_v1.txt')
            payload = request['dispatch_payload']
            self.assertEqual(payload['model'], committee.MODEL)
            self.assertEqual(payload['reasoning'], {'effort': committee.EFFORT})
            self.assertEqual(payload['input'], [{'role': 'user', 'content': sol.EXACT_PROMPT}])
            self.assertEqual(payload['tools'], [])
            self.assertIsNone(payload['previous_response_id'])
            self.assertFalse(request['execution_requirements']['allow_additional_model_visible_context'])
        self.assertEqual(len(labels), 25)


if __name__ == '__main__':
    unittest.main()
