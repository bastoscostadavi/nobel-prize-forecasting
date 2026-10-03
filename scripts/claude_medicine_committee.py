"""Claude-run Physiology or Medicine committee simulations.

Same protocol, validators, shortlist rule, slate and instant-runoff tally as
scripts/claude_committee.py (Physics), adapted to Medicine: six voting members
(chair Per Svenningsson), one directly prepared candidate list instead of
nomination runs, and simulation directories

  results/medicine/committee/claude/sim-NN      (members read agent-data/medicine/committee/<member-id>/profile.md)

Usage:
  python3 scripts/claude_medicine_committee.py prepare --sims 1-60 [--model claude-sonnet-5-5]
  python3 scripts/claude_medicine_committee.py check-member {opening,round1,round2,final} SIM MEMBER
  python3 scripts/claude_medicine_committee.py check-chair SIM
  python3 scripts/claude_medicine_committee.py {shortlist,slate,tally,validate} SIM...
  python3 scripts/claude_medicine_committee.py progress [--arm claude]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

import claude_committee as cc
from validate_committee_opening import load_json

ROOT = cc.ROOT
MEMBERS = {
    "el-manira-abdel", "linnarsson-sten", "perlmann-thomas",
    "sandberg-rickard", "svenningsson-per", "wahren-herlenius-marie",
}
CHAIR = "svenningsson-per"
SEED_PREFIX = "medicine-committee-claude-v1"
ARMS = {"claude": "profile.md"}
CANDIDATES = ROOT / "agent-data" / "medicine" / "candidates" / "candidates.json"
PROMPTS = {
    "opening": "prompts/medicine_committee_claude_opening_v1.md",
    "round1": "prompts/medicine_committee_claude_round1_v1.md",
    "chair": "prompts/medicine_committee_claude_chair_summary_v1.md",
    "round2": "prompts/medicine_committee_claude_round2_v1.md",
    "final": "prompts/medicine_committee_claude_final_ballot_v1.md",
}
RESULTS = ROOT / "results" / "medicine" / "committee"


def identity(sim: Path) -> tuple[Path, str, int, str]:
    """(results dir, candidate list id, run=1, simulation id). Medicine has one candidate list, so run is always 1."""
    sim = sim.resolve()
    if sim.parent.name not in ARMS or sim.parent.parent != RESULTS.resolve():
        fail(f"not a Claude Medicine simulation directory: {sim}")
    if not (sim.name.startswith("sim-") and sim.name[4:].isdigit()):
        fail(f"simulation directory must be named sim-NN: {sim}")
    metadata = sim / "metadata.json"
    list_id = load_json(metadata)["list_id"] if metadata.exists() else "unprepared"
    return RESULTS, list_id, 1, sim.name


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load_candidates(path: Path) -> tuple[str, list[dict]]:
    data = load_json(path)
    candidates = data.get("candidates")
    if not isinstance(candidates, list) or len(candidates) < 8:
        fail(f"{path}: needs a candidates array with at least eight entries")
    seen = set()
    for c in candidates:
        cid = c.get("candidate_id")
        names = c.get("credited_names")
        if not isinstance(cid, str) or cid in seen:
            fail(f"{path}: missing or duplicate candidate_id {cid!r}")
        seen.add(cid)
        for key in ("discovery", "subfield"):
            if not isinstance(c.get(key), str) or not c[key].strip():
                fail(f"{path}: {cid} has no {key}")
        if not isinstance(names, list) or not names or len(set(names)) != len(names) or not all(
            isinstance(n, str) and n.strip() for n in names
        ):
            fail(f"{path}: {cid} credited_names must be unique non-empty strings")
    return data.get("list_id", path.parent.name), candidates


def build_packet(sim: Path, model: str | None = None, effort: str | None = None,
                 candidates_path: Path | None = None) -> tuple[dict, dict, dict]:
    saved = load_json(sim / "metadata.json") if (sim / "metadata.json").exists() else {}
    if model is None:
        model, effort = saved["committee_model"], saved["reasoning_effort"]
        candidates_path = ROOT / saved["candidate_input"]
    list_id, candidates = load_candidates(candidates_path)
    sim_id = sim.resolve().name
    arm = sim.resolve().parent.name
    label = f"{SEED_PREFIX}:{list_id}/{sim_id}"
    entries = []
    for c in candidates:
        payload = {
            "discovery": c["discovery"],
            "subfield": c["subfield"],
            "credited_names": sorted(c["credited_names"], key=lambda n: (n.casefold(), n)),
        }
        serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256((label + "\0" + serialized).encode("utf-8")).hexdigest()
        entries.append((digest, serialized, c["candidate_id"], payload))
    entries.sort(key=lambda e: e[:3])
    longlist = {"schema_version": 1, "candidates": []}
    crosswalk = {}
    for i, (_, _, cid, payload) in enumerate(entries, start=1):
        longlist["candidates"].append({"ballot_id": f"B{i:03d}", **payload})
        crosswalk[f"B{i:03d}"] = cid
    ballot_map = {
        "schema_version": 1, "list_id": list_id, "run": 1, "simulation_id": sim_id,
        "shuffle": {"algorithm": "sha256-sort-v1", "seed_label": label},
        "ballot_to_candidate": crosswalk,
    }
    rel = candidates_path.resolve().relative_to(ROOT)
    metadata = {
        "schema_version": 1,
        "category": "medicine",
        "committee_provider": cc.PROVIDER,
        "committee_model": model,
        "reasoning_effort": effort,
        "list_id": list_id,
        "simulation_id": sim_id,
        "seed_label": label,
        "candidate_input": str(rel),
        "candidate_input_sha256": hashlib.sha256(candidates_path.read_bytes()).hexdigest(),
        "candidate_count": len(candidates),
        "profiles": f"agent-data/medicine/committee/<member-id>/{ARMS[arm]}",
        "members": sorted(MEMBERS),
        "chair": CHAIR,
        "voting": "all six members vote; majority is four",
        "prompts": PROMPTS,
        "protocol": "docs/PHYSICS_PHASE2.md (adapted to Medicine)",
    }
    return longlist, ballot_map, metadata


def prepare(sim: Path, model: str, effort: str, candidates_path: Path) -> None:
    if (sim / "opening").exists() and any((sim / "opening").glob("*.json")):
        fail(f"refusing to replace dispatched packets in {sim}")
    sim.mkdir(parents=True, exist_ok=True)
    for name, value in zip(("longlist.json", "ballot_map.json", "metadata.json"),
                           build_packet(sim, model, effort, candidates_path)):
        (sim / name).write_text(cc.encode(value), encoding="utf-8")
    print(f"OK: {sim}: prepared")


def check_packet(sim: Path) -> dict:
    longlist, ballot_map, metadata = build_packet(sim)
    for name, value in (("longlist.json", longlist), ("ballot_map.json", ballot_map), ("metadata.json", metadata)):
        if (sim / name).read_text(encoding="utf-8") != cc.encode(value):
            fail(f"{sim / name} differs from the deterministic packet (candidate file changed?)")
    return {c["ballot_id"]: c for c in longlist["candidates"]}


# Point the shared Physics implementation at the Medicine committee.
cc.EXPECTED_MEMBERS = MEMBERS
cc.CHAIR = CHAIR
cc.PROMPTS = PROMPTS
cc.identity = identity
cc.check_packet = check_packet
cc.ONESHOT_PROMPT = "prompts/medicine_oneshot_claude_v1.md"


def progress(arm: str) -> None:
    path = ROOT / "results" / "medicine" / f"claude_committee_{arm}_progress.json"
    sims = {}
    for sim in sorted((RESULTS / arm).glob("sim-*")):
        if (sim / "decision.json").exists():
            try:
                decision = cc.validate_sim(sim)
            except SystemExit as exc:
                sims[sim.name] = {"status": "failed", "error": str(exc)}
                continue
            commit = subprocess.run(["git", "log", "-1", "--format=%h", "--", str((sim / "decision.json").relative_to(ROOT))],
                                    cwd=ROOT, capture_output=True, text=True).stdout.strip() or None
            sims[sim.name] = {"status": "complete", "commit": commit,
                              "winner": [{"candidate_id": p["candidate_id"], "laureates": p["laureates"]}
                                         for p in decision["winner"]["prize_parts"]]}
        else:
            sims[sim.name] = {"status": "running"}
    totals = Counter(v["status"] for v in sims.values())
    path.write_text(cc.encode({"schema_version": 1, "category": "medicine", "arm": arm,
                               "totals": dict(sorted(totals.items())),
                               "simulations": sims}), encoding="utf-8")
    print(f"OK: {path.relative_to(ROOT)}: {dict(sorted(totals.items()))}")


def parse_range(text: str) -> list[int]:
    out = []
    for part in text.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--candidates", type=Path, default=CANDIDATES)
    p.add_argument("--sims", required=True, help="e.g. 1-60")
    p.add_argument("--arm", choices=sorted(ARMS), default="claude")
    p.add_argument("--model", default="claude-sonnet-5-5")
    p.add_argument("--effort", default="high")
    for name in ("shortlist", "slate", "tally", "validate"):
        q = sub.add_parser(name)
        q.add_argument("sims", nargs="+", type=Path)
        q.add_argument("--check", action="store_true")
    q = sub.add_parser("check-member")
    q.add_argument("stage", choices=("opening", "round1", "round2", "final"))
    q.add_argument("sim", type=Path)
    q.add_argument("member", choices=sorted(MEMBERS))
    q = sub.add_parser("check-oneshot")
    q.add_argument("paths", nargs="+", type=Path)
    q = sub.add_parser("check-chair")
    q.add_argument("sim", type=Path)
    q = sub.add_parser("progress")
    q.add_argument("--arm", choices=sorted(ARMS), default="claude")
    args = parser.parse_args()

    if args.command == "prepare":
        for n in parse_range(args.sims):
            prepare(RESULTS / args.arm / f"sim-{n:02d}", args.model, args.effort, args.candidates)
    elif args.command == "check-member":
        {"opening": lambda: cc.check_opening(args.sim, args.member),
         "final": lambda: cc.check_final(args.sim, args.member)}.get(
            args.stage, lambda: cc.check_round(args.sim, int(args.stage[-1]), args.member))()
        print(f"OK: {args.stage}/{args.member}")
    elif args.command == "check-oneshot":
        for path in args.paths:
            value = cc.check_oneshot(path)
            print(f"OK: {path}: {value['discovery']} - {'; '.join(value['laureates'])}")
    elif args.command == "check-chair":
        cc.check_chair(args.sim)
        print("OK: chair summary")
    elif args.command == "shortlist":
        for sim in args.sims:
            value = cc.build_shortlist(sim)
            cc.write_or_check(sim / "shortlist.json", value, args.check, guard=sim / "round1")
            print(f"OK: {sim}: {len(value['shortlist'])} shortlisted")
    elif args.command == "slate":
        for sim in args.sims:
            value = cc.build_slate(sim)
            cc.write_or_check(sim / "proposal_slate.json", value, args.check, guard=sim / "final_ballots")
            print(f"OK: {sim}: {len(value['proposals'])} proposals")
    elif args.command == "tally":
        for sim in args.sims:
            value = cc.build_decision(sim)
            cc.write_or_check(sim / "decision.json", value, args.check)
            print(f"OK: {sim}: winner {value['winner']['proposal_id']}")
    elif args.command == "validate":
        for sim in args.sims:
            decision = cc.validate_sim(sim)
            print(f"OK: {sim}: complete; winner {decision['winner']['proposal_id']}")
    elif args.command == "progress":
        progress(args.arm)


if __name__ == "__main__":
    main()
