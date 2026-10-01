"""GPT-5.6 Terra physics committee simulations.

This is a model-locked adapter around the shared multi-simulation committee
implementation.  It deliberately accepts only simulation directories shaped
as::

    results/physics/<list-id>/run-<n>/committee/gpt-5.6-terra/sim-XX

and pins every simulation to OpenAI ``gpt-5.6-terra`` with ``high`` reasoning.
The legacy flat ``committee/`` GPT-6.1 Sol artifacts are therefore outside this
tool's namespace and cannot be overwritten by it.

Usage (SIM has the shape above):
  python3 scripts/terra_committee.py prepare SIM...
  python3 scripts/terra_committee.py check-member {opening,round1,round2,final} SIM MEMBER
  python3 scripts/terra_committee.py check-chair SIM
  python3 scripts/terra_committee.py shortlist SIM...
  python3 scripts/terra_committee.py slate SIM...
  python3 scripts/terra_committee.py tally SIM...
  python3 scripts/terra_committee.py validate SIM...
  python3 scripts/terra_committee.py progress

The shared implementation currently lives in ``claude_committee.py`` because
that was the first multi-simulation cohort added.  All cohort-sensitive globals
and path parsing are replaced below before any operation runs.
"""

from __future__ import annotations

import argparse
import subprocess
from collections import Counter
from pathlib import Path

import claude_committee as shared


PROVIDER = "openai"
MODEL = "gpt-5.6-terra"
EFFORT = "high"
COHORT = MODEL
SEED_PREFIX = "physics-committee-gpt-5.6-terra-v1"
PROMPTS = {
    "opening": "prompts/physics_committee_terra_opening_v1.md",
    "round1": "prompts/physics_committee_terra_round1_v1.md",
    "chair": "prompts/physics_committee_terra_chair_summary_v1.md",
    "round2": "prompts/physics_committee_terra_round2_v1.md",
    "final": "prompts/physics_committee_terra_final_ballot_v1.md",
}
ROOT = Path(__file__).resolve().parent.parent
LISTS = ("claude-opus-5-5", "gpt-6-sol")
RUNS = range(1, 7)
SIMS = tuple(f"sim-{index:02d}" for index in range(1, 6))
MANIFEST = ROOT / "results" / "physics" / "terra_committee_progress.json"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def identity(sim: Path) -> tuple[Path, str, int, str]:
    """Return the nomination run identity after enforcing the Terra namespace."""
    sim = sim.resolve()
    if sim.parent.name != COHORT or sim.parent.parent.name != "committee":
        fail(f"not a {MODEL} simulation directory: {sim}")
    run_dir = sim.parents[2]
    if not run_dir.name.startswith("run-"):
        fail(f"run directory must be named run-N: {run_dir}")
    try:
        run = int(run_dir.name.removeprefix("run-"))
    except ValueError:
        fail(f"run directory must be named run-N: {run_dir}")
    if run not in RUNS:
        fail(f"nomination run must be run-1..run-6: {run_dir}")
    if run_dir.parent.name not in LISTS:
        fail(f"unexpected nomination list: {run_dir.parent.name}")
    if sim.name not in SIMS:
        fail(f"simulation directory must be sim-01..sim-05: {sim}")
    return run_dir, run_dir.parent.name, run, sim.name


def seed_label(sim: Path) -> str:
    _, list_id, run, sim_id = identity(sim)
    return f"{SEED_PREFIX}:{list_id}/run-{run}/{sim_id}"


def assert_metadata(sim: Path) -> None:
    metadata = shared.load_json(sim / "metadata.json")
    expected = {
        "committee_provider": PROVIDER,
        "committee_model": MODEL,
        "reasoning_effort": EFFORT,
    }
    for key, value in expected.items():
        if metadata.get(key) != value:
            fail(f"{sim / 'metadata.json'}: {key} must be {value!r}")


# Install the Terra cohort configuration into the shared implementation.  Its
# functions resolve these names at call time, so derived-file logic stays
# identical across the two full-committee cohorts.
shared.PROVIDER = PROVIDER
shared.DEFAULT_MODEL = MODEL
shared.DEFAULT_EFFORT = EFFORT
shared.SEED_PREFIX = SEED_PREFIX
shared.PROMPTS = PROMPTS
shared.LISTS = LISTS
shared.RUNS = RUNS
shared.SIMS = list(SIMS)
shared.MANIFEST = MANIFEST
shared.identity = identity
shared.seed_label = seed_label

_shared_build_packet = shared.build_packet


def build_packet(
    sim: Path,
    model: str | None = None,
    effort: str | None = None,
) -> tuple[dict, dict, dict]:
    """Build the shared packet while refusing non-Terra execution metadata."""
    if model not in (None, MODEL):
        fail(f"model is fixed at {MODEL!r}; got {model!r}")
    if effort not in (None, EFFORT):
        fail(f"reasoning effort is fixed at {EFFORT!r}; got {effort!r}")
    return _shared_build_packet(sim, MODEL, EFFORT)


shared.build_packet = build_packet

_shared_check_packet = shared.check_packet


def prepare(sim: Path) -> None:
    shared.prepare(sim, MODEL, EFFORT)
    assert_metadata(sim)


def check_packet(sim: Path) -> dict:
    value = _shared_check_packet(sim)
    assert_metadata(sim)
    return value


shared.check_packet = check_packet

_shared_build_decision = shared.build_decision


