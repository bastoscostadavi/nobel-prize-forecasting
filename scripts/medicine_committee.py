"""Model-locked OpenAI Medicine committee coordinator.

Uses the Physics stage validators, shortlist, slate and instant-runoff rules in
an isolated shared module. All six simulated members vote; disclosed conflicts
are not adjudicated. This script does not make model requests.

prepare SIM... --candidates PATH [--exclude M042]
check-member {opening,round1,round2,final} SIM MEMBER
check-chair SIM
{shortlist,slate,tally,validate} SIM...
progress
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Never mutate the imported Physics/Claude coordinator's module globals.
_SPEC = importlib.util.spec_from_file_location(
    "_openai_medicine_shared", ROOT / "scripts" / "claude_committee.py"
)
assert _SPEC and _SPEC.loader
shared = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(shared)

PROVIDER = "openai"
MODEL = COHORT = "gpt-5.6-terra"
EFFORT = "high"
SEED_PREFIX = f"medicine-committee-{MODEL}-v1"
MEMBERS = {
    "el-manira-abdel", "linnarsson-sten", "perlmann-thomas",
    "sandberg-rickard", "svenningsson-per", "wahren-herlenius-marie",
}
CHAIR = "svenningsson-per"
PROMPTS = {
    "opening": "prompts/medicine_committee_terra_opening_v1.md",
    "round1": "prompts/medicine_committee_terra_round1_v1.md",
    "chair": "prompts/medicine_committee_terra_chair_summary_v1.md",
    "round2": "prompts/medicine_committee_terra_round2_v1.md",
    "final": "prompts/medicine_committee_terra_final_ballot_v1.md",
}
RESULTS = ROOT / "results" / "medicine" / "committee"
MANIFEST = RESULTS / "terra_progress.json"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        fail(f"cannot read {path}: {exc}")


def default_candidates() -> Path:
    """The reviewed Medicine source relocated by the candidate-list owner."""
    return ROOT / "agent-data/medicine/candidates/candidates.json"


def identity(sim: Path) -> tuple[Path, str, int, str]:
    sim = sim.resolve()
    if sim.parent != (RESULTS / COHORT).resolve():
        fail(f"not an OpenAI Medicine {COHORT} simulation directory: {sim}")
    if not re.fullmatch(r"sim-\d{2,}", sim.name) or int(sim.name[4:]) < 1:
        fail(f"simulation directory must be named sim-NN with N >= 1: {sim}")
    if sim.name != f"sim-{int(sim.name[4:]):02d}":
        fail(f"noncanonical simulation directory name: {sim}")
    metadata = sim / "metadata.json"
    list_id = shared.load_json(metadata).get("list_id") if metadata.exists() else "unprepared"
    return RESULTS, list_id, 1, sim.name


def load_candidates(path: Path) -> tuple[str, list[dict]]:
    data = shared.load_json(path)
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        fail(f"{path}: expected schema_version 1 object")
    if data.get("category", "medicine") != "medicine":
        fail(f"{path}: expected Medicine candidates")
    list_id = data.get("list_id")
    if not isinstance(list_id, str) or not list_id.strip() or list_id.strip() != list_id:
        fail(f"{path}: list_id must be a non-empty string")
    candidates = data.get("candidates")
    if not isinstance(candidates, list) or len(candidates) < 8:
        fail(f"{path}: needs at least eight candidates")
    if "candidate_count" in data and (type(data["candidate_count"]) is not int or data["candidate_count"] != len(candidates)):
        fail(f"{path}: candidate_count differs from candidates")
    seen = set()
    for candidate in candidates:
        if not isinstance(candidate, dict):
            fail(f"{path}: candidate must be an object")
        cid = candidate.get("candidate_id")
        if not isinstance(cid, str) or not cid.strip() or cid.strip() != cid or cid in seen:
            fail(f"{path}: missing or duplicate candidate_id {cid!r}")
        seen.add(cid)
        for key in ("discovery", "subfield"):
            if not isinstance(candidate.get(key), str) or not candidate[key].strip():
                fail(f"{path}: {cid} needs {key}")
        names = candidate.get("credited_names")
        if not isinstance(names, list) or not names or not all(
            isinstance(n, str) and n.strip() and n.strip() == n for n in names
        ) or len(set(names)) != len(names):
            fail(f"{path}: {cid} credited_names must be unique non-empty strings")
    return list_id, candidates


def profile_inputs() -> dict[str, dict[str, str]]:
    profiles = {}
    for member in sorted(MEMBERS):
        path = ROOT / f"agent-data/medicine/committee/{member}/profile.md"
        profiles[member] = {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
    return profiles


def prompt_inputs() -> dict[str, dict[str, str]]:
    return {stage: {"path": path, "sha256": sha256(ROOT / path)}
            for stage, path in PROMPTS.items()}


def _input_path(path: Path) -> Path:
    path = path.resolve()
    if not path.is_relative_to(ROOT.resolve()):
        fail(f"candidate input must be inside the repository: {path}")
    return path


def _shuffle(candidates: list[dict], list_id: str, sim_id: str) -> tuple[dict, dict]:
    label = f"{SEED_PREFIX}:{list_id}/{sim_id}"
    adapted = {"candidates": [{**c, "nominees": c["credited_names"], "other_names": []} for c in candidates]}
    entries = []
    for candidate in adapted["candidates"]:
        payload = shared.canonical_payload(candidate)
        serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256((label + "\0" + serialized).encode("utf-8")).hexdigest()
        entries.append((digest, serialized, candidate["candidate_id"], payload))
    entries.sort(key=lambda item: item[:3])
    longlist = {"schema_version": 1, "candidates": []}
    mapping = {}
    for index, (_, _, cid, payload) in enumerate(entries, start=1):
        ballot_id = f"B{index:03d}"
        longlist["candidates"].append({"ballot_id": ballot_id, **payload})
        mapping[ballot_id] = cid
    ballot_map = {
        "schema_version": 1, "list_id": list_id, "run": 1, "simulation_id": sim_id,
        "shuffle": {"algorithm": shared.ALGORITHM, "seed_label": label},
        "ballot_to_candidate": mapping,
    }
    shared.validate_packet(adapted, longlist, ballot_map)
    return longlist, ballot_map


def build_packet(sim: Path, candidates_path: Path | None = None,
                 excluded: list[str] | tuple[str, ...] | None = None) -> tuple[dict, dict, dict]:
    _, _, _, sim_id = identity(sim)
    saved = shared.load_json(sim / "metadata.json") if (sim / "metadata.json").exists() else {}
    if candidates_path is None:
        candidates_path = ROOT / saved["candidate_input"] if saved else default_candidates()
    path = _input_path(candidates_path)
    list_id, candidates = load_candidates(path)
    excluded = saved.get("excluded_candidates", []) if excluded is None else list(excluded)
    if not isinstance(excluded, list) or not all(isinstance(c, str) for c in excluded) or len(set(excluded)) != len(excluded):
        fail("excluded_candidates must be distinct candidate IDs")
    excluded = sorted(excluded)
    missing = set(excluded) - {c["candidate_id"] for c in candidates}
    if missing:
        fail(f"excluded IDs absent from {path}: {sorted(missing)}")
    selected = [c for c in candidates if c["candidate_id"] not in excluded]
    if len(selected) < 8:
        fail("exclusions leave fewer than eight candidates")
    longlist, ballot_map = _shuffle(selected, list_id, sim_id)
    reversed_source = [{**c, "credited_names": list(reversed(c["credited_names"]))} for c in reversed(selected)]
    if _shuffle(reversed_source, list_id, sim_id) != (longlist, ballot_map):
        fail("packet generation depends on source order")
    metadata = {
        "schema_version": 1, "category": "medicine", "committee_provider": PROVIDER,
        "committee_model": MODEL, "reasoning_effort": EFFORT, "list_id": list_id,
        "nomination_run": 1, "simulation_id": sim_id,
        "seed_label": ballot_map["shuffle"]["seed_label"],
        "candidate_input": str(path.relative_to(ROOT.resolve())), "candidate_input_sha256": sha256(path),
        "input_candidate_count": len(candidates), "candidate_count": len(selected),
        "excluded_candidates": excluded, "exclusion_policy": "only explicit prepare --exclude IDs",
        "profile_version": "neutral-in-place", "profiles": "agent-data/medicine/committee/<member-id>/profile.md",
        "profile_inputs": profile_inputs(), "members": sorted(MEMBERS), "chair": CHAIR,
        "voting": "all six simulated members vote; majority is four",
        "conflict_policy": "disclosed but not adjudicated in this simulation",
        "conflict_flags": [{"candidate_id": c["candidate_id"], "flags": c["conflict_flags"]}
                           for c in sorted(selected, key=lambda c: c["candidate_id"]) if c.get("conflict_flags")],
        "prompts": PROMPTS, "prompt_inputs": prompt_inputs(), "protocol": "docs/PHYSICS_PHASE2.md (adapted to Medicine)",
    }
    return longlist, ballot_map, metadata


def assert_metadata(sim: Path) -> None:
    saved = shared.load_json(sim / "metadata.json")
    for key, expected in (("committee_provider", PROVIDER), ("committee_model", MODEL),
                          ("reasoning_effort", EFFORT), ("members", sorted(MEMBERS)), ("chair", CHAIR)):
        if saved.get(key) != expected:
            fail(f"{sim}/metadata.json: {key} must equal {expected!r}")
    if saved.get("profile_inputs") != profile_inputs():
        fail(f"{sim}: profile sources changed since preparation")
    if saved.get("prompt_inputs") != prompt_inputs():
        fail(f"{sim}: prompt sources changed since preparation")


def prepare(sim: Path, candidates_path: Path | None = None,
            excluded: list[str] | tuple[str, ...] | None = None) -> None:
    packets = dict(zip(("longlist.json", "ballot_map.json", "metadata.json"), build_packet(sim, candidates_path, excluded)))
    # Once any prepared input exists, allow only byte-identical idempotent reuse.
    # This also protects runs dispatched by another process before ballots land.
    for name, value in packets.items():
        path = sim / name
        if path.exists() and path.read_text(encoding="utf-8") != shared.encode(value):
            fail(f"refusing to replace prepared input: {path}")
    dispatched = any((sim / stage).exists() and any((sim / stage).glob("*.json"))
                     for stage in ("opening", "round1", "round2", "final_ballots"))
    if dispatched and not all((sim / name).exists() for name in packets):
        fail(f"refusing to repair missing dispatched inputs in {sim}")
    sim.mkdir(parents=True, exist_ok=True)
    for name, value in packets.items():
        if not (sim / name).exists():
            (sim / name).write_text(shared.encode(value), encoding="utf-8")
    print(f"OK: {sim}: prepared {len(packets['longlist.json']['candidates'])} blinded candidates")


def check_packet(sim: Path) -> dict:
    identity(sim)
    assert_metadata(sim)
    for name, value in zip(("longlist.json", "ballot_map.json", "metadata.json"), build_packet(sim)):
        path = sim / name
        if not path.exists() or path.read_text(encoding="utf-8") != shared.encode(value):
            fail(f"{path} differs from deterministic source inputs")
    return {c["ballot_id"]: c for c in shared.load_json(sim / "longlist.json")["candidates"]}


# All stage logic resolves these globals dynamically in the private module.
shared.PROVIDER = PROVIDER
shared.DEFAULT_MODEL = MODEL
shared.DEFAULT_EFFORT = EFFORT
shared.EXPECTED_MEMBERS = MEMBERS
shared.CHAIR = CHAIR
shared.PROMPTS = PROMPTS
shared.identity = identity
shared.check_packet = check_packet


def _checked_stage(function):
    def checked(sim, member=None, *args, **kwargs):
        check_packet(sim)
        if member is None:
            return function(sim, *args, **kwargs)
        if member not in MEMBERS:
            fail(f"unknown Medicine member: {member}")
        return function(sim, member, *args, **kwargs)
    return checked


shared.check_opening = _checked_stage(shared.check_opening)
shared.check_final = _checked_stage(shared.check_final)
shared.check_chair = _checked_stage(shared.check_chair)
_original_round = shared.check_round


def check_round(sim: Path, number: int, member: str, shortlist: dict | None = None) -> dict:
    check_packet(sim)
    if number not in (1, 2) or member not in MEMBERS:
        fail("invalid Medicine round or member")
    return _original_round(sim, number, member, shortlist)


shared.check_round = check_round
_original_decision = shared.build_decision


def build_decision(sim: Path) -> dict:
    check_packet(sim)
    return {**_original_decision(sim), "committee_provider": PROVIDER, "category": "medicine"}


shared.build_decision = build_decision
_original_slate = shared.build_slate


def build_slate(sim: Path) -> dict:
    check_packet(sim)
    return _original_slate(sim)


shared.build_slate = build_slate


def validate_sim(sim: Path) -> dict:
    check_packet(sim)
    return shared.validate_sim(sim)


def progress() -> None:
    simulations = {}
    directory = RESULTS / COHORT
    for sim in sorted(directory.glob("sim-*")):
        identity(sim)
        entry = {"status": "running", "committee_provider": PROVIDER,
                 "committee_model": MODEL, "reasoning_effort": EFFORT}
        try:
            check_packet(sim)
            if (sim / "decision.json").exists():
                decision = validate_sim(sim)
                entry.update(status="complete", winner=decision["winner"])
        except (SystemExit, OSError, KeyError, ValueError) as exc:
            entry.update(status="failed", error=str(exc))
        simulations[sim.name] = entry
    counts = Counter(e["status"] for e in simulations.values())
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(shared.encode({"schema_version": 1, "category": "medicine",
        "committee_provider": PROVIDER, "committee_model": MODEL, "reasoning_effort": EFFORT,
        "totals": dict(sorted(counts.items())), "simulations": simulations}), encoding="utf-8")
    print(f"OK: {MANIFEST}: {dict(sorted(counts.items()))}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "shortlist", "slate", "tally", "validate"):
        command = sub.add_parser(name)
        command.add_argument("sims", nargs="+", type=Path)
        if name == "prepare":
            command.add_argument("--candidates", type=Path)
            command.add_argument("--exclude", action="append", default=None)
        elif name in ("shortlist", "slate", "tally"):
            command.add_argument("--check", action="store_true")
    member = sub.add_parser("check-member")
    member.add_argument("stage", choices=("opening", "round1", "round2", "final"))
    member.add_argument("sim", type=Path)
    member.add_argument("member", choices=sorted(MEMBERS))
    sub.add_parser("check-chair").add_argument("sim", type=Path)
    sub.add_parser("progress")
    args = parser.parse_args()
    if args.command == "prepare":
        for sim in args.sims:
            prepare(sim, args.candidates, args.exclude)
    elif args.command == "check-member":
        check_packet(args.sim)
        if args.stage == "opening":
            shared.check_opening(args.sim, args.member)
        elif args.stage == "final":
            shared.check_final(args.sim, args.member)
        else:
            check_round(args.sim, int(args.stage[-1]), args.member)
        print(f"OK: {args.stage}/{args.member}")
    elif args.command == "check-chair":
        shared.check_chair(args.sim)
        print("OK: chair summary")
    elif args.command in ("shortlist", "slate", "tally", "validate"):
        for sim in args.sims:
            check_packet(sim)
            if args.command == "validate":
                decision = validate_sim(sim)
                print(f"OK: {sim}: complete; winner {decision['winner']['proposal_id']}")
                continue
            function, filename, guard = {
                "shortlist": (shared.build_shortlist, "shortlist.json", sim / "round1"),
                "slate": (build_slate, "proposal_slate.json", sim / "final_ballots"),
                "tally": (build_decision, "decision.json", None),
            }[args.command]
            value = function(sim)
            shared.write_or_check(sim / filename, value, args.check, guard=guard)
            print(f"OK: {sim}: {filename}")
    else:
        progress()


if __name__ == "__main__":
    main()
