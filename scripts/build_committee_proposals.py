"""Build a deterministic final proposal slate from round-2 positions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_committee_opening import EXPECTED_MEMBERS, load_json
from validate_committee_round import validate as validate_round


def encode(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def canonical_parts(parts: list[dict]) -> list[dict]:
    return sorted(
        (
            {
                "ballot_id": part["ballot_id"],
                "laureates": sorted(part["laureates"], key=lambda name: (name.casefold(), name)),
            }
            for part in parts
        ),
        key=lambda part: (part["ballot_id"], part["laureates"]),
    )


def build(run_dir: Path) -> dict:
    validate_round(run_dir, 2)
    grouped: dict[str, dict] = {}
    directory = run_dir / "committee" / "round2"
    for member in sorted(EXPECTED_MEMBERS):
        value = load_json(directory / f"{member}.json")
        raw_parts = value["preferred_configuration"]["prize_parts"]
        parts = canonical_parts(raw_parts)
        key = json.dumps(parts, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        record = grouped.setdefault(
            key,
            {"prize_parts": parts, "explicit_supporters": [], "member_citations": []},
        )
        record["explicit_supporters"].append(member)
        record["member_citations"].append(
            {
                "member_id": member,
                "citations": [
                    {"ballot_id": part["ballot_id"], "citation": part["citation"]}
                    for part in raw_parts
                ],
            }
        )
    proposals = [
        {
            "proposal_id": "P000",
            "prize_parts": [],
            "explicit_supporters": [],
            "member_citations": [],
            "meaning": "No award in this run",
        }
    ]
    ordered = sorted(
        grouped.items(),
        key=lambda item: (-len(item[1]["explicit_supporters"]), item[0]),
    )
    for index, (_, record) in enumerate(ordered, start=1):
        proposals.append(
            {
                "proposal_id": f"P{index:03d}",
                **record,
                "meaning": "Award the listed prize part or parts",
            }
        )
    return {
        "schema_version": 1,
        "list_id": run_dir.parent.name,
        "run": int(run_dir.name.removeprefix("run-")),
        "source": "committee/round2/*.json",
        "proposals": proposals,
    }


def process(run_dir: Path, check: bool) -> None:
    value = build(run_dir)
    path = run_dir / "committee" / "proposal_slate.json"
    expected = encode(value)
    if check:
        if path.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"ERROR: {path} differs from deterministic proposal slate")
        action = "checked"
    else:
        ballot_dir = run_dir / "committee" / "final_ballots"
        if ballot_dir.exists() and any(ballot_dir.glob("*.json")):
            raise SystemExit(f"ERROR: refusing to replace dispatched slate with ballots in {ballot_dir}")
        path.write_text(expected, encoding="utf-8")
        action = "wrote"
    print(f"OK: {run_dir}: {action} {len(value['proposals'])} final proposals")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dirs", nargs="+", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for run_dir in args.run_dirs:
        process(run_dir, args.check)


if __name__ == "__main__":
    main()