def build_decision(sim: Path) -> dict:
    """Build a decision that records the exact committee provider as well."""
    check_packet(sim)
    value = _shared_build_decision(sim)
    return {
        "schema_version": value["schema_version"],
        "list_id": value["list_id"],
        "run": value["run"],
        "simulation_id": value["simulation_id"],
        "committee_provider": PROVIDER,
        "committee_model": value["committee_model"],
        "reasoning_effort": value["reasoning_effort"],
        "rule": value["rule"],
        "rounds": value["rounds"],
        "winner": value["winner"],
    }


shared.build_decision = build_decision


def validate_sim(sim: Path) -> dict:
    decision = shared.validate_sim(sim)
    assert_metadata(sim)
    if decision.get("committee_provider") != PROVIDER:
        fail(f"{sim / 'decision.json'}: committee_provider must be {PROVIDER!r}")
    if decision.get("committee_model") != MODEL:
        fail(f"{sim / 'decision.json'}: committee_model must be {MODEL!r}")
    if decision.get("reasoning_effort") != EFFORT:
        fail(f"{sim / 'decision.json'}: reasoning_effort must be {EFFORT!r}")
    return decision


def progress() -> None:
    manifest = shared.load_json(MANIFEST) if MANIFEST.exists() else {}
    simulations = manifest.get("simulations", {})
    for list_id in LISTS:
        for run in RUNS:
            for sim_id in SIMS:
                key = f"{list_id}/run-{run}/{sim_id}"
                sim = (
                    ROOT
                    / "results"
                    / "physics"
                    / list_id
                    / f"run-{run}"
                    / "committee"
                    / COHORT
                    / sim_id
                )
                entry = simulations.get(key, {"status": "pending", "commit": None})
                if sim.exists() and (sim / "decision.json").exists():
                    try:
                        decision = validate_sim(sim)
                    except SystemExit as exc:
                        entry = {"status": "failed", "commit": None, "error": str(exc)}
                    else:
                        rel = sim.relative_to(ROOT)
                        tracked = subprocess.run(
                            ["git", "log", "-1", "--format=%h", "--", str(rel / "decision.json")],
                            cwd=ROOT,
                            capture_output=True,
                            text=True,
                            check=False,
                        ).stdout.strip()
                        entry = {
                            "status": "complete",
                            "committee_provider": PROVIDER,
                            "committee_model": MODEL,
                            "reasoning_effort": EFFORT,
                            "commit": tracked or entry.get("commit"),
                            "winner": [
                                {
                                    "candidate_id": part["candidate_id"],
                                    "laureates": part["laureates"],
                                }
                                for part in decision["winner"]["prize_parts"]
                            ],
                        }
                elif sim.exists() and entry.get("status") != "failed":
                    entry = {
                        "status": "running",
                        "committee_provider": PROVIDER,
                        "committee_model": MODEL,
                        "reasoning_effort": EFFORT,
                        "commit": None,
                    }
                simulations[key] = entry
    counts = Counter(entry["status"] for entry in simulations.values())
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(
        shared.encode(
            {
                "schema_version": 1,
                "committee_provider": PROVIDER,
                "committee_model": MODEL,
                "reasoning_effort": EFFORT,
                "totals": dict(sorted(counts.items())),
                "simulations": simulations,
            }
        ),
        encoding="utf-8",
    )
    print(f"OK: {MANIFEST.relative_to(ROOT)}: {dict(sorted(counts.items()))}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "shortlist", "slate", "tally", "validate"):
        command = sub.add_parser(name)
        command.add_argument("sims", nargs="+", type=Path)
        if name in ("shortlist", "slate", "tally"):
            command.add_argument("--check", action="store_true")
    member = sub.add_parser("check-member")
    member.add_argument("stage", choices=("opening", "round1", "round2", "final"))
    member.add_argument("sim", type=Path)
    member.add_argument("member", choices=sorted(shared.EXPECTED_MEMBERS))
    chair = sub.add_parser("check-chair")
    chair.add_argument("sim", type=Path)
    sub.add_parser("progress")
    args = parser.parse_args()

    if args.command == "prepare":
        for sim in args.sims:
            prepare(sim)
    elif args.command == "check-member":
        check_packet(args.sim)
        if args.stage == "opening":
            shared.check_opening(args.sim, args.member)
        elif args.stage == "final":
            shared.check_final(args.sim, args.member)
        else:
            shared.check_round(args.sim, int(args.stage[-1]), args.member)
        print(f"OK: {args.stage}/{args.member}")
    elif args.command == "check-chair":
        check_packet(args.sim)
        shared.check_chair(args.sim)
        print("OK: chair summary")
    elif args.command == "shortlist":
        for sim in args.sims:
            value = shared.build_shortlist(sim)
            shared.write_or_check(
                sim / "shortlist.json", value, args.check, guard=sim / "round1"
            )
            print(f"OK: {sim}: {len(value['shortlist'])} shortlisted")
    elif args.command == "slate":
        for sim in args.sims:
            check_packet(sim)
            value = shared.build_slate(sim)
            shared.write_or_check(
                sim / "proposal_slate.json",
                value,
                args.check,
                guard=sim / "final_ballots",
            )
            print(f"OK: {sim}: {len(value['proposals'])} proposals")
    elif args.command == "tally":
        for sim in args.sims:
            check_packet(sim)
            value = build_decision(sim)
            shared.write_or_check(sim / "decision.json", value, args.check)
            print(f"OK: {sim}: winner {value['winner']['proposal_id']}")
    elif args.command == "validate":
        for sim in args.sims:
            decision = validate_sim(sim)
            print(f"OK: {sim}: complete; winner {decision['winner']['proposal_id']}")
    elif args.command == "progress":
        progress()


if __name__ == "__main__":
    main()
