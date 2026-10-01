#!/usr/bin/env python3
"""Compare Terra/high and Luna/high committee outcomes without model calls."""

from __future__ import annotations

import itertools
import json
import math
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "physics"
TERRA_PATH = RESULTS / "terra_committee_summary.json"
LUNA_PATH = RESULTS / "luna_committee_summary.json"
OUTPUT_JSON = RESULTS / "openai_committee_model_comparison.json"
OUTPUT_MD = RESULTS / "openai_committee_model_comparison.md"
TARGET = ("Hidetoshi Katori", "Jun Ye")
NAME_ALIASES = {
    "Max Haider": "Maximilian Haider",
    "Michael V. Berry": "Michael Berry",
    "Tejinder S. Virdee": "Tejinder Virdee",
}
EXPECTED_N = 60
EXPECTED_CLUSTERS = 12


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    if value.get("source_decision_count") != EXPECTED_N:
        raise ValueError(f"expected {EXPECTED_N} decisions in {path}")
    return value


def configuration(record: dict) -> tuple[str, ...]:
    return tuple(sorted(NAME_ALIASES.get(name, name) for name in record["laureates"]))


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> list[float]:
    proportion = successes / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    half = z * math.sqrt(
        proportion * (1 - proportion) / total + z * z / (4 * total * total)
    ) / denominator
    return [center - half, center + half]


def fisher_two_sided(a: int, b: int, c: int, d: int) -> float:
    """Two-sided Fisher exact p-value for [[a, b], [c, d]]."""
    first_row = a + b
    successes = a + c
    total = a + b + c + d
    low = max(0, first_row - (total - successes))
    high = min(first_row, successes)

    def probability(x: int) -> Fraction:
        return Fraction(
            math.comb(successes, x) * math.comb(total - successes, first_row - x),
            math.comb(total, first_row),
        )

    observed = probability(a)
    return float(sum((probability(x) for x in range(low, high + 1)
                      if probability(x) <= observed), Fraction(0, 1)))


def summarize(summary: dict) -> dict:
    records = summary["decisions"]
    distribution = Counter(configuration(record) for record in records)
    target_count = distribution[TARGET]
    entropy = -sum(
        (count / len(records)) * math.log2(count / len(records))
        for count in distribution.values()
    )
    return {
        "model": summary["model"],
        "reasoning_effort": summary["reasoning_effort"],
        "n": len(records),
        "katori_ye_count": target_count,
        "katori_ye_share": target_count / len(records),
        "katori_ye_wilson_95": wilson(target_count, len(records)),
        "distinct_winner_configurations": len(distribution),
        "winner_entropy_bits": entropy,
        "distribution": distribution,
    }


def cluster_counts(summary: dict) -> dict[tuple[str, int], int]:
    values: dict[tuple[str, int], int] = defaultdict(int)
    totals: dict[tuple[str, int], int] = defaultdict(int)
    for record in summary["decisions"]:
        key = (record["nominator_list_id"], int(record["run"]))
        totals[key] += 1
        if configuration(record) == TARGET:
            values[key] += 1
    if len(totals) != EXPECTED_CLUSTERS or any(total != 5 for total in totals.values()):
        raise ValueError("expected 12 nomination-run clusters with five simulations each")
    return {key: values[key] for key in totals}


def paired_sign_flip(differences: list[int]) -> dict:
    nonzero = [difference for difference in differences if difference]
    observed = abs(sum(nonzero))
    if not nonzero:
        return {"nonzero_clusters": 0, "p_value_two_sided": 1.0}
    extreme = 0
    total = 2 ** len(nonzero)
    for signs in itertools.product((-1, 1), repeat=len(nonzero)):
        if abs(sum(sign * difference for sign, difference in zip(signs, nonzero))) >= observed:
            extreme += 1
    return {
        "nonzero_clusters": len(nonzero),
        "observed_sum_of_luna_minus_terra_counts": sum(nonzero),
        "permutation_count": total,
        "extreme_permutation_count": extreme,
        "p_value_two_sided": extreme / total,
    }


def label(names: tuple[str, ...]) -> str:
    return " + ".join(names)


