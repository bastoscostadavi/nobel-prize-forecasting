"""Write a compact run-level CSV for completed physics committee decisions."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


FIELDS = [
    "list_id", "run", "winning_proposal", "no_award", "candidate_ids",
    "discoveries", "laureates", "deciding_round", "decisive_votes",
]


def row(path: Path) -> dict[str, str | int | bool]:
    value = json.loads(path.read_text(encoding="utf-8"))
    winner = value["winner"]
    parts = winner["prize_parts"]
    final_round = value["rounds"][-1]
    return {
        "list_id": value["list_id"],
        "run": value["run"],
        "winning_proposal": winner["proposal_id"],
        "no_award": winner["no_award"],
        "candidate_ids": "; ".join(part["candidate_id"] for part in parts),
        "discoveries": " + ".join(part["discovery"] for part in parts),
        "laureates": "; ".join(
            name for part in parts for name in part["laureates"]
        ),
        "deciding_round": final_round["round"],
        "decisive_votes": final_round["counts"][winner["proposal_id"]],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("decision_files", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows = sorted((row(path) for path in args.decision_files), key=lambda item: (item["list_id"], item["run"]))
    from io import StringIO
    buffer = StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    expected = buffer.getvalue()
    if args.check:
        if args.output.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"ERROR: {args.output} differs from decisions")
        action = "checked"
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(expected, encoding="utf-8")
        action = "wrote"
    print(f"OK: {action} {len(rows)} decisions to {args.output}")


if __name__ == "__main__":
    main()
