"""Validate a phase-2 physics candidate consolidation and optionally write CSV."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


EXPECTED_CONSOLIDATION = {
    "model": "gpt-6.1-sol",
    "reasoning_effort": "high",
    "prompt": "prompts/physics_merge_v1.md",
}
CSV_FIELDS = [
    "candidate_id",
    "discovery",
    "nominees",
    "other_names",
    "subfield",
    "n_nominations",
    "nominators",
]


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read valid JSON from {path}: {exc}")


def validate_source(path: Path) -> dict:
    data = load_json(path)
    required = {"nominator", "discovery", "nominees", "subfield", "motivation"}
    if not isinstance(data, dict) or not required.issubset(data):
        fail(f"invalid nomination structure: {path}")
    for field in ("nominator", "discovery", "subfield", "motivation"):
        if not isinstance(data[field], str) or not data[field]:
            fail(f"{field} must be a non-empty string in {path}")
    if not isinstance(data["nominees"], list) or not 1 <= len(data["nominees"]) <= 3:
        fail(f"nominees must contain one to three entries: {path}")
    for nominee in data["nominees"]:
        if not isinstance(nominee, dict) or set(nominee) != {"name", "affiliation"}:
            fail(f"each nominee must contain only name and affiliation: {path}")
        for field in ("name", "affiliation"):
            if not isinstance(nominee[field], str) or not nominee[field]:
                fail(f"nominee {field} must be a non-empty string: {path}")
    return data


def candidate_row(candidate: dict, run_dir: Path) -> dict[str, str | int]:
    slugs = []
    for relative in candidate["nomination_files"]:
        source = run_dir / relative
        slugs.append(load_json(source)["nominator"])
    return {
        "candidate_id": candidate["candidate_id"],
        "discovery": candidate["discovery"],
        "nominees": "; ".join(candidate["nominees"]),
        "other_names": "; ".join(candidate["other_names"]),
        "subfield": candidate["subfield"],
        "n_nominations": candidate["n_nominations"],
        "nominators": "; ".join(slugs),
    }


def validate(run_dir: Path) -> tuple[dict, list[dict[str, str | int]]]:
    nominations_dir = run_dir / "nominations"
    source_paths = sorted(nominations_dir.glob("*.json"))
    if len(source_paths) != 100:
        fail(f"{run_dir} has {len(source_paths)} nominations; expected 100")
    source_data = {
        f"nominations/{source.name}": validate_source(source) for source in source_paths
    }

    output_path = run_dir / "candidates.json"
    output = load_json(output_path)
    expected_top = {
        "schema_version",
        "list_id",
        "run",
        "source_nominations",
        "name_normalizations",
        "consolidation",
        "candidates",
    }
    if set(output) != expected_top:
        fail(f"{output_path} keys differ from the documented schema")
    if output["schema_version"] != 1:
        fail("schema_version must be 1")
    if output["list_id"] != run_dir.parent.name:
        fail("list_id does not match the list directory")
    try:
        expected_run = int(run_dir.name.removeprefix("run-"))
    except ValueError:
        fail(f"run directory must be named run-N: {run_dir}")
    if output["run"] != expected_run:
        fail("run value does not match the run directory")
    if output["source_nominations"] != 100:
        fail("source_nominations must be 100")
    normalizations = output["name_normalizations"]
    if not isinstance(normalizations, dict):
        fail("name_normalizations must be an object")
    alias_to_canonical: dict[str, str] = {}
    for canonical, aliases in normalizations.items():
        if not isinstance(canonical, str) or not canonical:
            fail("name_normalizations has an invalid canonical name")
        if not isinstance(aliases, list) or not aliases:
            fail(f"name_normalizations[{canonical!r}] must be a non-empty list")
        for alias in aliases:
            if not isinstance(alias, str) or not alias or alias == canonical:
                fail(f"invalid alias for {canonical!r}")
            if alias in alias_to_canonical:
                fail(f"source spelling {alias!r} is normalized more than once")
            alias_to_canonical[alias] = canonical
    if output["consolidation"] != EXPECTED_CONSOLIDATION:
        fail("consolidation metadata does not match the documented settings")
    if not isinstance(output["candidates"], list) or not output["candidates"]:
        fail("candidates must be a non-empty list")

    expected_files = {f"nominations/{path.name}" for path in source_paths}
    seen_files: list[str] = []
    used_aliases: set[str] = set()
    previous_sort_key = None
    rows = []
    for index, candidate in enumerate(output["candidates"], start=1):
        required = {
            "candidate_id",
            "discovery",
            "nominees",
            "other_names",
            "subfield",
            "n_nominations",
            "nomination_files",
        }
        if not isinstance(candidate, dict) or set(candidate) != required:
            fail(f"candidate {index} keys differ from the documented schema")
        expected_id = f"c{index:02d}"
        if candidate["candidate_id"] != expected_id:
            fail(f"candidate {index} must have ID {expected_id}")
        if not isinstance(candidate["discovery"], str) or not candidate["discovery"]:
            fail(f"{expected_id} has no discovery title")
        if not isinstance(candidate["subfield"], str) or not candidate["subfield"]:
            fail(f"{expected_id} has no subfield")
        if not isinstance(candidate["nominees"], list) or not 1 <= len(candidate["nominees"]) <= 3:
            fail(f"{expected_id} must have one to three canonical nominees")
        if not all(isinstance(name, str) and name for name in candidate["nominees"]):
            fail(f"{expected_id} has an invalid canonical nominee")
        if not isinstance(candidate["other_names"], list) or not all(
            isinstance(name, str) and name for name in candidate["other_names"]
        ):
            fail(f"{expected_id} has invalid other_names")
        files = candidate["nomination_files"]
        if not isinstance(files, list) or not files:
            fail(f"{expected_id} has no source nominations")
        if files != sorted(files):
            fail(f"{expected_id} nomination_files must be sorted")
        if candidate["n_nominations"] != len(files):
            fail(f"{expected_id} count does not equal its source-file count")
        name_counts: dict[str, int] = {}
        first_seen: dict[str, int] = {}
        position = 0
        for relative in files:
            for nominee in source_data[relative]["nominees"]:
                raw_name = nominee["name"]
                canonical_name = alias_to_canonical.get(raw_name, raw_name)
                if raw_name in alias_to_canonical:
                    used_aliases.add(raw_name)
                name_counts[canonical_name] = name_counts.get(canonical_name, 0) + 1
                first_seen.setdefault(canonical_name, position)
                position += 1
        expected_names = sorted(
            name_counts,
            key=lambda name: (-name_counts[name], first_seen[name]),
        )
        actual_names = candidate["nominees"] + candidate["other_names"]
        if actual_names != expected_names:
            fail(
                f"{expected_id} nominee ordering/preservation differs from sources: "
                f"expected {expected_names}, got {actual_names}"
            )
        sort_key = (-candidate["n_nominations"], candidate["discovery"].casefold())
        if previous_sort_key is not None and sort_key < previous_sort_key:
            fail("candidates are not sorted by count then discovery")
        previous_sort_key = sort_key
        seen_files.extend(files)
        rows.append(candidate_row(candidate, run_dir))

    if len(seen_files) != len(set(seen_files)):
        fail("at least one source nomination is assigned more than once")
    unknown = set(seen_files) - expected_files
    missing = expected_files - set(seen_files)
    if unknown:
        fail(f"unknown source nominations: {sorted(unknown)}")
    if missing:
        fail(f"unassigned source nominations: {sorted(missing)}")
    unused_aliases = set(alias_to_canonical) - used_aliases
    if unused_aliases:
        fail(f"unused source-name normalizations: {sorted(unused_aliases)}")
    return output, rows


def write_csv(run_dir: Path, rows: list[dict[str, str | int]]) -> None:
    output_path = run_dir / "candidates.csv"
    with output_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def check_csv(run_dir: Path, rows: list[dict[str, str | int]]) -> None:
    output_path = run_dir / "candidates.csv"
    if not output_path.exists():
        fail(f"missing {output_path}; use --write-csv")
    with output_path.open(newline="") as handle:
        actual = list(csv.DictReader(handle))
    expected = [{key: str(value) for key, value in row.items()} for row in rows]
    if actual != expected:
        fail(f"{output_path} does not match candidates.json; use --write-csv")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--write-csv", action="store_true")
    args = parser.parse_args()

    output, rows = validate(args.run_dir)
    if args.write_csv:
        write_csv(args.run_dir, rows)
    check_csv(args.run_dir, rows)
    print(
        f"OK: {args.run_dir}: {output['source_nominations']} nominations -> "
        f"{len(output['candidates'])} candidates"
    )


if __name__ == "__main__":
    main()
