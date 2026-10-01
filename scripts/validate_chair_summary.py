"""Validate round-1 chair summaries for physics committee runs."""

from __future__ import annotations

import argparse
from pathlib import Path

from validate_committee_opening import EXPECTED_MEMBERS, load_json, nonempty_text


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def text_list(value: object, label: str, minimum: int = 0) -> list[str]:
    if (
        not isinstance(value, list)
        or len(value) < minimum
        or not all(isinstance(item, str) and item.strip() for item in value)
    ):
        fail(f"{label} must contain at least {minimum} non-empty strings")
    return value


def validate(run_dir: Path) -> None:
    shortlist_doc = load_json(run_dir / "committee" / "shortlist.json")
    shortlisted = {item["ballot_id"] for item in shortlist_doc["shortlist"]}
    preferences = {}
    for member in EXPECTED_MEMBERS:
        statement = load_json(run_dir / "committee" / "round1" / f"{member}.json")
        preferences[member] = {
            part["ballot_id"]
            for part in statement["preferred_configuration"]["prize_parts"]
        }
    path = run_dir / "committee" / "chair_summary_round1.json"
    value = load_json(path)
    expected_top = {
        "schema_version", "list_id", "run", "chair_id", "model",
        "reasoning_effort", "prompt", "summary",
    }
    if set(value) != expected_top:
        fail(f"top-level schema differs: {path}")
    run = int(run_dir.name.removeprefix("run-"))
    if (
        type(value["schema_version"]) is not int or value["schema_version"] != 1
        or value["list_id"] != run_dir.parent.name
        or type(value["run"]) is not int or value["run"] != run
        or value["chair_id"] != "pearce-mark"
        or value["model"] != "gpt-6.1-sol"
        or value["reasoning_effort"] != "high"
        or value["prompt"] != "prompts/physics_committee_chair_summary_v1.md"
    ):
        fail(f"metadata differs: {path}")
    summary = value["summary"]
    expected_summary = {
        "leading_positions", "areas_of_agreement", "scientific_disputes",
        "attribution_disputes", "maturity_disputes", "conflict_or_recusal_flags",
        "questions_for_round2", "chair_observation",
    }
    if not isinstance(summary, dict) or set(summary) != expected_summary:
        fail(f"summary schema differs: {path}")
    positions = summary["leading_positions"]
    if not isinstance(positions, list) or not positions:
        fail(f"at least one leading position required: {path}")
    for position in positions:
        if not isinstance(position, dict) or set(position) != {"ballot_ids", "explicit_supporters", "synthesis"}:
            fail(f"leading-position schema differs: {path}")
        ids = text_list(position["ballot_ids"], f"{path}:ballot_ids", 1)
        supporters = text_list(position["explicit_supporters"], f"{path}:supporters", 1)
        if len(ids) != len(set(ids)) or not set(ids) <= shortlisted:
            fail(f"invalid leading ballot IDs: {path}")
        if len(supporters) != len(set(supporters)) or not set(supporters) <= EXPECTED_MEMBERS:
            fail(f"invalid leading supporters: {path}")
        for supporter in supporters:
            if not set(ids) <= preferences[supporter]:
                fail(f"{supporter} did not explicitly prefer all {ids}: {path}")
        nonempty_text(position["synthesis"], f"{path}:synthesis")
    text_list(summary["areas_of_agreement"], f"{path}:areas_of_agreement", 1)
    for key in ("scientific_disputes", "attribution_disputes", "maturity_disputes", "conflict_or_recusal_flags"):
        text_list(summary[key], f"{path}:{key}")
    text_list(summary["questions_for_round2"], f"{path}:questions_for_round2", 2)
    nonempty_text(summary["chair_observation"], f"{path}:chair_observation")
    print(f"OK: {run_dir}: validated chair round-1 summary")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dirs", nargs="+", type=Path)
    args = parser.parse_args()
    for run_dir in args.run_dirs:
        validate(run_dir)


if __name__ == "__main__":
    main()
