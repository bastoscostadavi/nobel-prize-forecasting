"""Validate one complete committee discussion round for physics runs."""

from __future__ import annotations

import argparse
from pathlib import Path

from build_committee_shortlist import build as build_shortlist
from validate_committee_opening import EXPECTED_MEMBERS, load_json, nonempty_text


EXPECTED_MODEL = "gpt-6.1-sol"
EXPECTED_EFFORT = "high"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def validate(run_dir: Path, round_number: int) -> None:
    shortlist_doc = load_json(run_dir / "committee" / "shortlist.json")
    if shortlist_doc != build_shortlist(run_dir):
        fail(f"shortlist is not the deterministic validated opening union: {run_dir}")
    shortlist = {item["ballot_id"]: item for item in shortlist_doc["shortlist"]}
    list_id = run_dir.parent.name
    run = int(run_dir.name.removeprefix("run-"))
    prompt = f"prompts/physics_committee_round{round_number}_v1.md"
    directory = run_dir / "committee" / f"round{round_number}"
    files = sorted(directory.glob("*.json"))
    members = {path.stem for path in files}
    if members != EXPECTED_MEMBERS:
        fail(f"round {round_number} members differ: missing={sorted(EXPECTED_MEMBERS-members)}, extra={sorted(members-EXPECTED_MEMBERS)}")

    for path in files:
        value = load_json(path)
        expected_top = {
            "schema_version", "list_id", "run", "member_id", "model",
            "reasoning_effort", "prompt", "preferred_configuration",
            "alternatives", "statement",
        }
        if set(value) != expected_top:
            fail(f"top-level schema differs: {path}")
        if type(value["schema_version"]) is not int or value["schema_version"] != 1:
            fail(f"schema_version differs: {path}")
        if value["list_id"] != list_id or type(value["run"]) is not int or value["run"] != run:
            fail(f"list/run metadata differs: {path}")
        if value["member_id"] != path.stem or path.stem not in EXPECTED_MEMBERS:
            fail(f"member metadata differs: {path}")
        if value["model"] != EXPECTED_MODEL or value["reasoning_effort"] != EXPECTED_EFFORT or value["prompt"] != prompt:
            fail(f"execution metadata differs: {path}")

        configuration = value["preferred_configuration"]
        if not isinstance(configuration, dict) or set(configuration) != {"prize_parts"}:
            fail(f"configuration schema differs: {path}")
        parts = configuration["prize_parts"]
        if not isinstance(parts, list) or not 1 <= len(parts) <= 2:
            fail(f"configuration must contain one or two parts: {path}")
        part_ids = set()
        people = set()
        for part in parts:
            if not isinstance(part, dict) or set(part) != {"ballot_id", "laureates", "citation"}:
                fail(f"prize-part schema differs: {path}")
            ballot_id = part["ballot_id"]
            if not isinstance(ballot_id, str):
                fail(f"prize-part ballot_id must be a string: {path}")
            if ballot_id not in shortlist or ballot_id in part_ids:
                fail(f"invalid or repeated prize part {ballot_id!r}: {path}")
            part_ids.add(ballot_id)
            laureates = part["laureates"]
            credited = set(shortlist[ballot_id]["credited_names"])
            if (
                not isinstance(laureates, list) or not 1 <= len(laureates) <= 3
                or not all(isinstance(name, str) for name in laureates)
                or len(laureates) != len(set(laureates))
                or not all(name in credited for name in laureates)
            ):
                fail(f"invalid laureates for {ballot_id}: {path}")
            people.update(laureates)
            nonempty_text(part["citation"], f"{path}:{ballot_id}:citation")
        if not 1 <= len(people) <= 3:
            fail(f"configuration must name one to three unique people total: {path}")

        alternatives = value["alternatives"]
        if (
            not isinstance(alternatives, list) or len(alternatives) > 2
            or not all(isinstance(item, str) for item in alternatives)
            or len(alternatives) != len(set(alternatives))
            or not all(item in shortlist and item not in part_ids for item in alternatives)
        ):
            fail(f"invalid alternatives: {path}")
        statement = value["statement"]
        if not isinstance(statement, dict) or set(statement) != {
            "case_for", "case_against", "responses", "uncertainties", "conflict_note"
        }:
            fail(f"statement schema differs: {path}")
        for key in ("case_for", "case_against", "conflict_note"):
            nonempty_text(statement[key], f"{path}:{key}")
        responses = statement["responses"]
        if not isinstance(responses, list) or len(responses) < 2:
            fail(f"at least two responses required: {path}")
        response_members = set()
        for response in responses:
            if not isinstance(response, dict) or set(response) != {"member_id", "point", "response"}:
                fail(f"response schema differs: {path}")
            member = response["member_id"]
            if not isinstance(member, str) or member not in EXPECTED_MEMBERS or member == path.stem:
                fail(f"invalid response member: {path}")
            response_members.add(member)
            nonempty_text(response["point"], f"{path}:response point")
            nonempty_text(response["response"], f"{path}:response text")
        if len(response_members) < 2:
            fail(f"responses must address at least two distinct members: {path}")
        uncertainties = statement["uncertainties"]
        if not isinstance(uncertainties, list) or not all(isinstance(item, str) and item.strip() for item in uncertainties):
            fail(f"uncertainties must be nonempty strings: {path}")
    print(f"OK: {run_dir}: round {round_number}: {len(files)} member statements")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("round_number", type=int, choices=(1, 2))
    parser.add_argument("run_dirs", nargs="+", type=Path)
    args = parser.parse_args()
    for run_dir in args.run_dirs:
        validate(run_dir, args.round_number)


if __name__ == "__main__":
    main()
