#!/usr/bin/env python3
"""Render the Medicine prediction distributions shown in the README."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import plot_physics_prediction_distributions as physics

ROOT = physics.ROOT
physics.SLATE_COLORS.update({
    "Drucker–Holst–Mojsov": "#167D8D",
    "Drucker–Holst–Knudsen": "#4FA3AE",
    "Habener–Knudsen–Mojsov": "#7162AA",
    "Drucker–Habener–Mojsov": "#9A8CC8",
})


def label(names: list[str]) -> str:
    """Surnames in alphabetical order, so identical trios share a label regardless of name spelling."""
    return "–".join(sorted(name.split()[-1] for name in names))


def claude_committee() -> Counter[str]:
    counts: Counter[str] = Counter()
    for path in sorted((ROOT / "results/medicine/committee/claude").glob("sim-*/decision.json")):
        parts = json.loads(path.read_text())["winner"]["prize_parts"]
        counts[" + ".join(label(p["laureates"]) for p in parts) or "No award"] += 1
    return counts


def claude_oneshot() -> Counter[str]:
    counts: Counter[str] = Counter()
    for path in sorted((ROOT / "results/medicine/oneshot/claude-opus-5-5").glob("pred-*.json")):
        counts[label(json.loads(path.read_text())["laureates"])] += 1
    return counts


def main() -> None:
    committee, oneshot = claude_committee(), claude_oneshot()
    rows = max(len(committee), len(oneshot))
    physics.plot("medicine-claude-committee-distribution.png", "Claude committee",
                 "Claude Sonnet 5.5", committee, rows)
    physics.plot("medicine-claude-oneshot-distribution.png", "Claude one-shot",
                 "Claude Opus 5.5", oneshot, rows)
    print(dict(committee), dict(oneshot))


if __name__ == "__main__":
    main()
