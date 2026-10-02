#!/usr/bin/env python3
"""Render the aggregate and individual Physics prediction distributions in the README."""

from __future__ import annotations

import json
import textwrap
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "docs" / "figures"


def load_json(path: Path) -> dict:
    with path.open() as handle:
        return json.load(handle)


def labels_for(names: list[str]) -> str:
    surname = {
        "Hidetoshi Katori": "Katori",
        "Jun Ye": "Ye",
        "Harald Rose": "Rose",
        "Maximilian Haider": "Haider",
        "Ondrej L. Krivanek": "Krivanek",
        "Charles L. Kane": "Kane",
        "Charles Kane": "Kane",
        "Eugene J. Mele": "Mele",
        "Eugene Mele": "Mele",
        "Laurens W. Molenkamp": "Molenkamp",
        "Laurenz W. Molenkamp": "Molenkamp",
        "Laurens Molenkamp": "Molenkamp",
        "Allan H. MacDonald": "MacDonald",
        "Allan MacDonald": "MacDonald",
        "Pablo Jarillo-Herrero": "Jarillo-Herrero",
        "Rafi Bistritzer": "Bistritzer",
        "Michael Berry": "Berry",
        "Yakir Aharonov": "Aharonov",
        "Juan Ignacio Cirac": "Cirac",
        "Ignacio Cirac": "Cirac",
        "Peter Zoller": "Zoller",
        "Rainer Blatt": "Blatt",
        "Jocelyn Bell Burnell": "Bell Burnell",
        "Alexandre Blais": "Blais",
        "Andreas Wallraff": "Wallraff",
        "Robert J. Schoelkopf": "Schoelkopf",
        "David R. Smith": "Smith",
        "David Smith": "Smith",
        "John B. Pendry": "Pendry",
        "John Pendry": "Pendry",
        "Sir John Pendry": "Pendry",
        "Ulf Leonhardt": "Leonhardt",
        "Nader Engheta": "Engheta",
        "Eli Yablonovitch": "Yablonovitch",
        "Sajeev John": "John",
        "Immanuel Bloch": "Bloch",
        'Alexei Kitaev': 'Kitaev',
        'Andrew M. Steane': 'Steane',
        'Peter W. Shor': 'Shor',
        'Michel Della Negra': 'Della Negra',
        'Peter Jenni': 'Jenni',
        'Tejinder Virdee': 'Virdee',
        'Alessandra Buonanno': 'Buonanno',
        'Frans Pretorius': 'Pretorius',
        'Thibault Damour': 'Damour',
        'Alexander A. Belavin': 'Belavin',
        'Alexander B. Zamolodchikov': 'Zamolodchikov',
        'Alexander M. Polyakov': 'Polyakov',
        'Alfred Y. Cho': 'Cho',
        'Federico Capasso': 'Capasso',
        'Jérôme Faist': 'Faist',
        'Artur K. Ekert': 'Ekert',
        'Charles H. Bennett': 'Bennett',
        'Gilles Brassard': 'Brassard',
        'Bart J. van Wees': 'van Wees',
        'David A. Wharam': 'Wharam',
        'Chang C. Tsuei': 'Tsuei',
        'Dale J. Van Harlingen': 'Van Harlingen',
        'John R. Kirtley': 'Kirtley',
        'Charles L. Bennett': 'Bennett',
        'David N. Spergel': 'Spergel',
        'Lyman A. Page Jr.': 'Page',
        'Christophe Salomon': 'Salomon',
        'John E. Thomas': 'Thomas',
        'Rudolf Grimm': 'Grimm',
        'John D. Joannopoulos': 'Joannopoulos',
        'John G. Baker': 'Baker',
        'Manuela Campanelli': 'Campanelli',
        'Knut Urban': 'Urban',
        'Peter F. Moulton': 'Moulton',
        'Ursula Keller': 'Keller',
        'Wilson Sibbett': 'Sibbett',
    }
    return "–".join(surname.get(name, name) for name in names)


def luna_decisions() -> Counter[str]:
    from compare_openai_committee_models import configuration, load, LUNA_PATH

    data = load(LUNA_PATH)
    counts = Counter(labels_for(configuration(record)) for record in data["decisions"])
    if sum(counts.values()) != 60 or len(counts) != 21:
        raise ValueError("Expected 60 Luna decisions and 21 normalized slates")
    return counts


