"""Scaffold and validate the zero-context GPT-6.1 Sol physics arm.

This module never calls a model. It prepares 60 independent request records,
validates saved verbatim responses plus post-hoc prediction transcriptions, and
reports arm progress.

The dispatch payload in each request.json is the complete model-visible input.
Do not add system/developer text, candidate files, prior-response state, tools,
or conversation history when executing a request.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ARM_ROOT = ROOT / "results" / "physics" / "oneshot" / "gpt-6.1-sol"
PROMPT_PATH = ROOT / "prompts" / "physics_oneshot_gpt_6_1_sol_v1.txt"
SCHEMA_PATH = ROOT / "schemas" / "physics_oneshot_prediction_v1.schema.json"

SCHEMA_VERSION = 1
ARM_ID = "physics-oneshot-gpt-6.1-sol-high-v1"
PROMPT_VERSION = "physics-oneshot-gpt-6.1-sol-v1"
MODEL = "gpt-6.1-sol"
REASONING_EFFORT = "high"
EXACT_PROMPT = "Who do you predict will win the 2026 Nobel Prize in Physics?"
PREDICTION_IDS = tuple(f"pred-{index:03d}" for index in range(1, 61))
PREDICTION_ID_RE = re.compile(r"^pred-(00[1-9]|0[1-5][0-9]|060)$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RETURNED_MODEL_RE = re.compile(r"^gpt-6\.1-sol(?:-.+)?$")


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def encode_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read valid JSON from {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"expected a JSON object in {path}")
    return value


def prompt_bytes() -> bytes:
    try:
        value = PROMPT_PATH.read_bytes()
    except OSError as exc:
        fail(f"cannot read prompt {PROMPT_PATH}: {exc}")
    if value != (EXACT_PROMPT + "\n").encode("utf-8"):
        fail(f"{PROMPT_PATH} must contain exactly the versioned question and one newline")
    return value


def expected_request(prediction_id: str) -> dict:
    if prediction_id not in PREDICTION_IDS:
        fail(f"invalid prediction ID: {prediction_id}")
    prompt = prompt_bytes()
    return {
        "schema_version": SCHEMA_VERSION,
        "arm_id": ARM_ID,
        "prediction_id": prediction_id,
        "independence_label": f"{ARM_ID}:{prediction_id}",
        "prompt_version": PROMPT_VERSION,
        "prompt_file": "prompts/physics_oneshot_gpt_6_1_sol_v1.txt",
        "prompt_sha256": sha256_bytes(prompt),
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
        "description": "Sixty independent zero-context predictions of the 2026 Nobel Prize in Physics.",
        "prediction_count": len(PREDICTION_IDS),
        "prediction_ids": list(PREDICTION_IDS),
        "prompt_version": PROMPT_VERSION,
        "prompt_file": "prompts/physics_oneshot_gpt_6_1_sol_v1.txt",
        "prompt_sha256": sha256_bytes(prompt_bytes()),
        "model": MODEL,
        "reasoning_effort": REASONING_EFFORT,
        "result_schema": "schemas/physics_oneshot_prediction_v1.schema.json",
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


def validate_request(path: Path, prediction_id: str) -> None:
    expected = expected_request(prediction_id)
    actual = load_json(path)
    if actual != expected:
        fail(f"{path} differs from the deterministic zero-context request")


def validate_nullable_text(value: object, field: str) -> None:
    if value is not None and (not isinstance(value, str) or not value.strip()):
        fail(f"{field} must be null or a non-empty string")


def validate_nullable_count(value: object, field: str) -> None:
    if value is not None and (type(value) is not int or value < 0):
        fail(f"{field} must be null or a non-negative integer")


def validate_result(prediction_dir: Path) -> None:
    prediction_id = prediction_dir.name
    if not PREDICTION_ID_RE.fullmatch(prediction_id):
        fail(f"invalid prediction directory: {prediction_dir}")
    validate_request(prediction_dir / "request.json", prediction_id)
    result = load_json(prediction_dir / "result.json")
    expected_keys = {
        "schema_version",
        "arm_id",
        "prediction_id",
        "prompt_version",
        "execution",
        "response_file",
        "response_sha256",
        "prize_configuration",
        "rationale",
    }
    if set(result) != expected_keys:
        fail(f"{prediction_dir / 'result.json'} keys differ from the result schema")
    if (
        result["schema_version"] != SCHEMA_VERSION
        or result["arm_id"] != ARM_ID
        or result["prediction_id"] != prediction_id
        or result["prompt_version"] != PROMPT_VERSION
        or result["response_file"] != "response.txt"
    ):
        fail(f"identity metadata differs in {prediction_dir / 'result.json'}")

    response_path = prediction_dir / "response.txt"
    try:
        response = response_path.read_bytes()
    except OSError as exc:
        fail(f"cannot read verbatim response {response_path}: {exc}")
    if not response:
        fail(f"verbatim response is empty: {response_path}")
    response_hash = result["response_sha256"]
    if not isinstance(response_hash, str) or not SHA256_RE.fullmatch(response_hash):
        fail(f"invalid response_sha256 in {prediction_dir / 'result.json'}")
    if response_hash != sha256_bytes(response):
        fail(f"response_sha256 does not match {response_path}")

    execution = result["execution"]
    execution_keys = {
        "provider",
        "interface",
        "requested_model",
        "returned_model",
        "reasoning_effort",
        "request_id",
        "response_id",
        "created_at_utc",
        "usage",
    }
    if not isinstance(execution, dict) or set(execution) != execution_keys:
        fail(f"execution metadata keys differ in {prediction_dir / 'result.json'}")
    if (
        execution["provider"] != "openai"
        or execution["requested_model"] != MODEL
        or execution["reasoning_effort"] != REASONING_EFFORT
    ):
        fail(f"model execution metadata differs in {prediction_dir / 'result.json'}")
    if (
        not isinstance(execution["returned_model"], str)
        or not RETURNED_MODEL_RE.fullmatch(execution["returned_model"])
    ):
        fail("execution.returned_model must identify GPT-6.1 Sol exactly")
    if not isinstance(execution["interface"], str) or not execution["interface"].strip():
        fail("execution.interface must be a non-empty string")
    for key in ("request_id", "response_id"):
        validate_nullable_text(execution[key], f"execution.{key}")
    created = execution["created_at_utc"]
    if not isinstance(created, str) or not created.endswith("Z"):
        fail("execution.created_at_utc must be a UTC ISO-8601 timestamp ending in Z")
    try:
        datetime.fromisoformat(created.removesuffix("Z") + "+00:00")
    except ValueError:
        fail("execution.created_at_utc must be a valid ISO-8601 timestamp")
    usage = execution["usage"]
    usage_keys = {"input_tokens", "output_tokens", "reasoning_tokens", "total_tokens"}
    if not isinstance(usage, dict) or set(usage) != usage_keys:
        fail("execution.usage keys differ")
    for key in usage_keys:
        validate_nullable_count(usage[key], f"execution.usage.{key}")
    known_counts = [usage[key] for key in ("input_tokens", "output_tokens")]
    if all(value is not None for value in known_counts) and usage["total_tokens"] is not None:
        if usage["total_tokens"] < sum(known_counts):
            fail("execution.usage.total_tokens is smaller than input plus output tokens")

    configuration = result["prize_configuration"]
    if not isinstance(configuration, dict) or set(configuration) != {"outcome", "prize_parts"}:
        fail("prize_configuration keys differ")
    outcome, parts = configuration["outcome"], configuration["prize_parts"]
    if outcome not in {"award", "no_award"} or not isinstance(parts, list):
        fail("invalid prize_configuration outcome or prize_parts")
    if (outcome == "no_award" and parts) or (outcome == "award" and not 1 <= len(parts) <= 2):
        fail("no_award requires zero parts; award requires one or two parts")
    all_names: list[str] = []
    for index, part in enumerate(parts, start=1):
        if not isinstance(part, dict) or set(part) != {"credited_names", "description"}:
            fail(f"prize part {index} keys differ")
        names = part["credited_names"]
        if (
            not isinstance(names, list)
            or not 1 <= len(names) <= 3
            or len(names) != len(set(names))
            or not all(isinstance(name, str) and name.strip() for name in names)
        ):
            fail(f"prize part {index} credited_names must contain 1-3 unique exact names")
        all_names.extend(names)
        validate_nullable_text(part["description"], f"prize part {index}.description")
    if len(all_names) > 3 or len(all_names) != len(set(all_names)):
        fail("a prize configuration may credit at most three unique people total")
    validate_nullable_text(result["rationale"], "rationale")


def prepare(check: bool = False) -> None:
    manifest = expected_manifest()
    if check:
        if load_json(ARM_ROOT / "manifest.json") != manifest:
            fail(f"{ARM_ROOT / 'manifest.json'} differs from the deterministic manifest")
        for prediction_id in PREDICTION_IDS:
            validate_request(ARM_ROOT / prediction_id / "request.json", prediction_id)
        print(f"OK: checked {len(PREDICTION_IDS)} deterministic zero-context requests")
        return

    ARM_ROOT.mkdir(parents=True, exist_ok=True)
    manifest_path = ARM_ROOT / "manifest.json"
    if manifest_path.exists() and load_json(manifest_path) != manifest:
        fail(f"refusing to replace differing manifest: {manifest_path}")
    manifest_path.write_text(encode_json(manifest), encoding="utf-8")
    for prediction_id in PREDICTION_IDS:
        prediction_dir = ARM_ROOT / prediction_id
        prediction_dir.mkdir(parents=True, exist_ok=True)
        request_path = prediction_dir / "request.json"
        expected = expected_request(prediction_id)
        if request_path.exists() and load_json(request_path) != expected:
            fail(f"refusing to replace differing request: {request_path}")
        request_path.write_text(encode_json(expected), encoding="utf-8")
    print(f"OK: prepared {len(PREDICTION_IDS)} deterministic zero-context requests")


def progress(write: bool = False) -> dict:
    prepared, responded, complete, invalid = [], [], [], []
    for prediction_id in PREDICTION_IDS:
        prediction_dir = ARM_ROOT / prediction_id
        try:
            validate_request(prediction_dir / "request.json", prediction_id)
            prepared.append(prediction_id)
        except SystemExit:
            invalid.append(prediction_id)
            continue
        if (prediction_dir / "response.txt").exists():
            responded.append(prediction_id)
        artifacts = [prediction_dir / "response.txt", prediction_dir / "result.json"]
        if all(path.exists() for path in artifacts):
            try:
                validate_result(prediction_dir)
                complete.append(prediction_id)
            except SystemExit:
                invalid.append(prediction_id)
    status = {
        "schema_version": SCHEMA_VERSION,
        "arm_id": ARM_ID,
        "expected": len(PREDICTION_IDS),
        "prepared": len(prepared),
        "responded": len(responded),
        "complete": len(complete),
        "pending": len(PREDICTION_IDS) - len(complete),
        "invalid_prediction_ids": sorted(set(invalid)),
    }
    if write:
        ARM_ROOT.mkdir(parents=True, exist_ok=True)
        (ARM_ROOT / "progress.json").write_text(encode_json(status), encoding="utf-8")
    return status


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser("prepare", help="create the 60 request records")
    prepare_parser.add_argument("--check", action="store_true")
    validate_parser = subparsers.add_parser("validate", help="validate one or all completed results")
    validate_parser.add_argument("prediction_dirs", nargs="*", type=Path)
    progress_parser = subparsers.add_parser("progress", help="show deterministic arm progress")
    progress_parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    if args.command == "prepare":
        prepare(args.check)
    elif args.command == "validate":
        paths = args.prediction_dirs or [ARM_ROOT / item for item in PREDICTION_IDS]
        for path in paths:
            validate_result(path)
        print(f"OK: validated {len(paths)} completed one-shot predictions")
    else:
        print(encode_json(progress(args.write)), end="")


if __name__ == "__main__":
    main()
