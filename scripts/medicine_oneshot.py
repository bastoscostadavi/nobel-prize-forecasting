#!/usr/bin/env python3
"""Prepare and validate 60 zero-context GPT-6 Sol Medicine predictions."""

from __future__ import annotations

import re

import physics_oneshot as shared


ROOT = shared.ROOT
ARM_ROOT = ROOT / "results" / "medicine" / "oneshot" / "gpt-6-sol"
PROMPT_PATH = ROOT / "prompts" / "medicine_oneshot_gpt_6_sol_v1.txt"
SCHEMA_PATH = ROOT / "schemas" / "medicine_oneshot_prediction_v1.schema.json"
SCHEMA_VERSION = 1
ARM_ID = "medicine-oneshot-gpt-6-sol-high-v1"
PROMPT_VERSION = "medicine-oneshot-gpt-6-sol-v1"
MODEL = "gpt-6-sol"
REASONING_EFFORT = "high"
EXACT_PROMPT = (
    "Who will win the 2026 Nobel Prize in Physiology or Medicine? Predict the prize: "
    "the discovery or invention, and the one to three laureates. Answer from your own "
    "knowledge only; do not search the web or read any files."
)
PREDICTION_IDS = shared.PREDICTION_IDS
PREDICTION_ID_RE = shared.PREDICTION_ID_RE
RETURNED_MODEL_RE = re.compile(r"^gpt-6-sol(?:-.+)?$")


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
        "prompt_file": "prompts/medicine_oneshot_gpt_6_sol_v1.txt",
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
            "Sixty independent zero-context predictions of the 2026 Nobel Prize "
            "in Physiology or Medicine."
        ),
        "prediction_count": len(PREDICTION_IDS),
        "prediction_ids": list(PREDICTION_IDS),
        "prompt_version": PROMPT_VERSION,
        "prompt_file": "prompts/medicine_oneshot_gpt_6_sol_v1.txt",
        "prompt_sha256": shared.sha256_bytes(shared.prompt_bytes()),
        "model": MODEL,
        "reasoning_effort": REASONING_EFFORT,
        "result_schema": "schemas/medicine_oneshot_prediction_v1.schema.json",
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


if __name__ == "__main__":
    shared.main()