def main() -> None:
    terra_raw = load(TERRA_PATH)
    luna_raw = load(LUNA_PATH)
    terra = summarize(terra_raw)
    luna = summarize(luna_raw)

    all_configurations = set(terra["distribution"]) | set(luna["distribution"])
    tvd = 0.5 * sum(
        abs(luna["distribution"][names] / EXPECTED_N
            - terra["distribution"][names] / EXPECTED_N)
        for names in all_configurations
    )

    a = luna["katori_ye_count"]
    b = EXPECTED_N - a
    c = terra["katori_ye_count"]
    d = EXPECTED_N - c
    odds_ratio = (a * d) / (b * c) if b and c else None
    fisher_p = fisher_two_sided(a, b, c, d)

    terra_clusters = cluster_counts(terra_raw)
    luna_clusters = cluster_counts(luna_raw)
    if set(terra_clusters) != set(luna_clusters):
        raise ValueError("Terra and Luna nomination-run clusters do not match")
    cluster_rows = []
    differences = []
    for key in sorted(terra_clusters):
        difference = luna_clusters[key] - terra_clusters[key]
        differences.append(difference)
        cluster_rows.append({
            "nominator_list_id": key[0],
            "run": key[1],
            "terra_katori_ye_wins": terra_clusters[key],
            "luna_katori_ye_wins": luna_clusters[key],
            "luna_minus_terra": difference,
        })
    paired = paired_sign_flip(differences)
    significant = fisher_p < 0.05 and paired["p_value_two_sided"] < 0.05

    distributions = []
    for names in sorted(
        all_configurations,
        key=lambda names: (-(terra["distribution"][names] + luna["distribution"][names]), names),
    ):
        distributions.append({
            "laureates": list(names),
            "terra_count": terra["distribution"][names],
            "luna_count": luna["distribution"][names],
        })

    def public_arm(value: dict) -> dict:
        return {key: item for key, item in value.items() if key != "distribution"}

    result = {
        "schema_version": 1,
        "record_type": "committee_model_sensitivity_comparison",
        "comparison": "GPT-6 Luna high versus GPT-5.6 Terra high",
        "target_configuration": list(TARGET),
        "name_aliases_used_for_comparison": NAME_ALIASES,
        "terra": public_arm(terra),
        "luna": public_arm(luna),
        "effect": {
            "katori_ye_share_difference_luna_minus_terra": (
                luna["katori_ye_share"] - terra["katori_ye_share"]
            ),
            "katori_ye_odds_ratio_luna_vs_terra": odds_ratio,
            "total_variation_distance_all_winners": tvd,
        },
        "tests": {
            "simulation_level_fisher_exact_two_sided": {
                "table_luna_then_terra_success_failure": [[a, b], [c, d]],
                "p_value": fisher_p,
                "note": "Treats the 60 simulations in each arm as independent.",
            },
            "nomination_run_cluster_paired_sign_flip_two_sided": paired,
        },
        "significant_at_0_05_under_both_tests": significant,
        "interpretation": (
            "The committee-model substitution materially changes the simulated "
            "winner distribution." if significant else
            "The saved simulations do not establish a change under both prespecified tests."
        ),
        "winner_configuration_counts": distributions,
        "nomination_run_cluster_counts": cluster_rows,
        "method_note": (
            "The binary tests compare Katori–Ye with all other saved winner "
            "configurations. Fisher's exact test is simulation-level; the exact "
            "paired sign-flip test treats each of the 12 shared nomination runs as "
            "a cluster. Model arms use separate deterministic seed namespaces, so "
            "candidate-order shuffles are independent rather than position-matched. "
            "This is a sensitivity analysis of stochastic simulations, not evidence "
            "about the real Nobel committee's sampling distribution."
        ),
    }
    OUTPUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rows = [
        "# OpenAI committee-model sensitivity comparison",
        "",
        "The nomination lists, personas, substantive protocol, evidence boundary, and five-simulation allocation are fixed. The model arms use independent deterministic candidate-order shuffles, so this is a model-arm sensitivity comparison rather than an exact prompt-token pair.",
        "Obvious saved-name variants are normalized for this comparison; the raw arm summaries retain the exact saved strings.",
        "",
        "| Committee model | Katori–Ye wins | Share | Wilson 95% CI | Distinct winners | Entropy (bits) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for value in (terra, luna):
        low, high = value["katori_ye_wilson_95"]
        rows.append(
            f"| {value['model']} (`{value['reasoning_effort']}`) | "
            f"{value['katori_ye_count']}/{value['n']} | {value['katori_ye_share']:.1%} | "
            f"{low:.1%}–{high:.1%} | {value['distinct_winner_configurations']} | "
            f"{value['winner_entropy_bits']:.3f} |"
        )
    rows.extend([
        "",
        f"Katori–Ye changes by {result['effect']['katori_ye_share_difference_luna_minus_terra']:+.1%} (Luna minus Terra).",
        f"The full winner distributions have total-variation distance {tvd:.3f}.",
        f"Simulation-level Fisher exact: p = {fisher_p:.6g}.",
        f"Paired 12-nomination-run sign-flip test: p = {paired['p_value_two_sided']:.6g}.",
        "",
        f"**Conclusion:** {result['interpretation']}",
        "",
        "## Winner configurations",
        "",
        "| Laureates | Terra | Luna |",
        "|---|---:|---:|",
    ])
    for item in distributions:
        rows.append(f"| {label(tuple(item['laureates']))} | {item['terra_count']} | {item['luna_count']} |")
    rows.extend(["", "See the JSON companion for per-nomination-run counts and exact test metadata.", ""])
    OUTPUT_MD.write_text("\n".join(rows), encoding="utf-8")
    print(f"OK: wrote {OUTPUT_JSON.relative_to(ROOT)} and {OUTPUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
