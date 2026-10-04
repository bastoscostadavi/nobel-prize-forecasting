#!/usr/bin/env python3
"""Transcribe primary predictions from the saved GPT-6 Sol Medicine responses."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import medicine_oneshot as protocol


GROUPS = {
    "K": {
        "ids": [1, 3, 4, 5, 8, 9, 10, 11, 12, 13, 14, 15, 17, 19, 20, 22, 23, 29, 31, 33, 34, 43, 44, 50, 54, 56, 57],
        "names": ["Joel Habener", "Svetlana Mojsov", "Lotte Bjerre Knudsen"],
        "description": "GLP-1 biology and the development of GLP-1 medicines",
    },
    "H": {
        "ids": [6, 7, 16, 18, 21, 24, 26, 27, 30, 32, 35, 36, 37, 38, 39, 40, 41, 45, 46, 47, 48, 52, 53, 58, 59, 60],
        "names": ["Joel Habener", "Svetlana Mojsov", "Jens Juul Holst"],
        "description": "discovery and characterization of GLP-1 physiology",
    },
    "D": {
        "ids": [25, 42, 49],
        "names": ["Joel Habener", "Svetlana Mojsov", "Daniel Drucker"],
        "description": "GLP-1 biology and its therapeutic significance",
    },
    "T": {
        "ids": [2],
        "names": ["Svetlana Mojsov", "Jens Juul Holst", "Daniel Drucker"],
        "description": "GLP-1 physiology and the development of GLP-1 medicines",
    },
    "X": {
        "ids": [28],
        "names": ["Joel Habener", "Jens Juul Holst", "Daniel Drucker"],
        "description": "GLP-1 physiology and its therapeutic significance",
    },
    "C": {
        "ids": [51, 55],
        "names": ["Zelig Eshhar", "Michel Sadelain", "Carl June"],
        "description": "development of chimeric antigen receptor T-cell therapy",
    },
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def reasoning_tokens(path: Path) -> int | None:
    value = None
    for line in path.read_text(encoding="utf-8").splitlines():
        event = json.loads(line)
        if event.get("type") == "turn.completed":
            value = event.get("usage", {}).get("reasoning_output_tokens")
    return value


def main() -> None:
    assignments = {}
    for group in GROUPS.values():
        for number in group["ids"]:
            if number in assignments:
                raise ValueError(f"duplicate transcription for prediction {number}")
            assignments[number] = group
    if set(assignments) != set(range(1, 61)):
        raise ValueError("transcriptions must cover predictions 1 through 60 exactly")

    counts: Counter[tuple[str, ...]] = Counter()
    for number in range(1, 61):
        prediction_id = f"pred-{number:03d}"
        directory = protocol.ARM_ROOT / prediction_id
        response = (directory / "response.txt").read_bytes()
        execution = load(directory / "execution.json")
        group = assignments[number]
        names = group["names"]
        result = {
            "schema_version": 1,
            "arm_id": protocol.ARM_ID,
            "prediction_id": prediction_id,
            "prompt_version": protocol.PROMPT_VERSION,
            "execution": {
                "provider": "openai",
                "interface": execution["interface"],
                "requested_model": protocol.MODEL,
                "returned_model": protocol.MODEL,
                "reasoning_effort": protocol.REASONING_EFFORT,
                "request_id": execution["thread_id"],
                "response_id": None,
                "created_at_utc": execution["completed_at_utc"],
                "usage": {
                    "input_tokens": execution["usage"]["input_tokens"],
                    "output_tokens": execution["usage"]["output_tokens"],
                    "reasoning_tokens": reasoning_tokens(directory / "runtime.jsonl"),
                    "total_tokens": execution["usage"]["total_tokens"],
                },
            },
            "response_file": "response.txt",
            "response_sha256": hashlib.sha256(response).hexdigest(),
            "prize_configuration": {
                "outcome": "award",
                "prize_parts": [{
                    "credited_names": names,
                    "description": group["description"],
                }],
            },
            "rationale": group["description"],
        }
        (directory / "result.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        counts[tuple(sorted(names))] += 1

    summary = {
        "schema_version": 1,
        "arm_id": protocol.ARM_ID,
        "record_type": "post_hoc_transcription_summary",
        "source_record_count": 60,
        "method": (
            "Post-hoc transcription of the primary prize configuration in each "
            "saved verbatim response; alternatives were excluded."
        ),
        "configuration_counts": [
            {"credited_names": list(names), "count": count}
            for names, count in counts.most_common()
        ],
    }
    (protocol.ARM_ROOT / "posthoc_transcription_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
