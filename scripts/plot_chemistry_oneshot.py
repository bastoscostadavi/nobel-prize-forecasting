#!/usr/bin/env python3
"""Render the Sol Chemistry one-shot distribution in the existing forecast style."""

import hashlib
import json
from collections import Counter

import plot_physics_prediction_distributions as physics


def main() -> None:
    root = physics.ROOT / "results/chemistry/oneshot/gpt-6.1-sol"
    summary = json.loads((root / "posthoc_transcription_summary.json").read_text())
    if summary["source_record_count"] != 60 or len(summary["source_records"]) != 60:
        raise ValueError("Expected 60 validated Sol one-shot predictions")
    counts = Counter()
    for source in summary["source_records"]:
        directory = root / source["prediction_id"]
        for filename, hash_key in [("response.txt", "response_sha256"), ("result.json", "result_sha256")]:
            if hashlib.sha256((directory / filename).read_bytes()).hexdigest() != source[hash_key]:
                raise ValueError(f"Source changed: {directory / filename}")
        result = json.loads((directory / "result.json").read_text())
        parts = result["prize_configuration"]["prize_parts"]
        label = " / ".join(sorted(
            "–".join(sorted(name.split()[-1] for name in part["credited_names"]))
            for part in parts
        )) or "No award"
        counts[label] += 1
    if sum(counts.values()) != 60:
        raise ValueError("Expected 60 prediction outcomes")
    physics.SLATE_COLORS.update({"Balasubramanian–Klenerman–Mayer": "#167D8D"})
    physics.FIGURES.mkdir(parents=True, exist_ok=True)
    physics.plot("chemistry-openai-oneshot-distribution.png", "OpenAI one-shot",
                 "GPT-6.1 Sol", counts, len(counts))
    print(dict(counts))


if __name__ == "__main__":
    main()
