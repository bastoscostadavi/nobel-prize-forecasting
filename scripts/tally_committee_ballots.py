"""Validate and tally exhaustive final committee ballots by instant runoff."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from build_committee_proposals import build as build_proposals
from validate_committee_opening import EXPECTED_MEMBERS, load_json, nonempty_text


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def encode(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def load_ballots(run_dir: Path, slate: dict) -> dict[str, list[str]]:
    proposal_ids = [item["proposal_id"] for item in slate["proposals"]]
    expected = set(proposal_ids)
    directory = run_dir / "committee" / "final_ballots"
    files = sorted(directory.glob("*.json"))
    members = {path.stem for path in files}
    if members != EXPECTED_MEMBERS:
        fail(f"final-ballot members differ: missing={sorted(EXPECTED_MEMBERS-members)}, extra={sorted(members-EXPECTED_MEMBERS)}")
    ballots = {}
    run = int(run_dir.name.removeprefix("run-"))
    for path in files:
        value = load_json(path)
        if set(value) != {
            "schema_version", "list_id", "run", "member_id", "model",
            "reasoning_effort", "prompt", "ranked_proposal_ids",
            "top_choice_rationale", "recusal_note",
        }:
            fail(f"final-ballot schema differs: {path}")
        if (
            type(value["schema_version"]) is not int or value["schema_version"] != 1
            or value["list_id"] != run_dir.parent.name
            or type(value["run"]) is not int or value["run"] != run
            or value["member_id"] != path.stem
            or value["model"] != "gpt-6.1-sol"
            or value["reasoning_effort"] != "high"
            or value["prompt"] != "prompts/physics_committee_final_ballot_v1.md"
        ):
            fail(f"final-ballot metadata differs: {path}")
        ranking = value["ranked_proposal_ids"]
        if (
            not isinstance(ranking, list)
            or not all(isinstance(item, str) for item in ranking)
            or len(ranking) != len(expected)
            or len(ranking) != len(set(ranking))
            or set(ranking) != expected
        ):
            fail(f"ranking is not an exhaustive proposal permutation: {path}")
        nonempty_text(value["top_choice_rationale"], f"{path}:top_choice_rationale")
        nonempty_text(value["recusal_note"], f"{path}:recusal_note")
        ballots[path.stem] = ranking
    return ballots


def tally(run_dir: Path) -> dict:
    slate_path = run_dir / "committee" / "proposal_slate.json"
    saved_slate = load_json(slate_path)
    expected_slate = build_proposals(run_dir)
    if slate_path.read_bytes() != encode(expected_slate).encode("utf-8"):
        fail(f"proposal slate differs from deterministic round-2 positions: {run_dir}")
    ballots = load_ballots(run_dir, saved_slate)
    proposals = {item["proposal_id"]: item for item in saved_slate["proposals"]}
    active = set(proposals)
    majority = len(ballots) // 2 + 1
    borda = {
        proposal_id: sum(len(active) - ranking.index(proposal_id) for ranking in ballots.values())
        for proposal_id in active
    }
    supporter_counts = {
        proposal_id: len(proposals[proposal_id]["explicit_supporters"])
        for proposal_id in active
    }
    rounds = []
    winner = None
    while active:
        choices = {
            member: next(proposal_id for proposal_id in ranking if proposal_id in active)
            for member, ranking in ballots.items()
        }
        counts = Counter(choices.values())
        count_table = {proposal_id: counts.get(proposal_id, 0) for proposal_id in sorted(active)}
        leaders = [proposal_id for proposal_id, count in count_table.items() if count >= majority]
        if leaders:
            winner = sorted(leaders, key=lambda item: (-count_table[item], item))[0]
            rounds.append({"round": len(rounds) + 1, "counts": count_table, "eliminated": None})
            break
        if len(active) == 1:
            winner = next(iter(active))
            rounds.append({"round": len(rounds) + 1, "counts": count_table, "eliminated": None})
            break
        minimum = min(count_table.values())
        tied = [item for item, count in count_table.items() if count == minimum]
        eliminated = sorted(
            tied,
            key=lambda item: (supporter_counts[item], borda[item], item),
        )[0]
        rounds.append(
            {
                "round": len(rounds) + 1,
                "counts": count_table,
                "eliminated": eliminated,
                "elimination_tie_break": {
                    "fewest_current_votes": minimum,
                    "round2_explicit_supporters": supporter_counts[eliminated],
                    "full_ballot_borda": borda[eliminated],
                    "final_tie_break": "proposal_id ascending",
                },
            }
        )
        active.remove(eliminated)
    assert winner is not None

    ballot_map = load_json(run_dir / "committee" / "ballot_map.json")["ballot_to_candidate"]
    longlist = {
        item["ballot_id"]: item
        for item in load_json(run_dir / "committee" / "longlist.json")["candidates"]
    }
    winning = proposals[winner]
    decoded_parts = []
    for part in winning["prize_parts"]:
        public = longlist[part["ballot_id"]]
        decoded_parts.append(
            {
                "ballot_id": part["ballot_id"],
                "candidate_id": ballot_map[part["ballot_id"]],
                "discovery": public["discovery"],
                "laureates": part["laureates"],
            }
        )
    return {
        "schema_version": 1,
        "list_id": run_dir.parent.name,
        "run": int(run_dir.name.removeprefix("run-")),
        "rule": {
            "method": "instant runoff over exhaustive rankings",
            "majority_votes": majority,
            "elimination_order": [
                "fewest current first-active preferences",
                "fewest explicit round-2 supporters",
                "lowest full-ballot Borda score",
                "proposal_id ascending",
            ],
            "recusals": "disclosed but not adjudicated in this simulation",
        },
        "rounds": rounds,
        "winner": {
            "proposal_id": winner,
            "no_award": winner == "P000",
            "prize_parts": decoded_parts,
        },
    }


def process(run_dir: Path, check: bool) -> None:
    value = tally(run_dir)
    path = run_dir / "committee" / "decision.json"
    expected = encode(value)
    if check:
        if path.read_text(encoding="utf-8") != expected:
            fail(f"{path} differs from deterministic tally")
        action = "checked"
    else:
        path.write_text(expected, encoding="utf-8")
        action = "wrote"
    print(f"OK: {run_dir}: {action} winner {value['winner']['proposal_id']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dirs", nargs="+", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for run_dir in args.run_dirs:
        process(run_dir, args.check)


if __name__ == "__main__":
    main()
