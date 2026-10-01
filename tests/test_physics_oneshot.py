from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "physics_oneshot", ROOT / "scripts" / "physics_oneshot.py"
)
assert SPEC and SPEC.loader
oneshot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(oneshot)


class PhysicsOneShotTests(unittest.TestCase):
    def test_request_has_exactly_one_model_visible_question(self) -> None:
        request = oneshot.expected_request("pred-001")
        payload = request["dispatch_payload"]
        self.assertEqual(
            payload["input"],
            [{"role": "user", "content": oneshot.EXACT_PROMPT}],
        )
        self.assertEqual(payload["tools"], [])
        self.assertIsNone(payload["previous_response_id"])
        serialized = json.dumps(payload).casefold()
        for forbidden in ("candidate", "nomination", "committee", "profile", "run-"):
            self.assertNotIn(forbidden, serialized)

    def test_sixty_unique_external_labels_share_identical_payloads(self) -> None:
        requests = [oneshot.expected_request(item) for item in oneshot.PREDICTION_IDS]
        self.assertEqual(len(requests), 60)
        self.assertEqual(len({item["independence_label"] for item in requests}), 60)
        self.assertEqual(
            len({json.dumps(item["dispatch_payload"], sort_keys=True) for item in requests}),
            1,
        )

    def test_prepare_is_deterministic_and_non_destructive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            arm = Path(directory) / "arm"
            with mock.patch.object(oneshot, "ARM_ROOT", arm):
                oneshot.prepare()
                initial = oneshot.progress()
                self.assertEqual(initial["responded"], 0)
                before = (arm / "pred-060" / "request.json").read_bytes()
                oneshot.prepare(check=True)
                oneshot.prepare()
                self.assertEqual(before, (arm / "pred-060" / "request.json").read_bytes())
                changed = json.loads((arm / "pred-001" / "request.json").read_text())
                changed["dispatch_payload"]["input"].append({"role": "user", "content": "extra"})
                (arm / "pred-001" / "request.json").write_text(json.dumps(changed))
                with self.assertRaises(SystemExit):
                    oneshot.prepare()

    def test_valid_result_binds_verbatim_response(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            arm = Path(directory) / "arm"
            with mock.patch.object(oneshot, "ARM_ROOT", arm):
                oneshot.prepare()
                prediction_dir = arm / "pred-001"
                response = b"I predict Example Person, for an example discovery.\n"
                (prediction_dir / "response.txt").write_bytes(response)
                result = {
                    "schema_version": 1,
                    "arm_id": oneshot.ARM_ID,
                    "prediction_id": "pred-001",
                    "prompt_version": oneshot.PROMPT_VERSION,
                    "execution": {
                        "provider": "openai",
                        "interface": "responses_api",
                        "requested_model": oneshot.MODEL,
                        "returned_model": oneshot.MODEL,
                        "reasoning_effort": oneshot.REASONING_EFFORT,
                        "request_id": "req_test",
                        "response_id": "resp_test",
                        "created_at_utc": "2026-09-30T12:00:00Z",
                        "usage": {
                            "input_tokens": 15,
                            "output_tokens": 12,
                            "reasoning_tokens": 20,
                            "total_tokens": 47,
                        },
                    },
                    "response_file": "response.txt",
                    "response_sha256": hashlib.sha256(response).hexdigest(),
                    "prize_configuration": {
                        "outcome": "award",
                        "prize_parts": [
                            {"credited_names": ["Example Person"], "description": "Example discovery"}
                        ],
                    },
                    "rationale": "An example rationale.",
                }
                (prediction_dir / "result.json").write_text(
                    json.dumps(result, indent=2) + "\n", encoding="utf-8"
                )
                oneshot.validate_result(prediction_dir)
                result["response_sha256"] = "0" * 64
                (prediction_dir / "result.json").write_text(json.dumps(result))
                with self.assertRaises(SystemExit):
                    oneshot.validate_result(prediction_dir)


if __name__ == "__main__":
    unittest.main()
