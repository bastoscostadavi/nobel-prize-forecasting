#!/usr/bin/env python3
"""Prepare and validate 25 zero-context GPT-6.1 Sol Literature predictions."""

from __future__ import annotations

import re

import importlib.util
from pathlib import Path

# Keep the Physics and Medicine arms untouched when this module is imported.
_SPEC = importlib.util.spec_from_file_location(
    "_literature_oneshot_shared", Path(__file__).with_name("physics_oneshot.py")
)
assert _SPEC and _SPEC.loader
shared = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(shared)


ROOT = shared.ROOT
ARM_ROOT = ROOT / "results" / "literature" / "oneshot" / "gpt-6.1-sol"
PROMPT_PATH = ROOT / "prompts" / "literature_oneshot_gpt_6_1_sol_v1.txt"
SCHEMA_PATH = ROOT / "schemas" / "literature_oneshot_prediction_v1.schema.json"
SCHEMA_VERSION = 1
ARM_ID = "literature-oneshot-gpt-6.1-sol-high-v1"
PROMPT_VERSION = "literature-oneshot-gpt-6.1-sol-v1"
MODEL = "gpt-6.1-sol"
REASONING_EFFORT = "high"
EXACT_PROMPT = (
    "Who will win the 2026 Nobel Prize in Literature? Predict the laureate and the literary achievement. "
    "Answer from your own knowledge only; do not search the web or read any files."
)
PREDICTION_IDS = tuple(f"pred-{index:03d}" for index in range(1, 26))
PREDICTION_ID_RE = re.compile(r"^pred-(00[1-9]|01[0-9]|02[0-5])$")
RETURNED_MODEL_RE = re.compile(r"^gpt-6\.1-sol(?:-.+)?$")


def expected_request(prediction_id: str) -> dict:
    if prediction_id not in PREDICTION_IDS:
        shared.fail(f"invalid prediction ID: {prediction_id}")
    prompt = shared.prompt_bytes()
    return {
        "schema_version": SCHEMA_VERSION,
        "arm_id": ARM_ID,
        "prediction_id": prediction_id,
        "independence_label": f"{ARM_ID}:{prediction_id}",
        "prompt_version": PROMPT_VERSION,
        "prompt_file": "prompts/literature_oneshot_gpt_6_1_sol_v1.txt",
        "prompt_sha256": shared.sha256_bytes(prompt),
        "dispatch_payload": {
            "model": MODEL,
            "reasoning": {"effort": REASONING_EFFORT},
            "input": [{"role": "user", "content": EXACT_PROMPT}],
            "tools": [],
            "previous_response_id": None,
        },
        "execution_requirements": {
            "fresh_request": True,
            "fresh_conversation": True,
            "one_request_per_prediction": True,
            "allow_additional_model_visible_context": False,
        },
    }


def expected_manifest() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "arm_id": ARM_ID,
        "description": (
            "Twenty-five independent zero-context predictions of the 2026 Nobel Prize "
            "in Literature."
        ),
        "prediction_count": len(PREDICTION_IDS),
        "prediction_ids": list(PREDICTION_IDS),
        "prompt_version": PROMPT_VERSION,
        "prompt_file": "prompts/literature_oneshot_gpt_6_1_sol_v1.txt",
        "prompt_sha256": shared.sha256_bytes(shared.prompt_bytes()),
        "model": MODEL,
        "reasoning_effort": REASONING_EFFORT,
        "result_schema": "schemas/literature_oneshot_prediction_v1.schema.json",
        "independence": {
            "unit": "one fresh request in one fresh conversation",
            "model_visible_input": "the exact versioned user question only",
            "candidate_inputs": False,
            "nomination_run_inputs": False,
            "profile_inputs": False,
            "committee_inputs": False,
            "prior_response_state": False,
            "tools": False,
        },
    }


def configure() -> None:
    shared.ARM_ROOT = ARM_ROOT
    shared.PROMPT_PATH = PROMPT_PATH
    shared.SCHEMA_PATH = SCHEMA_PATH
    shared.SCHEMA_VERSION = SCHEMA_VERSION
    shared.ARM_ID = ARM_ID
    shared.PROMPT_VERSION = PROMPT_VERSION
    shared.MODEL = MODEL
    shared.REASONING_EFFORT = REASONING_EFFORT
    shared.EXACT_PROMPT = EXACT_PROMPT
    shared.PREDICTION_IDS = PREDICTION_IDS
    shared.PREDICTION_ID_RE = PREDICTION_ID_RE
    shared.RETURNED_MODEL_RE = RETURNED_MODEL_RE
    shared.expected_request = expected_request
    shared.expected_manifest = expected_manifest


configure()
_original_validate = shared.validate_result

def validate_result(directory):
    _original_validate(directory)
    result = shared.load_json(directory / "result.json")
    if result["prize_configuration"]["outcome"] == "award":
        parts = result["prize_configuration"]["prize_parts"]
        if len(parts) != 1 or len(parts[0]["credited_names"]) != 1:
            shared.fail("Literature primary-pick transcription must identify exactly one writer")
shared.validate_result = validate_result


if __name__ == "__main__":
    shared.main()
