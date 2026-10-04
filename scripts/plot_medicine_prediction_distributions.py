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
    "Frazer–Lowy–Schiller": "#C17B35",
    "Cooper–Miller": "#7162AA",
    "Mori–Walter": "#9A8CC8",
    "Feldmann–Maini": "#8C9BA6",
    "Lo": "#B0BAC1",
    "Habener–Knudsen–Mojsov": "#7162AA",
    "Drucker–Habener–Mojsov": "#9A8CC8",
})


def label(names: list[str]) -> str:
    """Surnames in alphabetical order, so identical trios share a label regardless of name spelling."""
    return "–".join(sorted(name.split()[-1] for name in names))


def committee(cohort: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for path in sorted((ROOT / "results/medicine/committee" / cohort).glob("sim-*/decision.json")):
        parts = json.loads(path.read_text())["winner"]["prize_parts"]
        counts[" + ".join(label(p["laureates"]) for p in parts) or "No award"] += 1
    return counts


def claude_oneshot() -> Counter[str]:
    counts: Counter[str] = Counter()
    for path in sorted((ROOT / "results/medicine/oneshot/claude-opus-5-5").glob("pred-*.json")):
        counts[label(json.loads(path.read_text())["laureates"])] += 1
    return counts


def main() -> None:
    claude = committee("claude")
    terra = committee("gpt-5.6-terra")
    aggregate = claude + terra
    oneshot = claude_oneshot()
    committee_rows = max(len(claude), len(terra))
    oneshot_rows = max(len(claude), len(oneshot))
    physics.plot("medicine-committee-aggregate-distribution.png", "Medicine committee aggregate",
                 "Claude Sonnet 5.5 + GPT-5.6 Terra", aggregate, len(aggregate))
    physics.plot("medicine-claude-committee-distribution.png", "Claude committee",
                 "Claude Sonnet 5.5", claude, committee_rows)
    physics.plot("medicine-terra-committee-distribution.png", "Terra committee",
                 "GPT-5.6 Terra", terra, committee_rows)
    physics.plot("medicine-claude-oneshot-distribution.png", "Claude one-shot",
                 "Claude Opus 5.5", oneshot, oneshot_rows)
    print({"aggregate": dict(aggregate), "claude": dict(claude),
           "terra": dict(terra), "oneshot": dict(oneshot)})


if __name__ == "__main__":
    main()
