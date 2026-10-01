"""Validate private opening rankings for one physics committee run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from prepare_committee_longlist import DEFAULT_SEED_LABEL, prepare
from validate_candidate_merge import check_csv, validate as validate_merge


EXPECTED_MEMBERS = {
    "danielsson-ulf",
    "eriksson-olle",
    "johansson-goran",
    "kroll-stefan",
    "lindroth-eva",
    "mehlig-bernhard",
    "olsson-eva",
    "pearce-mark",
}
EXPECTED_MODEL = "gpt-6.1-sol"
EXPECTED_EFFORT = "high"
EXPECTED_PROMPT = "prompts/physics_committee_opening_v1.md"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read valid JSON from {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"top level must be an object: {path}")
    return value


def nonempty_text(value: object, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be a non-empty string")


def validate(run_dir: Path) -> None:
    longlist = load_json(run_dir / "committee" / "longlist.json")
    if (
        set(longlist) != {"schema_version", "candidates"}
        or type(longlist["schema_version"]) is not int
        or longlist["schema_version"] != 1
    ):
        fail("longlist schema differs from version 1")
    candidates = longlist["candidates"]
    if not isinstance(candidates, list):
        fail("longlist candidates must be an array")
    by_id = {}
    for candidate in candidates:
        if not isinstance(candidate, dict) or set(candidate) != {
            "ballot_id", "discovery", "subfield", "credited_names"
        }:
            fail("longlist candidate schema differs from version 1")
        ballot_id = candidate["ballot_id"]
        nonempty_text(ballot_id, "longlist ballot_id")
        if ballot_id in by_id:
            fail(f"duplicate longlist ballot ID: {ballot_id}")
        nonempty_text(candidate["discovery"], f"{ballot_id}:discovery")
        nonempty_text(candidate["subfield"], f"{ballot_id}:subfield")
        names = candidate["credited_names"]
        if (
            not isinstance(names, list)
            or not names
            or not all(isinstance(name, str) and name.strip() for name in names)
            or len(names) != len(set(names))
            or names != sorted(names, key=lambda name: (name.casefold(), name))
        ):
            fail(f"{ballot_id}: credited_names must be unique, nonempty and alphabetized")
        by_id[ballot_id] = candidate

    expected_ballot_ids = [f"B{i:03d}" for i in range(1, len(candidates) + 1)]
    if list(by_id) != expected_ballot_ids:
        fail("longlist ballot IDs must be consecutive in array order")

    merged, rows = validate_merge(run_dir)
    check_csv(run_dir, rows)
    expected_longlist, expected_map = prepare(merged, DEFAULT_SEED_LABEL)
    if longlist != expected_longlist:
        fail("longlist does not match the deterministic validated consolidation")
    if load_json(run_dir / "committee" / "ballot_map.json") != expected_map:
        fail("ballot_map does not match the deterministic validated consolidation")

    list_id = run_dir.parent.name
    try:
        run = int(run_dir.name.removeprefix("run-"))
    except ValueError:
        fail(f"run directory must be named run-N: {run_dir}")
    opening_dir = run_dir / "committee" / "opening"
    files = sorted(opening_dir.glob("*.json"))
    found_members = {path.stem for path in files}
    if found_members != EXPECTED_MEMBERS:
        fail(
            f"opening members differ: missing={sorted(EXPECTED_MEMBERS - found_members)}, "
            f"extra={sorted(found_members - EXPECTED_MEMBERS)}"
        )

    for path in files:
        value = load_json(path)
        if set(value) != {
            "schema_version", "list_id", "run", "member_id", "model",
            "reasoning_effort", "prompt", "rankings"
        }:
            fail(f"top-level schema differs: {path}")
        if type(value["schema_version"]) is not int or value["schema_version"] != 1:
            fail(f"schema_version must be 1: {path}")
        if (
            value["list_id"] != list_id
            or type(value["run"]) is not int
            or value["run"] != run
        ):
            fail(f"list_id/run do not match path: {path}")
        if value["member_id"] != path.stem:
            fail(f"member_id does not match filename: {path}")
        if value["model"] != EXPECTED_MODEL or value["reasoning_effort"] != EXPECTED_EFFORT:
            fail(f"model metadata differs: {path}")
        if value["prompt"] != EXPECTED_PROMPT:
            fail(f"prompt metadata differs: {path}")
        rankings = value["rankings"]
        if not isinstance(rankings, list) or len(rankings) != 8:
            fail(f"rankings must contain exactly eight entries: {path}")
        seen = set()
        for rank, entry in enumerate(rankings, start=1):
            if not isinstance(entry, dict) or set(entry) != {
                "rank", "ballot_id", "proposed_laureates", "assessment"
            }:
                fail(f"ranking schema differs at rank {rank}: {path}")
            if type(entry["rank"]) is not int or entry["rank"] != rank:
                fail(f"rankings must be consecutive in array order: {path}")
            ballot_id = entry["ballot_id"]
            if ballot_id not in by_id or ballot_id in seen:
                fail(f"invalid or repeated ballot ID {ballot_id!r}: {path}")
            seen.add(ballot_id)
            laureates = entry["proposed_laureates"]
            credited = set(by_id[ballot_id]["credited_names"])
            if (
                not isinstance(laureates, list)
                or not 1 <= len(laureates) <= 3
                or len(set(laureates)) != len(laureates)
                or not all(isinstance(name, str) and name in credited for name in laureates)
            ):
                fail(f"invalid proposed laureates for {ballot_id}: {path}")
            assessment = entry["assessment"]
            if not isinstance(assessment, dict) or set(assessment) != {
                "nobel_worthiness", "attribution", "maturity", "uncertainties"
            }:
                fail(f"assessment schema differs for {ballot_id}: {path}")
            for key in ("nobel_worthiness", "attribution", "maturity"):
                nonempty_text(assessment[key], f"{path}:{ballot_id}:{key}")
            uncertainties = assessment["uncertainties"]
            if not isinstance(uncertainties, list) or not all(
                isinstance(item, str) and item.strip() for item in uncertainties
            ):
                fail(f"uncertainties must be an array of non-empty strings: {path}")
    print(f"OK: {run_dir}: {len(files)} members x 8 private opening rankings")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dirs", nargs="+", type=Path)
    args = parser.parse_args()
    for run_dir in args.run_dirs:
        validate(run_dir)


if __name__ == "__main__":
    main()
