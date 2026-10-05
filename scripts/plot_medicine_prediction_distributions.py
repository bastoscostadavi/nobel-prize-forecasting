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
    "Habener–Holst–Mojsov": "#167D8D",
    "Drucker–Habener–Mojsov": "#9A8CC8",
    "Eshhar–June–Sadelain": "#C17B35",
})

MEDICINE_DESCRIPTIONS = {
    "Drucker–Holst–Mojsov": "GLP-1 physiology and incretin therapies",
    "Frazer–Lowy–Schiller": "HPV virus-like particle vaccines",
    "Cooper–Miller": "B- and T-lymphocyte lineages",
    "Drucker–Holst–Knudsen": "GLP-1 physiology and long-acting drugs",
    "Mori–Walter": "Unfolded protein response",
    "Hartl–Horwich": "Chaperonin-assisted protein folding",
    "Feldmann–Maini": "TNF blockade",
    "Lo": "Cell-free fetal DNA and prenatal screening",
}


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


def sol_oneshot() -> Counter[str]:
    counts: Counter[str] = Counter()
    root = ROOT / "results/medicine/oneshot/gpt-6-sol"
    for path in sorted(root.glob("pred-*/result.json")):
        parts = json.loads(path.read_text())["prize_configuration"]["prize_parts"]
        names = [name for part in parts for name in part["credited_names"]]
        counts[label(names)] += 1
    return counts


def main() -> None:
    claude = committee("claude")
    terra = committee("gpt-5.6-terra")
    aggregate = claude + terra
    claude_direct = claude_oneshot()
    sol_direct = sol_oneshot()
    committee_rows = max(len(claude), len(terra))
    oneshot_rows = max(len(claude_direct), len(sol_direct))
    physics.plot("medicine-committee-aggregate-distribution.png", "Medicine results",
                 None, aggregate, len(aggregate))
    physics.ranked_plot(
        "medicine-committee-top5.png",
        "2026 Nobel Prize in Physiology or Medicine",
        aggregate,
        MEDICINE_DESCRIPTIONS,
        limit=5,
    )
    physics.ranked_plot(
        "medicine-committee-full-distribution.png",
        "2026 Nobel Prize in Physiology or Medicine",
        aggregate,
        MEDICINE_DESCRIPTIONS,
    )
    physics.plot("medicine-claude-committee-distribution.png", "Claude committee",
                 "Claude Sonnet 5.5", claude, committee_rows)
    physics.plot("medicine-terra-committee-distribution.png", "Terra committee",
                 "GPT-5.6 Terra", terra, committee_rows)
    physics.plot("medicine-openai-oneshot-distribution.png", "OpenAI one-shot",
                 "GPT-6 Sol", sol_direct, oneshot_rows)
    physics.plot("medicine-claude-oneshot-distribution.png", "Claude one-shot",
                 "Claude Opus 5.5", claude_direct, oneshot_rows)
    print({"aggregate": dict(aggregate), "claude": dict(claude),
           "terra": dict(terra), "sol_oneshot": dict(sol_direct),
           "claude_oneshot": dict(claude_direct)})


if __name__ == "__main__":
    main()
