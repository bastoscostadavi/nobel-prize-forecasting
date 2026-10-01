#!/usr/bin/env python3
"""Summarize the completed GPT-5.6 Terra Physics committee arm.

The summary is a deterministic, clerical reduction of the 60 validated
``decision.json`` records.  It never calls a model and does not inspect the
separate Claude committee or GPT-6.1 Sol one-shot arms.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "physics"
LIST_IDS = ("claude-opus-5-5", "gpt-6-sol")
MODEL = "gpt-5.6-terra"
REASONING = "high"
DISPLAY_NAME = "Terra"
ARM_ID = "physics-committee-gpt-5.6-terra-high-v1"
RUNTIME_DIRECTORY = "terra_committee_runtime"
EXPECTED_COUNT = 60
OUTPUT_JSON = RESULTS / "terra_committee_summary.json"
OUTPUT_CSV = RESULTS / "terra_committee_summary.csv"


def load_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def decision_paths() -> list[Path]:
    paths: list[Path] = []
    for list_id in LIST_IDS:
        paths.extend(
            sorted(
                (RESULTS / list_id).glob(
                    f"run-*/committee/{MODEL}/sim-*/decision.json"
                )
            )
        )
    return paths


def configuration(decision: dict) -> tuple[str, ...]:
    winner = decision["winner"]
    if winner["no_award"]:
        return ("NO AWARD",)
    names = [
        name
        for part in winner["prize_parts"]
        for name in part["laureates"]
    ]
    return tuple(sorted(names))


def build_summary() -> tuple[dict, list[dict]]:
    paths = decision_paths()
    if len(paths) != EXPECTED_COUNT:
        raise ValueError(
            f"expected {EXPECTED_COUNT} {DISPLAY_NAME} decisions, found {len(paths)}"
        )

    records: list[dict] = []
    configurations: dict[tuple[str, ...], list[str]] = defaultdict(list)
    by_list: dict[str, dict[tuple[str, ...], list[str]]] = {
        list_id: defaultdict(list) for list_id in LIST_IDS
    }
    seen: set[str] = set()

    for path in paths:
        decision = load_object(path)
        if decision.get("committee_model") != MODEL:
            raise ValueError(f"unexpected model in {path}")
        if decision.get("reasoning_effort") != REASONING:
            raise ValueError(f"unexpected reasoning effort in {path}")

        list_id = decision["list_id"]
        run = decision["run"]
        simulation_id = decision["simulation_id"]
        key = f"{list_id}/run-{run}/{simulation_id}"
        if key in seen:
            raise ValueError(f"duplicate simulation identity: {key}")
        seen.add(key)

        winner = decision["winner"]
        names = configuration(decision)
        discoveries = [part["discovery"] for part in winner["prize_parts"]]
        final_round = decision["rounds"][-1]
        winning_votes = final_round["counts"].get(winner["proposal_id"], 0)
        relative_path = path.relative_to(ROOT).as_posix()
        record = {
            "simulation_key": key,
            "nominator_list_id": list_id,
            "run": run,
            "simulation_id": simulation_id,
            "winner_proposal_id": winner["proposal_id"],
            "no_award": winner["no_award"],
            "laureates": list(names),
            "discoveries": discoveries,
            "decisive_round": final_round["round"],
            "winning_votes": winning_votes,
            "decision_path": relative_path,
        }
        records.append(record)
        configurations[names].append(key)
        by_list[list_id][names].append(key)

    records.sort(key=lambda item: item["simulation_key"])

    def counts(values: dict[tuple[str, ...], list[str]], denominator: int) -> list[dict]:
        ranked = sorted(values.items(), key=lambda item: (-len(item[1]), item[0]))
        return [
            {
                "laureates": list(names),
                "count": len(keys),
                "share": len(keys) / denominator,
                "simulation_keys": sorted(keys),
            }
            for names, keys in ranked
        ]

    rejected = sorted(
        path.relative_to(ROOT).as_posix()
        for path in (RESULTS / RUNTIME_DIRECTORY).glob(
            "**/rejected-output.json"
        )
    )
    summary = {
        "schema_version": 1,
        "arm_id": ARM_ID,
        "record_type": "committee_decision_summary",
        "model": MODEL,
        "reasoning_effort": REASONING,
        "source_decision_count": len(records),
        "expected_decision_count": EXPECTED_COUNT,
        "method": (
            "Deterministic aggregation of validated decision.json records. "
            "Laureate configurations use exact saved name strings sorted "
            "within each configuration; no semantic name normalization is applied."
        ),
        "coverage": {
            list_id: sum(1 for record in records if record["nominator_list_id"] == list_id)
            for list_id in LIST_IDS
        },
        "configuration_counts": counts(configurations, len(records)),
        "configuration_counts_by_nominator_list": {
            list_id: counts(by_list[list_id], 30) for list_id in LIST_IDS
        },
        "rejected_attempt_count": len(rejected),
        "rejected_attempt_paths": rejected,
        "decisions": records,
    }
    return summary, records


def write_summary() -> None:
    summary, records = build_summary()
    OUTPUT_JSON.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(
            [
                "simulation_key",
                "nominator_list_id",
                "run",
                "simulation_id",
                "winner_proposal_id",
                "no_award",
                "laureates",
                "discoveries",
                "decisive_round",
                "winning_votes",
                "decision_path",
            ]
        )
        for record in records:
            writer.writerow(
                [
                    record["simulation_key"],
                    record["nominator_list_id"],
                    record["run"],
                    record["simulation_id"],
                    record["winner_proposal_id"],
                    str(record["no_award"]).lower(),
                    " | ".join(record["laureates"]),
                    " | ".join(record["discoveries"]),
                    record["decisive_round"],
                    record["winning_votes"],
                    record["decision_path"],
                ]
            )
    print(f"OK: summarized {len(records)} {DISPLAY_NAME} committee decisions")


if __name__ == "__main__":
    write_summary()
