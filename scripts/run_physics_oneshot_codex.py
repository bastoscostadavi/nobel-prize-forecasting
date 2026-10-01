"""Run the 60 zero-context GPT-6.1 Sol predictions through Codex CLI.

Each prediction is a fresh ephemeral invocation in an empty temporary working
directory.  The versioned question is the only user message.  Successful runs
save the verbatim final answer and the raw JSONL event stream for auditability.

This dispatcher intentionally does not transcribe answers into structured
winner fields; that is a separate, post-hoc analysis step.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

import physics_oneshot as protocol


DEFAULT_CODEX = Path(
    "/Applications/ChatGPT.app/Contents/Resources/"
    "codex-cli/CodexCLI.app/Contents/MacOS/codex"
)
ALLOWED_ITEM_TYPES = {"agent_message", "reasoning"}


def encode(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def parse_events(raw: str) -> tuple[str | None, dict[str, int | None], list[str]]:
    thread_id = None
    usage = {
        "input_tokens": None,
        "cached_input_tokens": None,
        "output_tokens": None,
        "reasoning_tokens": None,
        "total_tokens": None,
    }
    disallowed_items: list[str] = []
    for line in raw.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "thread.started":
            thread_id = event.get("thread_id")
        item = event.get("item")
        if isinstance(item, dict):
            item_type = item.get("type")
            if isinstance(item_type, str) and item_type not in ALLOWED_ITEM_TYPES:
                disallowed_items.append(item_type)
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            observed = event["usage"]
            for key in usage:
                value = observed.get(key)
                if type(value) is int and value >= 0:
                    usage[key] = value
    if usage["total_tokens"] is None:
        known = [usage["input_tokens"], usage["output_tokens"]]
        if all(type(value) is int for value in known):
            usage["total_tokens"] = sum(known)  # type: ignore[arg-type]
    return thread_id, usage, sorted(set(disallowed_items))


def run_one(prediction_id: str, codex: Path) -> str:
    prediction_dir = protocol.ARM_ROOT / prediction_id
    protocol.validate_request(prediction_dir / "request.json", prediction_id)
    response_path = prediction_dir / "response.txt"
    event_path = prediction_dir / "runtime.jsonl"
    execution_path = prediction_dir / "execution.json"
    if response_path.exists() or event_path.exists() or execution_path.exists():
        return f"SKIP {prediction_id}: output already exists"

    with tempfile.TemporaryDirectory(prefix=f"physics-{prediction_id}-") as directory:
        temp = Path(directory)
        last_message = temp / "response.txt"
        command = [
            str(codex),
            "exec",
            "--ephemeral",
            "--ignore-user-config",
            "--ignore-rules",
            "--skip-git-repo-check",
            "--json",
            "-c",
            'web_search="disabled"',
            "--disable",
            "apps",
            "--disable",
            "browser_use",
            "--disable",
            "browser_use_external",
            "--disable",
            "computer_use",
            "--disable",
            "image_generation",
            "--disable",
            "multi_agent",
            "--disable",
            "plugins",
            "--disable",
            "remote_plugin",
            "--disable",
            "shell_tool",
            "--disable",
            "skill_search",
            "--disable",
            "unified_exec",
            "--disable",
            "workspace_dependencies",
            "-m",
            protocol.MODEL,
            "-c",
            f"model_reasoning_effort={protocol.REASONING_EFFORT}",
            "-s",
            "read-only",
            "-C",
            str(temp),
            "-o",
            str(last_message),
            protocol.EXACT_PROMPT,
        ]
        completed = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=False,
        )
        attempt_dir = prediction_dir / "attempts"
        if completed.returncode != 0 or not last_message.exists():
            attempt_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
            (attempt_dir / f"{stamp}.stdout.jsonl").write_text(
                completed.stdout, encoding="utf-8"
            )
            (attempt_dir / f"{stamp}.stderr.txt").write_text(
                completed.stderr, encoding="utf-8"
            )
            raise RuntimeError(f"{prediction_id}: Codex exited {completed.returncode}")

        response = last_message.read_bytes()
        if not response:
            raise RuntimeError(f"{prediction_id}: empty final response")
        thread_id, usage, disallowed = parse_events(completed.stdout)
        if disallowed:
            attempt_dir.mkdir(parents=True, exist_ok=True)
            (attempt_dir / "rejected-tool-use.jsonl").write_text(
                completed.stdout, encoding="utf-8"
            )
            raise RuntimeError(
                f"{prediction_id}: rejected tool activity: {', '.join(disallowed)}"
            )

        # Write the response last so its presence always means the runtime log
        # and execution record were successfully captured first.
        event_path.write_text(completed.stdout, encoding="utf-8")
        (prediction_dir / "stderr.txt").write_text(completed.stderr, encoding="utf-8")
        execution_path.write_text(
            encode(
                {
                    "schema_version": 1,
                    "provider": "openai",
                    "interface": "codex-cli-0.159.0",
                    "requested_model": protocol.MODEL,
                    "reasoning_effort": protocol.REASONING_EFFORT,
                    "prediction_id": prediction_id,
                    "thread_id": thread_id,
                    "ephemeral": True,
                    "working_directory": "fresh empty temporary directory",
                    "user_messages": [protocol.EXACT_PROMPT],
                    "tool_calls_observed": [],
                    "completed_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                    "usage": usage,
                }
            ),
            encoding="utf-8",
        )
        response_path.write_bytes(response)
    return f"OK {prediction_id}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prediction_ids", nargs="*", choices=protocol.PREDICTION_IDS)
    parser.add_argument("--jobs", type=int, default=3)
    parser.add_argument("--codex", type=Path, default=DEFAULT_CODEX)
    args = parser.parse_args()
    ids = args.prediction_ids or list(protocol.PREDICTION_IDS)
    if not args.codex.is_file():
        raise SystemExit(f"ERROR: Codex executable not found: {args.codex}")
    if not 1 <= args.jobs <= 8:
        raise SystemExit("ERROR: --jobs must be between 1 and 8")

    failures = []
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(run_one, item, args.codex): item for item in ids}
        for future in as_completed(futures):
            prediction_id = futures[future]
            try:
                print(future.result(), flush=True)
            except Exception as exc:  # keep independent requests running
                failures.append(prediction_id)
                print(f"FAIL {prediction_id}: {exc}", flush=True)
    if failures:
        raise SystemExit(f"ERROR: failed predictions: {', '.join(sorted(failures))}")


if __name__ == "__main__":
    main()
