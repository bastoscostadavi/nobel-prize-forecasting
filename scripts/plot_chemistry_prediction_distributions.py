#!/usr/bin/env python3
"""Render the completed Chemistry forecast in the Physics/Medicine figure format."""

from __future__ import annotations

import json
import hashlib
from collections import Counter

import plot_physics_prediction_distributions as physics

ROOT = physics.ROOT
physics.SLATE_COLORS.update({
    "Crews–Deshaies–Handa": "#167D8D",
    "Ciulli–Crews–Deshaies": "#4FA3AE",
    "Buchwald–Hartwig": "#C17B35",
    "Gaudelli–Komor–Liu": "#7162AA",
    "Buchwald–Hartwig / Liu": "#9A8CC8",
    "Liu": "#9A8CC8",
    "Crews–Handa / Liu": "#4FA3AE",
    "Crews–Deshaies / Liu": "#4FA3AE",
    "Car–Parrinello": "#7162AA",
    "Balasubramanian–Klenerman–Mayer": "#167D8D",
    "Matyjaszewski–Sawamoto": "#C17B35",
    "Matyjaszewski–Rizzardo–Sawamoto": "#D9A066",
})

CHEMISTRY_DESCRIPTIONS = {
    "Car–Parrinello": "First-principles molecular dynamics",
    "Crews–Deshaies–Handa": "PROTACs and molecular glue degraders",
    "Ciulli–Crews–Deshaies": "Targeted protein degradation",
    "Buchwald–Hartwig": "Palladium-catalyzed carbon–nitrogen cross-coupling",
    "Gaudelli–Komor–Liu": "Programmable DNA base editing",
    "Crews–Deshaies / Liu": "Targeted protein degradation / DNA base editing",
    "Buchwald–Hartwig / Liu": "Carbon–nitrogen cross-coupling / DNA base editing",
    "Balasubramanian–Klenerman": "Next-generation DNA sequencing",
    "Liu": "Programmable DNA base editing",
    "Cullis–Hope–Madden": "Lipid nanoparticles for nucleic-acid delivery",
    "Crews–Handa / Liu": "Targeted protein degradation / DNA base editing",
    "Makarov": "Orbitrap mass spectrometry",
}


def label(names: list[str]) -> str:
    """Surnames in alphabetical order, so identical trios share a label regardless of name spelling."""
    return "–".join(sorted(name.split()[-1] for name in names))


def committee(pattern: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for path in sorted((ROOT / "results/chemistry/committee").glob(f"{pattern}/sim-*/decision.json")):
        parts = json.loads(path.read_text())["winner"]["prize_parts"]
        # A split prize keeps its parts apart, in sorted order: "Buchwald–Hartwig / Liu".
        counts[" / ".join(sorted(label(p["laureates"]) for p in parts)) or "No award"] += 1
    if sum(counts.values()) != 50:
        raise ValueError(f"Expected 50 completed {pattern} decisions, got {sum(counts.values())}")
    return counts


def claude_oneshot() -> Counter[str]:
    counts: Counter[str] = Counter()
    for path in sorted((ROOT / "results/chemistry/oneshot/claude-opus-5-5").glob("pred-*.json")):
        counts[label(json.loads(path.read_text())["laureates"])] += 1
    return counts


def main() -> None:
    # The published summary binds every input decision to its validated snapshot.
    summary = json.loads((ROOT / "results/chemistry/final_summary.json").read_text())
    if summary["completed_simulations"] != 100:
        raise ValueError("Expected 100 validated Chemistry decisions")
    for source in summary["source_decisions"]:
        path = ROOT / source["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError(f"Decision changed since validation: {path}")
    claude = committee("claude*")
    terra = committee("gpt-5.6-terra")
    aggregate = claude + terra
    physics.FIGURES.mkdir(parents=True, exist_ok=True)
    physics.ranked_plot("chemistry-committee-top5.png", "2026 Nobel Prize in Chemistry",
                        aggregate, CHEMISTRY_DESCRIPTIONS, limit=5)
    physics.ranked_plot("chemistry-committee-full-distribution.png", "2026 Nobel Prize in Chemistry",
                        aggregate, CHEMISTRY_DESCRIPTIONS)
    rows = max(len(claude), len(terra))
    physics.plot("chemistry-claude-committee-distribution.png", "Claude committee",
                 "Claude Sonnet 5.5", claude, rows)
    physics.plot("chemistry-terra-committee-distribution.png", "Terra committee",
                 "GPT-5.6 Terra", terra, rows)
    claude_direct = claude_oneshot()
    if claude_direct:
        physics.plot("chemistry-claude-oneshot-distribution.png", "Claude one-shot",
                     "Claude Opus 5.5", claude_direct, len(claude_direct))
    print({"aggregate": dict(aggregate), "terra": dict(terra), "claude": dict(claude),
           "claude_oneshot": dict(claude_direct)})


if __name__ == "__main__":
    main()
