#!/usr/bin/env python3
"""Run 50 independent zero-context Claude Opus 5.5 Peace predictions (resumable).

Usage: python3 scripts/run_peace_oneshot_claude.py [--n 50] [--jobs 5] [--max-attempts 3]
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = "claude-opus-5-5"
EFFORT = "high"
PROMPT_FILE = "prompts/peace_oneshot_claude_v1.md"
OUT = ROOT / "results/peace/oneshot" / MODEL
USER_PROMPT = (ROOT / "prompts/peace_oneshot_gpt_6_1_sol_v1.txt").read_text().strip()
SYSTEM_PROMPT = ('Answer with only a JSON object with exactly these keys: "achievement" (string), '
                 '"laureates" (array of one to three individual and/or organization names), '
                 '"rationale" (string, concise).')


def command(claude: str) -> list[str]:
    return [claude, "--print", "--model", MODEL, "--effort", EFFORT,
            "--tools", "", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
            "--disable-slash-commands", "--safe-mode", "--no-session-persistence",
            "--output-format", "stream-json", "--verbose", "--permission-mode", "dontAsk",
            "--setting-sources", "", "--no-chrome", "--system-prompt", SYSTEM_PROMPT]


def parse(stdout: str) -> tuple[dict, set[str]]:
    models, result = set(), None
    for line in stdout.splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        if event.get("type") == "system" and event.get("subtype") == "init":
            if event.get("tools") or event.get("mcp_servers"):
                raise RuntimeError("tools or MCP servers were available")
            models.add(event.get("model"))
        if event.get("type") == "assistant":
            models.add(event.get("message", {}).get("model"))
            if any(b.get("type") in ("tool_use", "server_tool_use") for b in event["message"].get("content", [])):
                raise RuntimeError("tool use detected")
        if event.get("type") == "result":
            result = event
    if not result or result.get("subtype") != "success" or result.get("is_error"):
        raise RuntimeError(f"no successful result: {str(result)[:300]}")
    models.discard(None)
    if models != {MODEL}:
        raise RuntimeError(f"model drift: {sorted(models)}")
    text = result["result"].strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    value = json.loads(text)
    return value, models


def validate(value: dict) -> None:
    if set(value) != {"achievement", "laureates", "rationale"}:
        raise RuntimeError(f"keys differ: {sorted(value)}")
    names = value["laureates"]
    if not isinstance(names, list) or not 1 <= len(names) <= 3 or len(set(names)) != len(names) \
            or not all(isinstance(n, str) and n.strip() for n in names):
        raise RuntimeError("laureates must be one to three distinct names")
    for key in ("achievement", "rationale"):
        if not isinstance(value[key], str) or not value[key].strip():
            raise RuntimeError(f"{key} must be non-empty text")


def run_one(n: int, claude: str, max_attempts: int) -> str:
    pid = f"pred-{n:02d}"
    path = OUT / f"{pid}.json"
    if path.exists():
        return f"SKIP {pid}"
    errors = []
    for attempt in range(1, max_attempts + 1):
        with tempfile.TemporaryDirectory(prefix=f"peace-oneshot-{pid}-") as tmp:
            done = subprocess.run(command(claude), input=USER_PROMPT, capture_output=True, text=True,
                                  cwd=tmp, timeout=1800)
        (OUT / "runtime" / f"{pid}-attempt-{attempt}.jsonl").write_text(done.stdout)
        try:
            if done.returncode != 0:
                raise RuntimeError(f"exit {done.returncode}: {done.stderr.strip()[:300]}")
            value, _ = parse(done.stdout)
            validate(value)
        except Exception as exc:  # recorded and retried
            errors.append(f"attempt {attempt}: {exc}")
            continue
        record = {"schema_version": 1, "prediction_id": pid, "model": MODEL, "reasoning_effort": EFFORT,
                  "prompt": PROMPT_FILE, **value}
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
        return f"OK {pid}: {value['achievement'][:70]} - {'; '.join(value['laureates'])}"
    return f"FAIL {pid}: {' | '.join(errors)}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=50)
    parser.add_argument("--jobs", type=int, default=5)
    parser.add_argument("--max-attempts", type=int, default=3)
    args = parser.parse_args()
    claude = shutil.which("claude") or str(Path.home() / ".local/bin/claude")
    (OUT / "runtime").mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(args.jobs) as pool:
        for line in pool.map(lambda n: run_one(n, claude, args.max_attempts), range(1, args.n + 1)):
            print(line, flush=True)


if __name__ == "__main__":
    main()
