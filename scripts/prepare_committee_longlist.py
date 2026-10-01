"""Prepare deterministic, blinded opening packets for complete physics runs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from validate_candidate_merge import check_csv, fail, validate


DEFAULT_SEED_LABEL = "physics-committee-opening-v1"
ALGORITHM = "sha256-sort-v1"


def encode_json(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def canonical_payload(candidate: dict) -> dict:
    names = candidate["nominees"] + candidate["other_names"]
    if len(names) != len(set(names)):
        fail(f"duplicate credited name in {candidate['candidate_id']}")
    return {
        "discovery": candidate["discovery"],
        "subfield": candidate["subfield"],
        "credited_names": sorted(names, key=lambda name: (name.casefold(), name)),
    }


def prepare(output: dict, seed_label: str) -> tuple[dict, dict]:
    """Hash public content, never source counts or frequency-derived ordering."""
    run_seed = f"{seed_label}:{output['list_id']}/run-{output['run']}"
    entries = []
    for candidate in output["candidates"]:
        payload = canonical_payload(candidate)
        serialized = json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        digest = hashlib.sha256(
            (run_seed + "\0" + serialized).encode("utf-8")
        ).hexdigest()
        entries.append((digest, serialized, candidate["candidate_id"], payload))
    # IDs are used solely as a final tie breaker for identical public payloads.
    entries.sort(key=lambda entry: entry[:3])
    longlist = {"schema_version": 1, "candidates": []}
    crosswalk = {}
    for index, (_, _, candidate_id, payload) in enumerate(entries, start=1):
        ballot_id = f"B{index:03d}"
        longlist["candidates"].append({"ballot_id": ballot_id, **payload})
        crosswalk[ballot_id] = candidate_id
    ballot_map = {
        "schema_version": 1,
        "list_id": output["list_id"],
        "run": output["run"],
        "shuffle": {"algorithm": ALGORITHM, "seed_label": run_seed},
        "ballot_to_candidate": crosswalk,
    }
    validate_packet(output, longlist, ballot_map)
    return longlist, ballot_map


def validate_packet(output: dict, longlist: dict, ballot_map: dict) -> None:
    sources = {c["candidate_id"]: c for c in output["candidates"]}
    if len(sources) != len(output["candidates"]):
        fail("duplicate source candidate IDs")
    if len(sources) < 8:
        fail("opening rankings require at least eight candidates")
    entries = longlist["candidates"]
    mapping = ballot_map["ballot_to_candidate"]
    ballots = [entry["ballot_id"] for entry in entries]
    expected_ballots = [f"B{i:03d}" for i in range(1, len(sources) + 1)]
    if ballots != expected_ballots or list(mapping) != expected_ballots:
        fail("packet ballot IDs must be consecutive and cover every candidate")
    if len(set(mapping.values())) != len(sources) or set(mapping.values()) != set(sources):
        fail("packet crosswalk is not bijective")
    for entry in entries:
        payload = canonical_payload(sources[mapping[entry["ballot_id"]]])
        if entry != {"ballot_id": entry["ballot_id"], **payload}:
            fail("packet entry differs from its blinded source payload")
        if set(entry) != {"ballot_id", "discovery", "subfield", "credited_names"}:
            fail("packet exposes undocumented fields")


def process(run_dir: Path, check: bool) -> None:
    output, rows = validate(run_dir)
    check_csv(run_dir, rows)
    longlist, ballot_map = prepare(output, DEFAULT_SEED_LABEL)
    # Input array order must not determine the shuffle or credited-name order.
    reversed_input = {
        **output,
        "candidates": [
            {
                **candidate,
                "nominees": list(reversed(candidate["nominees"])),
                "other_names": list(reversed(candidate["other_names"])),
            }
            for candidate in reversed(output["candidates"])
        ],
    }
    if prepare(reversed_input, DEFAULT_SEED_LABEL) != (longlist, ballot_map):
        fail("packet generation is not deterministic under candidate reordering")
    directory = run_dir / "committee"
    packets = {"longlist.json": longlist, "ballot_map.json": ballot_map}
    if check:
        for filename, value in packets.items():
            path = directory / filename
            try:
                actual = path.read_text(encoding="utf-8")
            except OSError as exc:
                fail(f"cannot read {path}: {exc}")
            if actual != encode_json(value):
                fail(f"{path} differs from the deterministic expected packet")
    else:
        opening_dir = directory / "opening"
        if opening_dir.exists() and any(opening_dir.glob("*.json")):
            fail(f"refusing to replace dispatched packets with ballots in {opening_dir}")
        directory.mkdir(parents=True, exist_ok=True)
        for filename, value in packets.items():
            (directory / filename).write_text(encode_json(value), encoding="utf-8")
    action = "checked" if check else "prepared"
    print(f"OK: {run_dir}: {action} {len(longlist['candidates'])} blinded candidates")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dirs", nargs="+", type=Path)
    parser.add_argument("--check", action="store_true", help="verify packets without writing")
    args = parser.parse_args()
    for run_dir in args.run_dirs:
        process(run_dir, args.check)


if __name__ == "__main__":
    main()
