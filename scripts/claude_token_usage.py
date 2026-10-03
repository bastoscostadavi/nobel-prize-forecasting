"""Sum Claude Code token usage for this project's Claude sessions, by experiment stage.

Reads the session transcripts Claude Code stores under
~/.claude/projects/<project>/<session-id>.jsonl and <session-id>/subagents/,
de-duplicates API responses by message ID, and writes
results/physics/claude_token_usage.json.

Usage: python3 scripts/claude_token_usage.py SESSION_DIR [SESSION_DIR ...]
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "physics" / "claude_token_usage.json"

# Workflow run IDs launched in session 221175dc-bcf6-445f-abd0-d9974d942539.
WORKFLOW_STAGE = {
    "wf_f689ea72-f48": "nominations", "wf_7a50aa19-ab0": "nominations",
    "wf_4e4e9778-2ef": "nominations", "wf_d1a29ddf-e65": "nominations",
    "wf_2bd0ca70-13d": "nominations", "wf_4ae2776f-635": "nominations",
    "wf_4a5678a6-858": "nominations", "wf_6adc25a4-ea0": "nominations",
    "wf_7b665e95-398": "oneshot_opus",
    "wf_ffcd39ce-501": "committee_sonnet_profile_v2", "wf_be724cd4-fe8": "committee_sonnet_profile_v2",
    "wf_7de5ac51-021": "committee_sonnet_profile_v2", "wf_f5a7b59c-13b": "committee_sonnet_profile_v2",
    "wf_ae2efab9-626": "committee_sonnet_profile_v2", "wf_b7fc70dd-e8d": "committee_sonnet_profile_v2",
    "wf_8a48f6bf-5e5": "medicine_committee_sonnet", "wf_118e0828-423": "medicine_committee_sonnet",
    "wf_1bcd8c75-3ca": "medicine_oneshot_opus",
}
FIELDS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")


def usage_of(path: Path) -> tuple[dict[str, int], dict[str, int]]:
    """Return (token totals, per-model total tokens) for one transcript, one count per message ID."""
    seen: dict[str, tuple[str, dict]] = {}
    for line in path.read_text(errors="ignore").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        message = record.get("message") if isinstance(record, dict) else None
        if not isinstance(message, dict) or "usage" not in message:
            continue
        key = message.get("id") or record.get("uuid")
        seen[key] = (message.get("model", "unknown"), message["usage"])  # last record holds final usage
    totals = {f: 0 for f in FIELDS}
    models: dict[str, int] = defaultdict(int)
    for model, usage in seen.values():
        for f in FIELDS:
            totals[f] += usage.get(f) or 0
        models[model] += sum(usage.get(f) or 0 for f in FIELDS)
    return totals, models


def stage_of(path: Path, session_dir: Path) -> str:
    if session_dir not in path.parents:
        return "main_session"
    parts = path.relative_to(session_dir).parts
    if len(parts) > 2 and parts[1] == "workflows":
        return WORKFLOW_STAGE.get(parts[2], "committee_sonnet_profile_v1")
    return "profiles_and_setup_subagents"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("session_dirs", nargs="+", type=Path)
    args = parser.parse_args()
    stages: dict[str, dict] = defaultdict(lambda: {"agents": 0, **{f: 0 for f in FIELDS}, "models": defaultdict(int)})
    for session_dir in args.session_dirs:
        files = [session_dir.with_suffix(".jsonl")] + sorted(session_dir.glob("subagents/**/agent-*.jsonl"))
        for path in files:
            if not path.exists():
                continue
            totals, models = usage_of(path)
            stage = stages[stage_of(path, session_dir)]
            stage["agents"] += path.name.startswith("agent-")
            for f in FIELDS:
                stage[f] += totals[f]
            for model, n in models.items():
                stage["models"][model] += n
    report = {}
    for name, s in sorted(stages.items()):
        s["models"] = dict(sorted(s["models"].items()))
        s["total_tokens"] = sum(s[f] for f in FIELDS)
        report[name] = s
    grand = {f: sum(s[f] for s in report.values()) for f in FIELDS}
    grand["total_tokens"] = sum(grand.values())
    OUT.write_text(json.dumps({
        "schema_version": 1,
        "note": "Claude Code token usage, de-duplicated by API message ID. Includes the main Opus 5.5 session and all subagents.",
        "sessions": [d.name for d in args.session_dirs],
        "stages": report,
        "total": grand,
    }, indent=2) + "\n")
    for name, s in report.items():
        print(f"{name:32s} agents={s['agents']:5d} total={s['total_tokens']:>14,d} output={s['output_tokens']:>11,d}")
    print(f"{'TOTAL':32s} {'':12s}total={grand['total_tokens']:>14,d} output={grand['output_tokens']:>11,d}")


if __name__ == "__main__":
    main()
