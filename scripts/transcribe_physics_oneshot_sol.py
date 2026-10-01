"""Create post-hoc structured transcriptions of the saved GPT-6.1 Sol responses.

This script does not call a model or make new predictions. It maps each already
saved verbatim response to the primary prize configuration stated in that
response, copies execution metadata from the saved records, and writes aggregate
counts. Alternative or runner-up predictions are deliberately excluded.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARM_ROOT = ROOT / "results" / "physics" / "oneshot" / "gpt-6.1-sol"

QUANTUM_RATIONALE = (
    "The cited quantum-phase discoveries are experimentally established, "
    "foundational, and broadly influential across modern physics."
)
METAMATERIALS_RATIONALE = (
    "The work combines foundational theory, experimental demonstrations, and "
    "decades of influence in controlling electromagnetic waves."
)
TOPOLOGICAL_RATIONALE = (
    "The work combines foundational theoretical predictions with landmark "
    "experimental confirmation and established a major field."
)
CLOCK_RATIONALE = (
    "Optical lattice clocks combine extraordinary precision with tests of "
    "relativity and a possible future redefinition of the second."
)

# Exact credited-name strings are retained from each response's primary-pick
# sentence. Each tuple is (credited_names, achievement description, rationale).
TRANSCRIPTIONS: dict[str, tuple[list[str], str, str]] = {
    "pred-001": (["Michael Berry", "Yakir Aharonov"], "discoveries about quantum phase", QUANTUM_RATIONALE),
    "pred-002": (["John Pendry", "David R. Smith"], "work on metamaterials, including negative refraction", METAMATERIALS_RATIONALE),
    "pred-003": (["Charles Kane", "Eugene Mele", "Laurens Molenkamp"], "prediction and experimental discovery of topological insulators", TOPOLOGICAL_RATIONALE),
    "pred-004": (["John Pendry", "David R. Smith"], "pioneering metamaterials and demonstrating negative refraction", METAMATERIALS_RATIONALE),
    "pred-005": (["Michael Berry", "Yakir Aharonov"], "discoveries concerning quantum phases", QUANTUM_RATIONALE),
    "pred-006": (["Michael Berry", "Yakir Aharonov"], "revealing how quantum particles are affected by the geometry of their evolution and by electromagnetic potentials", QUANTUM_RATIONALE),
    "pred-007": (["Sir John Pendry", "David R. Smith"], "pioneering metamaterials", METAMATERIALS_RATIONALE),
    "pred-008": (["Michael Berry", "Yakir Aharonov"], "work on quantum phases, particularly the Berry phase and the Aharonov–Bohm effect", QUANTUM_RATIONALE),
    "pred-009": (["John Pendry", "David R. Smith", "Ulf Leonhardt"], "work on metamaterials and transformation optics", METAMATERIALS_RATIONALE),
    "pred-010": (["Charles L. Kane", "Eugene J. Mele", "Laurens W. Molenkamp"], "work on topological insulators", TOPOLOGICAL_RATIONALE),
    "pred-011": (["Michael Berry", "Yakir Aharonov"], "revealing how geometric and electromagnetic effects influence quantum phases", QUANTUM_RATIONALE),
    "pred-012": (["Michael Berry", "Yakir Aharonov"], "revealing how quantum particles acquire phases that produce measurable effects", QUANTUM_RATIONALE),
    "pred-013": (["Charles L. Kane", "Eugene J. Mele", "Laurens W. Molenkamp"], "work on topological insulators", TOPOLOGICAL_RATIONALE),
    "pred-014": (["Michael Berry", "Yakir Aharonov"], "revealing how geometry and electromagnetic potentials shape quantum behavior", QUANTUM_RATIONALE),
    "pred-015": (["Michael Berry", "Yakir Aharonov"], "revealing how quantum phases shape physical phenomena", QUANTUM_RATIONALE),
    "pred-016": (["Michael Berry", "Yakir Aharonov"], "work on geometric phases in quantum physics", QUANTUM_RATIONALE),
    "pred-017": (["Michael Berry", "Yakir Aharonov"], "discoveries showing how quantum particles acquire phases that produce measurable effects", QUANTUM_RATIONALE),
    "pred-018": (["John Pendry", "David R. Smith"], "work on metamaterials and transformation optics", METAMATERIALS_RATIONALE),
    "pred-019": (["Michael Berry", "Yakir Aharonov"], "work on quantum phases, particularly the Berry phase and the Aharonov–Bohm effect", QUANTUM_RATIONALE),
    "pred-020": (["Jun Ye", "Hidetoshi Katori"], "pioneering work on optical lattice clocks", CLOCK_RATIONALE),
    "pred-021": (["Ignacio Cirac", "Peter Zoller", "Immanuel Bloch"], "pioneering quantum simulation", "The work established how controlled atoms and ions can simulate quantum systems and paired foundational ideas with powerful experiments."),
    "pred-022": (["Michael Berry", "Yakir Aharonov"], "discoveries concerning quantum phases", QUANTUM_RATIONALE),
    "pred-023": (["John Pendry", "David R. Smith"], "pioneering metamaterials and negative refraction", METAMATERIALS_RATIONALE),
    "pred-024": (["John Pendry", "David R. Smith"], "pioneering metamaterials", METAMATERIALS_RATIONALE),
    "pred-025": (["Charles L. Kane", "Eugene J. Mele", "Laurens W. Molenkamp"], "prediction and experimental discovery of topological insulators", TOPOLOGICAL_RATIONALE),
    "pred-026": (["Hidetoshi Katori", "Jun Ye"], "work on optical lattice clocks", CLOCK_RATIONALE),
    "pred-027": (["Michael Berry", "Yakir Aharonov"], "discoveries concerning quantum phases, particularly the Berry phase and the Aharonov–Bohm effect", QUANTUM_RATIONALE),
    "pred-028": (["Michael Berry", "Yakir Aharonov"], "work on quantum phases and interference", QUANTUM_RATIONALE),
    "pred-029": (["Jun Ye", "Hidetoshi Katori"], "pioneering work on optical lattice clocks", CLOCK_RATIONALE),
    "pred-030": (["Charles Kane", "Eugene Mele", "Laurens Molenkamp"], "topological insulators", TOPOLOGICAL_RATIONALE),
    "pred-031": (["Charles L. Kane", "Eugene J. Mele", "Laurens W. Molenkamp"], "work on topological insulators and the quantum spin Hall effect", TOPOLOGICAL_RATIONALE),
    "pred-032": (["Michael Berry", "Yakir Aharonov"], "discoveries concerning quantum phases", QUANTUM_RATIONALE),
    "pred-033": (["Jun Ye", "Hidetoshi Katori"], "pioneering optical lattice clocks", CLOCK_RATIONALE),
    "pred-034": (["Michael Berry", "Yakir Aharonov"], "discoveries concerning quantum phase, particularly the Berry phase and the Aharonov–Bohm effect", QUANTUM_RATIONALE),
    "pred-035": (["Charles L. Kane", "Eugene J. Mele", "Laurens W. Molenkamp"], "work on topological insulators and the quantum spin Hall effect", TOPOLOGICAL_RATIONALE),
    "pred-036": (["Michael Berry", "Yakir Aharonov"], "work on geometric and topological phases in quantum physics", QUANTUM_RATIONALE),
    "pred-037": (["Charles L. Kane", "Eugene J. Mele", "Laurens W. Molenkamp"], "predicting and experimentally demonstrating the quantum spin Hall effect", TOPOLOGICAL_RATIONALE),
    "pred-038": (["Charles L. Kane", "Eugene J. Mele", "Laurens W. Molenkamp"], "work on topological insulators", TOPOLOGICAL_RATIONALE),
    "pred-039": (["Michael Berry", "Yakir Aharonov"], "work on quantum phases", QUANTUM_RATIONALE),
    "pred-040": (["Michael Berry", "Yakir Aharonov"], "work on quantum phases, particularly the Berry phase and the Aharonov–Bohm effect", QUANTUM_RATIONALE),
    "pred-041": (["Pablo Jarillo-Herrero", "Allan MacDonald", "Rafi Bistritzer"], "work on magic-angle graphene", "The theoretical prediction and 2018 experimental demonstration opened a major field based on controlling electronic properties through twist angle."),
    "pred-042": (["Yakir Aharonov", "Michael Berry"], "foundational discoveries concerning quantum phases—the Aharonov–Bohm effect and Berry phase", QUANTUM_RATIONALE),
    "pred-043": (["Jun Ye", "Hidetoshi Katori"], "pioneering work on optical lattice clocks", CLOCK_RATIONALE),
    "pred-044": (["Charles L. Kane", "Eugene J. Mele", "Laurens W. Molenkamp"], "work on topological insulators and the quantum spin Hall effect", TOPOLOGICAL_RATIONALE),
    "pred-045": (["Michael Berry", "Yakir Aharonov"], "work on quantum phases", QUANTUM_RATIONALE),
    "pred-046": (["John Pendry", "David R. Smith"], "pioneering electromagnetic metamaterials and negative refraction", METAMATERIALS_RATIONALE),
    "pred-047": (["Yakir Aharonov", "Michael Berry"], "the Aharonov–Bohm effect and geometric phases in quantum mechanics", QUANTUM_RATIONALE),
    "pred-048": (["Charles L. Kane", "Eugene J. Mele", "Laurens W. Molenkamp"], "work on topological insulators", TOPOLOGICAL_RATIONALE),
    "pred-049": (["Charles L. Kane", "Eugene J. Mele", "Laurens W. Molenkamp"], "work on topological insulators", TOPOLOGICAL_RATIONALE),
    "pred-050": (["John Pendry", "David R. Smith"], "pioneering metamaterials, including negative refraction", METAMATERIALS_RATIONALE),
    "pred-051": (["Michael Berry", "Yakir Aharonov"], "discoveries involving quantum phases", QUANTUM_RATIONALE),
    "pred-052": (["John Pendry", "David Smith", "Ulf Leonhardt"], "work on metamaterials and transformation optics", METAMATERIALS_RATIONALE),
    "pred-053": (["Jun Ye", "Hidetoshi Katori"], "pioneering optical lattice clocks", CLOCK_RATIONALE),
    "pred-054": (["John Pendry", "David Smith", "Ulf Leonhardt"], "work on metamaterials and transformation optics", METAMATERIALS_RATIONALE),
    "pred-055": (["Jun Ye", "Hidetoshi Katori"], "pioneering optical lattice clocks", CLOCK_RATIONALE),
    "pred-056": (["John Pendry", "David R. Smith", "Nader Engheta"], "pioneering metamaterials", METAMATERIALS_RATIONALE),
    "pred-057": (["John Pendry", "David R. Smith"], "work on metamaterials and negative refraction", METAMATERIALS_RATIONALE),
    "pred-058": (["Yakir Aharonov", "Michael Berry"], "discoveries revealing how phase and geometry shape quantum mechanics", QUANTUM_RATIONALE),
    "pred-059": (["Yakir Aharonov", "Michael Berry"], "work on quantum phases, particularly the Aharonov–Bohm effect and the Berry phase", QUANTUM_RATIONALE),
    "pred-060": (["Michael Berry", "Yakir Aharonov"], "work on quantum phases", QUANTUM_RATIONALE),
}

AMBIGUITIES = [
    {
        "prediction_id": "pred-018",
        "note": "The response says the named pair might share with an unnamed third researcher; only the two named people are transcribed.",
    },
    {
        "prediction_id": "pred-032",
        "note": "The opening primary pick says Michael Berry may share with Yakir Aharonov, while the closing sentence calls Berry the single-name bet; both opening-slate names are retained.",
    },
    {
        "prediction_id": "pred-041",
        "note": "The opening primary pick names Pablo Jarillo-Herrero with two potential co-recipients, while the closing sentence chooses Jarillo-Herrero if limited to one name; all opening-slate names are retained.",
    },
    {
        "prediction_id": "pred-054",
        "note": "The opening primary pick names John Pendry with two potential co-recipients, while the closing sentence chooses Pendry if limited to one name; all opening-slate names are retained.",
    },
]

HEDGED_PRIMARY_SLATES = [
    "pred-002",
    "pred-005",
    "pred-006",
    "pred-007",
    "pred-009",
    "pred-015",
    "pred-017",
    "pred-018",
    "pred-019",
    "pred-022",
    "pred-024",
    "pred-030",
    "pred-032",
    "pred-041",
    "pred-050",
    "pred-051",
    "pred-052",
    "pred-054",
    "pred-056",
    "pred-057",
]


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def reasoning_tokens(runtime_path: Path) -> int | None:
    found = None
    for line in runtime_path.read_text(encoding="utf-8").splitlines():
        event = json.loads(line)
        if event.get("type") == "turn.completed":
            found = event.get("usage", {}).get("reasoning_output_tokens")
    return found


def write_results() -> None:
    expected = {f"pred-{index:03d}" for index in range(1, 61)}
    if set(TRANSCRIPTIONS) != expected:
        raise ValueError("transcription map must contain pred-001 through pred-060 exactly")

    configuration_ids: dict[tuple[str, ...], list[str]] = defaultdict(list)
    name_ids: dict[str, list[str]] = defaultdict(list)

    for prediction_id in sorted(TRANSCRIPTIONS):
        names, description, rationale = TRANSCRIPTIONS[prediction_id]
        prediction_dir = ARM_ROOT / prediction_id
        response = (prediction_dir / "response.txt").read_bytes()
        execution = load_json(prediction_dir / "execution.json")
        usage = execution["usage"]
        result = {
            "schema_version": 1,
            "arm_id": "physics-oneshot-gpt-6.1-sol-high-v1",
            "prediction_id": prediction_id,
            "prompt_version": "physics-oneshot-gpt-6.1-sol-v1",
            "execution": {
                "provider": "openai",
                "interface": "codex-cli-0.159.0",
                "requested_model": "gpt-6.1-sol",
                "returned_model": "gpt-6.1-sol",
                "reasoning_effort": "high",
                "request_id": execution["thread_id"],
                "response_id": None,
                "created_at_utc": execution["completed_at_utc"],
                "usage": {
                    "input_tokens": usage["input_tokens"],
                    "output_tokens": usage["output_tokens"],
                    "reasoning_tokens": reasoning_tokens(prediction_dir / "runtime.jsonl"),
                    "total_tokens": usage["total_tokens"],
                },
            },
            "response_file": "response.txt",
            "response_sha256": hashlib.sha256(response).hexdigest(),
            "prize_configuration": {
                "outcome": "award",
                "prize_parts": [
                    {"credited_names": names, "description": description},
                ],
            },
            "rationale": rationale,
        }
        (prediction_dir / "result.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        configuration_ids[tuple(sorted(names))].append(prediction_id)
        for name in names:
            name_ids[name].append(prediction_id)

    configurations = [
        {
            "credited_names": list(names),
            "count": len(prediction_ids),
            "prediction_ids": prediction_ids,
        }
        for names, prediction_ids in sorted(
            configuration_ids.items(), key=lambda item: (-len(item[1]), item[0])
        )
    ]
    names = [
        {"name": name, "count": len(prediction_ids), "prediction_ids": prediction_ids}
        for name, prediction_ids in sorted(
            name_ids.items(), key=lambda item: (-len(item[1]), item[0])
        )
    ]
    summary = {
        "schema_version": 1,
        "arm_id": "physics-oneshot-gpt-6.1-sol-high-v1",
        "record_type": "post_hoc_transcription_summary",
        "source_record_count": 60,
        "method": (
            "Post-hoc clerical transcription of the primary predicted prize "
            "configuration in each saved verbatim response; no new prediction "
            "or model call was made. Alternatives and runner-ups were excluded. "
            "Names retain the exact spelling used in each primary-pick sentence."
        ),
        "primary_slate_rule": (
            "When the primary-pick sentence said a named lead might, could, or "
            "would likely share with named co-recipients, all names in that "
            "opening primary slate were transcribed; unnamed possible recipients "
            "were not inferred."
        ),
        "hedged_primary_slate_prediction_ids": HEDGED_PRIMARY_SLATES,
        "configuration_counts": configurations,
        "name_counts": names,
        "transcription_ambiguities": AMBIGUITIES,
    }
    (ARM_ROOT / "posthoc_transcription_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    with (ARM_ROOT / "posthoc_transcription_summary.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["summary_level", "label", "count", "prediction_ids"])
        for item in configurations:
            writer.writerow(
                [
                    "configuration",
                    " + ".join(item["credited_names"]),
                    item["count"],
                    ";".join(item["prediction_ids"]),
                ]
            )
        for item in names:
            writer.writerow(
                ["name", item["name"], item["count"], ";".join(item["prediction_ids"])]
            )


if __name__ == "__main__":
    write_results()
