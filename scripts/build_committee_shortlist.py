"""Build a deterministic union shortlist from validated private rankings."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_committee_opening import EXPECTED_MEMBERS, load_json, validate


MINIMUM_SHORTLIST = 8
RULE_ID = "opening-union-v1"


def encode_json(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def build(run_dir: Path) -> dict:
    validate(run_dir)
    longlist = load_json(run_dir / "committee" / "longlist.json")
    candidates = {item["ballot_id"]: item for item in longlist["candidates"]}
    support = {
        ballot_id: {
            "member_rankings": [],
            "laureate_proposals": [],
            "borda_points": 0,
        }
        for ballot_id in candidates
    }
    opening_dir = run_dir / "committee" / "opening"
    for member_id in sorted(EXPECTED_MEMBERS):
        ballot = load_json(opening_dir / f"{member_id}.json")
        for entry in ballot["rankings"]:
            item = support[entry["ballot_id"]]
            item["member_rankings"].append(
                {"member_id": member_id, "rank": entry["rank"]}
            )
            item["laureate_proposals"].append(
                {
                    "member_id": member_id,
                    "proposed_laureates": entry["proposed_laureates"],
                }
            )
            item["borda_points"] += 9 - entry["rank"]

    def metrics(ballot_id: str) -> tuple[int, int, int, int, int]:
        rankings = support[ballot_id]["member_rankings"]
        first = sum(item["rank"] == 1 for item in rankings)
        top_three = sum(item["rank"] <= 3 for item in rankings)
        ranked = len(rankings)
        best = min((item["rank"] for item in rankings), default=99)
        points = support[ballot_id]["borda_points"]
        return first, top_three, ranked, points, best

    selected = {
        ballot_id
        for ballot_id in candidates
        if (
            metrics(ballot_id)[0] >= 1
            or metrics(ballot_id)[1] >= 2
            or metrics(ballot_id)[2] >= 3
        )
    }
    priority = sorted(
        candidates,
        key=lambda ballot_id: (
            -metrics(ballot_id)[0],
            -metrics(ballot_id)[1],
            -metrics(ballot_id)[2],
            -metrics(ballot_id)[3],
            metrics(ballot_id)[4],
            ballot_id,
        ),
    )
    for ballot_id in priority:
        if len(selected) >= MINIMUM_SHORTLIST:
            break
        selected.add(ballot_id)

    shortlist = []
    for ballot_id in priority:
        if ballot_id not in selected:
            continue
        first, top_three, ranked, points, best = metrics(ballot_id)
        public = candidates[ballot_id]
        member_rankings = sorted(
            support[ballot_id]["member_rankings"],
            key=lambda item: (item["rank"], item["member_id"]),
        )
        proposals = sorted(
            support[ballot_id]["laureate_proposals"],
            key=lambda item: item["member_id"],
        )
        shortlist.append(
            {
                **public,
                "opening_support": {
                    "first_place": first,
                    "top_three": top_three,
                    "ranked": ranked,
                    "borda_points": points,
                    "best_rank": best,
                    "member_rankings": member_rankings,
                    "laureate_proposals": proposals,
                },
            }
        )
    list_id = run_dir.parent.name
    run = int(run_dir.name.removeprefix("run-"))
    return {
        "schema_version": 1,
        "list_id": list_id,
        "run": run,
        "selection_rule": {
            "id": RULE_ID,
            "automatic": [
                "at least one first-place ranking",
                "at least two top-three rankings",
                "ranked in the top eight by at least three members",
            ],
            "minimum_candidates": MINIMUM_SHORTLIST,
            "fill_order": [
                "first_place descending",
                "top_three descending",
                "ranked descending",
                "borda_points descending (8 points for rank 1 through 1 for rank 8)",
                "best_rank ascending",
                "ballot_id ascending",
            ],
        },
        "shortlist": shortlist,
    }


def process(run_dir: Path, check: bool) -> None:
    value = build(run_dir)
    path = run_dir / "committee" / "shortlist.json"
    expected = encode_json(value)
    if check:
        if path.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"ERROR: {path} differs from deterministic shortlist")
        action = "checked"
    else:
        path.write_text(expected, encoding="utf-8")
        action = "wrote"
    print(f"OK: {run_dir}: {action} {len(value['shortlist'])} shortlisted candidates")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dirs", nargs="+", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for run_dir in args.run_dirs:
        process(run_dir, args.check)


if __name__ == "__main__":
    main()
