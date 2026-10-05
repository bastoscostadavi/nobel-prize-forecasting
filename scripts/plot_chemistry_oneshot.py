#!/usr/bin/env python3
"""Render the Sol and Claude Chemistry one-shot distributions side by side in the existing forecast style."""

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
    claude = Counter()
    for path in sorted((physics.ROOT / "results/chemistry/oneshot/claude-opus-5-5").glob("pred-*.json")):
        claude["–".join(sorted(name.split()[-1] for name in json.loads(path.read_text())["laureates"]))] += 1
    if sum(claude.values()) != 50:
        raise ValueError("Expected 50 Claude one-shot predictions")
    physics.SLATE_COLORS.update({
        "Balasubramanian–Klenerman–Mayer": "#167D8D",
        "Balasubramanian–Klenerman": "#4FA3AE",
        "Buchwald–Hartwig": "#C17B35",
        "Matyjaszewski–Sawamoto": "#7162AA",
        "Matyjaszewski–Rizzardo–Sawamoto": "#9A8CC8",
    })
    physics.FIGURES.mkdir(parents=True, exist_ok=True)
    # Equal row counts keep the two charts the same height in the README table.
    rows = max(len(counts), len(claude))
    physics.plot("chemistry-openai-oneshot-distribution.png", "OpenAI one-shot",
                 "GPT-6.1 Sol", counts, rows)
    physics.plot("chemistry-claude-oneshot-distribution.png", "Claude one-shot",
                 "Claude Opus 5.5", claude, rows)
    print({"sol": dict(counts), "claude": dict(claude)})


if __name__ == "__main__":
    main()
