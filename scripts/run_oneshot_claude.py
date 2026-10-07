#!/usr/bin/env python3
"""Run independent zero-context Claude Opus 5.5 one-shot predictions (resumable).

Usage:
  python3 scripts/run_oneshot_claude.py peace --n 50
  python3 scripts/run_oneshot_claude.py literature --n 25
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

# Each category: prompt doc, exact user prompt, output keys, laureate key and allowed count.
CATEGORIES = {
    "peace": {
        "prompt_file": "prompts/peace_oneshot_claude_v1.md",
        "user_prompt": (ROOT / "prompts/peace_oneshot_gpt_6_1_sol_v1.txt").read_text().strip(),
        "system_prompt": ('Answer with only a JSON object with exactly these keys: "achievement" (string), '
                          '"laureates" (array of one to three individual and/or organization names), '
                          '"rationale" (string, concise).'),
        "keys": ("achievement", "laureates", "rationale"),
        "names_key": "laureates", "max_names": 3,
    },
    "literature": {
        "prompt_file": "prompts/literature_oneshot_claude_v1.md",
        "user_prompt": ("Who will win the 2026 Nobel Prize in Literature? Predict the laureate and the "
                        "literary achievement. Answer from your own knowledge only; do not search the web "
                        "or read any files."),
        "system_prompt": ('Answer with only a JSON object with exactly these keys: "laureate" (string, one '
                          'writer\'s name), "achievement" (string), "rationale" (string, concise).'),
        "keys": ("achievement", "laureate", "rationale"),
        "names_key": None, "max_names": 1,
    },
}


def command(claude: str, system_prompt: str) -> list[str]:
    return [claude, "--print", "--model", MODEL, "--effort", EFFORT,
            "--tools", "", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
            "--disable-slash-commands", "--safe-mode", "--no-session-persistence",
            "--output-format", "stream-json", "--verbose", "--permission-mode", "dontAsk",
            "--setting-sources", "", "--no-chrome", "--system-prompt", system_prompt]


def parse(stdout: str) -> dict:
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
    return json.loads(text)


def validate(value: dict, spec: dict) -> None:
    if set(value) != set(spec["keys"]):
        raise RuntimeError(f"keys differ: {sorted(value)}")
    if spec["names_key"]:
        names = value[spec["names_key"]]
        if not isinstance(names, list) or not 1 <= len(names) <= spec["max_names"] \
                or len(set(names)) != len(names) or not all(isinstance(n, str) and n.strip() for n in names):
            raise RuntimeError(f"{spec['names_key']} must be one to {spec['max_names']} distinct names")
    for key in spec["keys"]:
        if key != spec["names_key"] and (not isinstance(value[key], str) or not value[key].strip()):
            raise RuntimeError(f"{key} must be non-empty text")


def run_one(n: int, spec: dict, out: Path, claude: str, max_attempts: int) -> str:
    pid = f"pred-{n:02d}"
    path = out / f"{pid}.json"
    if path.exists():
        return f"SKIP {pid}"
    errors = []
    for attempt in range(1, max_attempts + 1):
        with tempfile.TemporaryDirectory(prefix=f"oneshot-{pid}-") as tmp:
            done = subprocess.run(command(claude, spec["system_prompt"]), input=spec["user_prompt"],
                                  capture_output=True, text=True, cwd=tmp, timeout=1800)
        (out / "runtime" / f"{pid}-attempt-{attempt}.jsonl").write_text(done.stdout)
        try:
            if done.returncode != 0:
                raise RuntimeError(f"exit {done.returncode}: {done.stderr.strip()[:300]}")
            value = parse(done.stdout)
            validate(value, spec)
        except Exception as exc:  # recorded and retried
            errors.append(f"attempt {attempt}: {exc}")
            continue
        record = {"schema_version": 1, "prediction_id": pid, "model": MODEL, "reasoning_effort": EFFORT,
                  "prompt": spec["prompt_file"], **{k: value[k] for k in spec["keys"]}}
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
        names = value[spec["names_key"]] if spec["names_key"] else [value["laureate"]]
        return f"OK {pid}: {value['achievement'][:70]} - {'; '.join(names)}"
    return f"FAIL {pid}: {' | '.join(errors)}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("category", choices=sorted(CATEGORIES))
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--jobs", type=int, default=5)
    parser.add_argument("--max-attempts", type=int, default=3)
    args = parser.parse_args()
    spec = CATEGORIES[args.category]
    out = ROOT / "results" / args.category / "oneshot" / MODEL
    claude = shutil.which("claude") or str(Path.home() / ".local/bin/claude")
    (out / "runtime").mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(args.jobs) as pool:
        for line in pool.map(lambda n: run_one(n, spec, out, claude, args.max_attempts), range(1, args.n + 1)):
            print(line, flush=True)


if __name__ == "__main__":
    main()
