#!/usr/bin/env python3
"""Render the Luna committee distribution using the shared Physics chart style."""

from plot_physics_prediction_distributions import FIGURES, luna_decisions, plot


def main() -> None:
    counts = luna_decisions()
    FIGURES.mkdir(parents=True, exist_ok=True)
    plot("physics-luna-committee-v1-distribution.png", "GPT-6 Luna committee",
         "Profiles with inferred traits · v1", counts, len(counts))


if __name__ == "__main__":
    main()