def aggregate_counts(arms: list[Counter[str]]) -> Counter[str]:
    """Merge identical slates regardless of saved laureate order."""
    labels: dict[tuple[str, ...], str] = {}
    combined: Counter[str] = Counter()
    for counts in arms:
        if sum(counts.values()) != 60:
            raise ValueError("Expected 60 decisions per committee experiment")
        for label, count in counts.items():
            signature = tuple(sorted(label.split("–")))
            combined[labels.setdefault(signature, label)] += count
    return combined


def legacy_summary(path: Path) -> Counter[str]:
    data = load_json(path)
    return Counter(
        {labels_for(item["laureates"]): item["count"] for item in data["configuration_counts"]}
    )


def v2_decisions(cohort: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for path in ROOT.glob(f"results/physics/*/run-*/committee/{cohort}/sim-??/decision.json"):
        decision = load_json(path)
        names = [
            name
            for part in decision["winner"]["prize_parts"]
            for name in part["laureates"]
        ]
        counts[labels_for(names)] += 1
    return counts


def sol_oneshot() -> Counter[str]:
    data = load_json(
        ROOT
        / "results/physics/oneshot/gpt-6.1-sol/posthoc_transcription_summary.json"
    )
    counts: Counter[str] = Counter()
    for item in data["configuration_counts"]:
        counts[labels_for(item["credited_names"])] += item["count"]
    return counts


def claude_oneshot() -> Counter[str]:
    counts: Counter[str] = Counter()
    for path in (ROOT / "results/physics/oneshot/claude-opus-5-5").glob("pred-*.json"):
        prediction = load_json(path)
        counts[labels_for(prediction["laureates"])] += 1
    return counts


SLATE_COLORS = {
    "Katori–Ye": "#167D8D",
    "Berry–Aharonov": "#7162AA",
    "Aharonov–Berry": "#7162AA",
    "Kane–Mele–Molenkamp": "#C17B35",
}
INK = "#23313D"
MUTED = "#687783"


def display_label(label: str) -> str:
    """Wrap the longest slates without truncating any laureate names."""
    parts = label.split("–")
    if label == "MacDonald–Jarillo-Herrero–Bistritzer":
        return "MacDonald + Jarillo-Herrero\n+ Bistritzer"
    if label == "Yablonovitch–John–Pendry":
        return "Yablonovitch + John + Pendry"
    return textwrap.fill(" + ".join(parts), width=40,
                         break_long_words=False, break_on_hyphens=False)


def plot(
    filename: str,
    title: str,
    subtitle: str | None,
    counts: Counter[str],
    row_count: int,
) -> None:
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    total = sum(counts.values())
    if total == 0:
        raise ValueError(f"No predictions available for {title}")
    if row_count > 12:
        plot_wide(filename, title, subtitle, counts)
        return
    header_height = 1.55 if subtitle else 1.21
    height = header_height + 0.76 * row_count
    figure = plt.figure(figsize=(7.4, height), facecolor="white")
    # Fixed margins and paired heights make all six charts comparable.
    axis = figure.add_axes([0.045, 0.58 / height, 0.91, (height - (header_height - 0.07)) / height])
    axis.set_xlim(0, 129)
    axis.set_ylim(row_count - 0.28, -0.3)
    figure.text(0.045, 1 - 0.24 / height, title, color=INK,
                fontsize=15, fontweight="bold", va="top")
    if subtitle:
        figure.text(0.045, 1 - 0.57 / height,
                    f"{subtitle}  ·  {total} runs", color=MUTED, fontsize=10, va="top")

    for row, (label, count) in enumerate(ordered):
        probability = 100 * count / total
        color = SLATE_COLORS.get(label, "#8C9BA6")
        axis.text(0, row - 0.035, display_label(label), color=INK, fontsize=11,
                  va="center", linespacing=1.15)
        # A common 100% track makes short bars legible without changing scale.
        axis.barh(row + 0.32, 100, height=0.13, color="#F0F3F5", zorder=1)
        axis.barh(row + 0.32, probability, height=0.13, color=color, zorder=2)
        axis.text(129, row + 0.015, f"{probability:.1f}%", ha="right", va="center",
                  fontsize=12, fontweight="bold", color=INK)
        axis.text(129, row + 0.31, f"{count} / {total}", ha="right", va="center",
                  fontsize=9, color=MUTED)

    axis.set_yticks([])
    axis.set_xticks([0, 25, 50, 75, 100], ["0", "25", "50", "75", "100%"])
    axis.tick_params(axis="x", colors=MUTED, length=0, pad=8, labelsize=9)
    axis.spines[["top", "right", "left", "bottom"]].set_visible(False)
    axis.set_xlabel("Share of runs", fontsize=10, color=MUTED, labelpad=9)
    for value in [0, 25, 50, 75, 100]:
        axis.plot([value, value], [row_count - 0.23, row_count - 0.16],
                  color="#C7D0D6", linewidth=0.8, clip_on=False)
    figure.savefig(FIGURES / filename, dpi=220, facecolor="white")
    plt.close(figure)


def plot_wide(filename: str, title: str, subtitle: str | None,
              counts: Counter[str]) -> None:
    """Use two columns for distributions with many low-frequency slates."""
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    total = sum(counts.values())
    rows = (len(ordered) + 1) // 2
    header_height = 1.55 if subtitle else 1.21
    height = header_height + 0.76 * rows
    figure = plt.figure(figsize=(14.8, height), facecolor="white")
    figure.text(0.025, 1 - 0.24 / height, title,
                fontsize=19, fontweight="bold", color=INK, va="top")
    if subtitle:
        figure.text(0.025, 1 - 0.59 / height,
                    f"{subtitle} · {total} runs", fontsize=11, color=MUTED, va="top")
    for column in range(2):
        axis = figure.add_axes([0.025 + column * 0.5, 0.58 / height,
                               0.45, (height - (header_height - 0.07)) / height])
        axis.set_xlim(0, 129)
        axis.set_ylim(rows - 0.28, -0.3)
        for row, (label, count) in enumerate(ordered[column * rows:(column + 1) * rows]):
            probability = 100 * count / total
            axis.text(0, row - 0.035, display_label(label), color=INK, fontsize=11,
                      va="center", linespacing=1.15)
            axis.barh(row + 0.32, 100, height=0.13, color="#F0F3F5")
            axis.barh(row + 0.32, probability, height=0.13,
                      color=SLATE_COLORS.get(label, "#8C9BA6"))
            axis.text(129, row + 0.015, f"{probability:.1f}%", color=INK,
                      fontsize=12, fontweight="bold", ha="right", va="center")
            axis.text(129, row + 0.31, f"{count} / {total}", color=MUTED,
                      fontsize=9, ha="right", va="center")
        axis.set_yticks([])
        axis.set_xticks([0, 25, 50, 75, 100], ["0", "25", "50", "75", "100%"])
        axis.tick_params(axis="x", colors=MUTED, length=0, pad=8, labelsize=9)
        axis.spines[["top", "right", "bottom", "left"]].set_visible(False)
        axis.set_xlabel("Share of runs", color=MUTED, fontsize=10, labelpad=9)
    figure.savefig(FIGURES / filename, dpi=180, facecolor="white")
    plt.close(figure)


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    pairs = [
        (
            ("physics-openai-committee-v2-distribution.png", "OpenAI committee", "Factual profiles · v2", v2_decisions("gpt-5.6-terra-profile-v2")),
            ("physics-claude-committee-v2-distribution.png", "Claude committee", "Factual profiles · v2", v2_decisions("claude-profile-v2")),
        ),
        (
            ("physics-openai-committee-v1-distribution.png", "OpenAI committee", "Profiles with inferred traits · v1", legacy_summary(ROOT / "results/physics/terra_committee_summary.json")),
            ("physics-claude-committee-v1-distribution.png", "Claude committee", "Profiles with inferred traits · v1", legacy_summary(ROOT / "results/physics/claude_committee_summary.json")),
        ),
        (
            ("physics-openai-oneshot-distribution.png", "OpenAI one-shot", "GPT-6.1 Sol", sol_oneshot()),
            ("physics-claude-oneshot-distribution.png", "Claude one-shot", "Claude Opus 5.5", claude_oneshot()),
        ),
    ]
    luna = luna_decisions()
    # Luna is shown separately; the aggregate pools only the four Terra/Sonnet arms.
    committee_counts = aggregate_counts(
        [arm[3] for pair in pairs[:2] for arm in pair]
    )
    plot(
        "physics-committee-aggregate-distribution.png",
        "Physics results",
        None,
        committee_counts,
        len(committee_counts),
    )
    plot(
        "physics-luna-committee-v1-distribution.png",
        "GPT-6 Luna committee",
        "Profiles with inferred traits · v1",
        luna,
        len(luna),
    )

    for pair in pairs:
        row_count = max(len(arm[3]) for arm in pair)
        for filename, title, subtitle, counts in pair:
            plot(filename, title, subtitle, counts, row_count)


if __name__ == "__main__":
    main()
