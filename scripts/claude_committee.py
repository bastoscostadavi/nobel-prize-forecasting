"""Claude-run physics committee simulations under committee/claude/sim-XX/.

Reuses the shared consolidation validator, blinded-payload rules, shortlist rule,
proposal grouping and instant-runoff tally, but operates on one simulation
directory and records Claude's model metadata. GPT-owned paths are never read
or written.

Usage (SIM is results/physics/<list-id>/run-<n>/committee/claude/sim-XX):
  python3 scripts/claude_committee.py prepare SIM...
  python3 scripts/claude_committee.py check-member {opening,round1,round2,final} SIM MEMBER
  python3 scripts/claude_committee.py check-chair SIM
  python3 scripts/claude_committee.py shortlist SIM...
  python3 scripts/claude_committee.py slate SIM...
  python3 scripts/claude_committee.py tally SIM...
  python3 scripts/claude_committee.py validate SIM...
  python3 scripts/claude_committee.py check-oneshot results/physics/oneshot/<model>/pred-XX.json...
  python3 scripts/claude_committee.py progress
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

from build_committee_proposals import canonical_parts
from prepare_committee_longlist import ALGORITHM, canonical_payload, validate_packet
from validate_candidate_merge import check_csv, validate as validate_merge
from validate_committee_opening import EXPECTED_MEMBERS, load_json, nonempty_text


PROVIDER = "anthropic"
DEFAULT_MODEL = "claude-sonnet-5-5"
DEFAULT_EFFORT = "high"
SEED_PREFIX = "physics-committee-claude-v1"
CHAIR = "pearce-mark"
PROMPTS = {
    "opening": "prompts/physics_committee_claude_opening_v1.md",
    "round1": "prompts/physics_committee_claude_round1_v1.md",
    "chair": "prompts/physics_committee_claude_chair_summary_v1.md",
    "round2": "prompts/physics_committee_claude_round2_v1.md",
    "final": "prompts/physics_committee_claude_final_ballot_v1.md",
}
ROOT = Path(__file__).resolve().parent.parent
LISTS = ("claude-opus-5-5", "gpt-6-sol")
RUNS = range(1, 7)
SIMS = [f"sim-{i:02d}" for i in range(1, 6)]
MANIFEST = ROOT / "results" / "physics" / "claude_committee_progress.json"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def encode(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def identity(sim: Path) -> tuple[Path, str, int, str]:
    sim = sim.resolve()
    if sim.parent.name != "claude" or sim.parent.parent.name != "committee":
        fail(f"not a Claude simulation directory: {sim}")
    run_dir = sim.parents[2]
    try:
        run = int(run_dir.name.removeprefix("run-"))
    except ValueError:
        fail(f"run directory must be named run-N: {run_dir}")
    if sim.name not in SIMS:
        fail(f"simulation directory must be sim-01..sim-05: {sim}")
    return run_dir, run_dir.parent.name, run, sim.name


def seed_label(sim: Path) -> str:
    _, list_id, run, sim_id = identity(sim)
    return f"{SEED_PREFIX}:{list_id}/run-{run}/{sim_id}"


# ---------------------------------------------------------------- packets

def build_packet(sim: Path, model: str | None = None, effort: str | None = None) -> tuple[dict, dict, dict]:
    run_dir, list_id, run, sim_id = identity(sim)
    merged, rows = validate_merge(run_dir)
    check_csv(run_dir, rows)
    label = seed_label(sim)

    def shuffle(candidates: list[dict]) -> tuple[dict, dict]:
        entries = []
        for candidate in candidates:
            payload = canonical_payload(candidate)
            serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            digest = hashlib.sha256((label + "\0" + serialized).encode("utf-8")).hexdigest()
            entries.append((digest, serialized, candidate["candidate_id"], payload))
        entries.sort(key=lambda entry: entry[:3])
        longlist = {"schema_version": 1, "candidates": []}
        crosswalk = {}
        for index, (_, _, candidate_id, payload) in enumerate(entries, start=1):
            ballot_id = f"B{index:03d}"
            longlist["candidates"].append({"ballot_id": ballot_id, **payload})
            crosswalk[ballot_id] = candidate_id
        ballot_map = {
            "schema_version": 1,
            "list_id": list_id,
            "run": run,
            "simulation_id": sim_id,
            "shuffle": {"algorithm": ALGORITHM, "seed_label": label},
            "ballot_to_candidate": crosswalk,
        }
        validate_packet(merged, longlist, ballot_map)
        return longlist, ballot_map

    longlist, ballot_map = shuffle(merged["candidates"])
    reversed_candidates = [
        {**c, "nominees": list(reversed(c["nominees"])), "other_names": list(reversed(c["other_names"]))}
        for c in reversed(merged["candidates"])
    ]
    if shuffle(reversed_candidates) != (longlist, ballot_map):
        fail("packet generation is not deterministic under candidate reordering")
    if model is None:
        saved = load_json(sim / "metadata.json")
        model, effort = saved["committee_model"], saved["reasoning_effort"]
    metadata = {
        "schema_version": 1,
        "committee_provider": PROVIDER,
        "committee_model": model,
        "reasoning_effort": effort,
        "list_id": list_id,
        "nomination_run": run,
        "simulation_id": sim_id,
        "seed_label": label,
        "candidate_input": "../../../candidates.json",
        "candidate_input_sha256": hashlib.sha256((run_dir / "candidates.json").read_bytes()).hexdigest(),
        "members": sorted(EXPECTED_MEMBERS),
        "chair": CHAIR,
        "prompts": PROMPTS,
        "protocol": "docs/PHYSICS_PHASE2.md",
    }
    if (sim / metadata["candidate_input"]).resolve() != (run_dir / "candidates.json").resolve():
        fail("candidate_input does not resolve to the run's candidates.json")
    return longlist, ballot_map, metadata


def prepare(sim: Path, model: str, effort: str) -> None:
    longlist, ballot_map, metadata = build_packet(sim, model, effort)
    if (sim / "opening").exists() and any((sim / "opening").glob("*.json")):
        fail(f"refusing to replace dispatched packets in {sim}")
    sim.mkdir(parents=True, exist_ok=True)
    for name, value in (("longlist.json", longlist), ("ballot_map.json", ballot_map), ("metadata.json", metadata)):
        (sim / name).write_text(encode(value), encoding="utf-8")
    print(f"OK: {sim}: prepared {len(longlist['candidates'])} blinded candidates")


def check_packet(sim: Path) -> dict:
    longlist, ballot_map, metadata = build_packet(sim)
    for name, value in (("longlist.json", longlist), ("ballot_map.json", ballot_map), ("metadata.json", metadata)):
        if (sim / name).read_text(encoding="utf-8") != encode(value):
            fail(f"{sim / name} differs from the deterministic packet")
    return {item["ballot_id"]: item for item in longlist["candidates"]}


# ---------------------------------------------------------------- member files

def execution(sim: Path) -> tuple[str, str]:
    metadata = load_json(sim / "metadata.json")
    return metadata["committee_model"], metadata["reasoning_effort"]


def check_header(value: dict, sim: Path, stage: str, member_key: str, member: str, extra: set[str]) -> None:
    _, list_id, run, sim_id = identity(sim)
    model, effort = execution(sim)
    keys = {"schema_version", "list_id", "run", "simulation_id", member_key, "model", "reasoning_effort", "prompt"} | extra
    if set(value) != keys:
        fail(f"{stage}/{member}: top-level keys differ (expected {sorted(keys)})")
    if (
        type(value["schema_version"]) is not int or value["schema_version"] != 1
        or value["list_id"] != list_id
        or type(value["run"]) is not int or value["run"] != run
        or value["simulation_id"] != sim_id
        or value[member_key] != member
        or value["model"] != model
        or value["reasoning_effort"] != effort
        or value["prompt"] != PROMPTS[stage]
    ):
        fail(f"{stage}/{member}: metadata differs")


def check_opening(sim: Path, member: str, longlist: dict | None = None) -> dict:
    by_id = longlist or {c["ballot_id"]: c for c in load_json(sim / "longlist.json")["candidates"]}
    value = load_json(sim / "opening" / f"{member}.json")
    check_header(value, sim, "opening", "member_id", member, {"rankings"})
    rankings = value["rankings"]
    if not isinstance(rankings, list) or len(rankings) != 8:
        fail(f"opening/{member}: rankings must contain exactly eight entries")
    seen = set()
    for rank, entry in enumerate(rankings, start=1):
        if not isinstance(entry, dict) or set(entry) != {"rank", "ballot_id", "proposed_laureates", "assessment"}:
            fail(f"opening/{member}: entry keys differ at rank {rank}")
        if type(entry["rank"]) is not int or entry["rank"] != rank:
            fail(f"opening/{member}: ranks must be consecutive")
        ballot_id = entry["ballot_id"]
        if ballot_id not in by_id or ballot_id in seen:
            fail(f"opening/{member}: invalid or repeated ballot ID {ballot_id!r}")
        seen.add(ballot_id)
        laureates = entry["proposed_laureates"]
        credited = set(by_id[ballot_id]["credited_names"])
        if (
            not isinstance(laureates, list) or not 1 <= len(laureates) <= 3
            or len(set(laureates)) != len(laureates)
            or not all(isinstance(n, str) and n in credited for n in laureates)
        ):
            fail(f"opening/{member}: laureates for {ballot_id} must be 1-3 exact credited names")
        assessment = entry["assessment"]
        if not isinstance(assessment, dict) or set(assessment) != {"nobel_worthiness", "attribution", "maturity", "uncertainties"}:
            fail(f"opening/{member}: assessment keys differ for {ballot_id}")
        for key in ("nobel_worthiness", "attribution", "maturity"):
            nonempty_text(assessment[key], f"opening/{member}:{ballot_id}:{key}")
        if not isinstance(assessment["uncertainties"], list) or not all(
            isinstance(i, str) and i.strip() for i in assessment["uncertainties"]
        ):
            fail(f"opening/{member}: uncertainties must be non-empty strings")
    return value


def check_round(sim: Path, number: int, member: str, shortlist: dict | None = None) -> dict:
    stage = f"round{number}"
    by_id = shortlist or {c["ballot_id"]: c for c in load_json(sim / "shortlist.json")["shortlist"]}
    value = load_json(sim / stage / f"{member}.json")
    check_header(value, sim, stage, "member_id", member, {"preferred_configuration", "alternatives", "statement"})
    configuration = value["preferred_configuration"]
    if not isinstance(configuration, dict) or set(configuration) != {"prize_parts"}:
        fail(f"{stage}/{member}: configuration keys differ")
    parts = configuration["prize_parts"]
    if not isinstance(parts, list) or not 1 <= len(parts) <= 2:
        fail(f"{stage}/{member}: one or two prize parts required")
    part_ids, people = set(), set()
    for part in parts:
        if not isinstance(part, dict) or set(part) != {"ballot_id", "laureates", "citation"}:
            fail(f"{stage}/{member}: prize-part keys differ")
        ballot_id = part["ballot_id"]
        if not isinstance(ballot_id, str) or ballot_id not in by_id or ballot_id in part_ids:
            fail(f"{stage}/{member}: invalid or repeated prize part {ballot_id!r}")
        part_ids.add(ballot_id)
        laureates = part["laureates"]
        credited = set(by_id[ballot_id]["credited_names"])
        if (
            not isinstance(laureates, list) or not 1 <= len(laureates) <= 3
            or len(set(laureates)) != len(laureates)
            or not all(isinstance(n, str) and n in credited for n in laureates)
        ):
            fail(f"{stage}/{member}: laureates for {ballot_id} must be 1-3 exact credited names")
        people.update(laureates)
        nonempty_text(part["citation"], f"{stage}/{member}:{ballot_id}:citation")
    if not 1 <= len(people) <= 3:
        fail(f"{stage}/{member}: configuration must name one to three unique people")
    alternatives = value["alternatives"]
    if (
        not isinstance(alternatives, list) or len(alternatives) > 2
        or len(set(alternatives)) != len(alternatives)
        or not all(isinstance(a, str) and a in by_id and a not in part_ids for a in alternatives)
    ):
        fail(f"{stage}/{member}: invalid alternatives")
    statement = value["statement"]
    if not isinstance(statement, dict) or set(statement) != {"case_for", "case_against", "responses", "uncertainties", "conflict_note"}:
        fail(f"{stage}/{member}: statement keys differ")
    for key in ("case_for", "case_against", "conflict_note"):
        nonempty_text(statement[key], f"{stage}/{member}:{key}")
    responses = statement["responses"]
    if not isinstance(responses, list) or len(responses) < 2:
        fail(f"{stage}/{member}: at least two responses required")
    addressed = set()
    for response in responses:
        if not isinstance(response, dict) or set(response) != {"member_id", "point", "response"}:
            fail(f"{stage}/{member}: response keys differ")
        other = response["member_id"]
        if other not in EXPECTED_MEMBERS or other == member:
            fail(f"{stage}/{member}: invalid response member {other!r}")
        addressed.add(other)
        nonempty_text(response["point"], f"{stage}/{member}:point")
        nonempty_text(response["response"], f"{stage}/{member}:response")
    if len(addressed) < 2:
        fail(f"{stage}/{member}: responses must address two distinct members")
    if not isinstance(statement["uncertainties"], list) or not all(
        isinstance(i, str) and i.strip() for i in statement["uncertainties"]
    ):
        fail(f"{stage}/{member}: uncertainties must be non-empty strings")
    return value


def check_final(sim: Path, member: str, slate: dict | None = None) -> list[str]:
    slate = slate or load_json(sim / "proposal_slate.json")
    expected = {p["proposal_id"] for p in slate["proposals"]}
    value = load_json(sim / "final_ballots" / f"{member}.json")
    check_header(value, sim, "final", "member_id", member, {"ranked_proposal_ids", "top_choice_rationale", "recusal_note"})
    ranking = value["ranked_proposal_ids"]
    if (
        not isinstance(ranking, list) or not all(isinstance(i, str) for i in ranking)
        or len(ranking) != len(expected) or set(ranking) != expected
    ):
        fail(f"final/{member}: ranking must be a permutation of every proposal ID")
    nonempty_text(value["top_choice_rationale"], f"final/{member}:top_choice_rationale")
    nonempty_text(value["recusal_note"], f"final/{member}:recusal_note")
    return ranking


def text_list(value: object, label: str, minimum: int = 0) -> list:
    if not isinstance(value, list) or len(value) < minimum or not all(isinstance(i, str) and i.strip() for i in value):
        fail(f"{label} must contain at least {minimum} non-empty strings")
    return value


def check_chair(sim: Path) -> None:
    shortlisted = {c["ballot_id"] for c in load_json(sim / "shortlist.json")["shortlist"]}
    preferences = {
        m: {p["ballot_id"] for p in load_json(sim / "round1" / f"{m}.json")["preferred_configuration"]["prize_parts"]}
        for m in EXPECTED_MEMBERS
    }
    value = load_json(sim / "chair_summary_round1.json")
    check_header(value, sim, "chair", "chair_id", CHAIR, {"summary"})
    summary = value["summary"]
    keys = {
        "leading_positions", "areas_of_agreement", "scientific_disputes", "attribution_disputes",
        "maturity_disputes", "conflict_or_recusal_flags", "questions_for_round2", "chair_observation",
    }
    if not isinstance(summary, dict) or set(summary) != keys:
        fail("chair: summary keys differ")
    positions = summary["leading_positions"]
    if not isinstance(positions, list) or not positions:
        fail("chair: at least one leading position required")
    for position in positions:
        if not isinstance(position, dict) or set(position) != {"ballot_ids", "explicit_supporters", "synthesis"}:
            fail("chair: leading-position keys differ")
        ids = text_list(position["ballot_ids"], "chair:ballot_ids", 1)
        supporters = text_list(position["explicit_supporters"], "chair:explicit_supporters", 1)
        if len(set(ids)) != len(ids) or not set(ids) <= shortlisted:
            fail("chair: invalid leading ballot IDs")
        if len(set(supporters)) != len(supporters) or not set(supporters) <= EXPECTED_MEMBERS:
            fail("chair: invalid supporters")
        for supporter in supporters:
            if not set(ids) <= preferences[supporter]:
                fail(f"chair: {supporter} did not propose all of {ids} in round 1")
        nonempty_text(position["synthesis"], "chair:synthesis")
    text_list(summary["areas_of_agreement"], "chair:areas_of_agreement", 1)
    for key in ("scientific_disputes", "attribution_disputes", "maturity_disputes", "conflict_or_recusal_flags"):
        text_list(summary[key], f"chair:{key}")
    text_list(summary["questions_for_round2"], "chair:questions_for_round2", 2)
    nonempty_text(summary["chair_observation"], "chair:chair_observation")


# ---------------------------------------------------------------- derived files

def build_shortlist(sim: Path) -> dict:
    by_id = check_packet(sim)
    _, list_id, run, sim_id = identity(sim)
    support = {b: {"member_rankings": [], "laureate_proposals": [], "borda_points": 0} for b in by_id}
    for member in sorted(EXPECTED_MEMBERS):
        for entry in check_opening(sim, member, by_id)["rankings"]:
            item = support[entry["ballot_id"]]
            item["member_rankings"].append({"member_id": member, "rank": entry["rank"]})
            item["laureate_proposals"].append({"member_id": member, "proposed_laureates": entry["proposed_laureates"]})
            item["borda_points"] += 9 - entry["rank"]

    def metrics(b: str) -> tuple[int, int, int, int, int]:
        ranks = [r["rank"] for r in support[b]["member_rankings"]]
        return (
            sum(r == 1 for r in ranks), sum(r <= 3 for r in ranks), len(ranks),
            support[b]["borda_points"], min(ranks, default=99),
        )

    selected = {b for b in by_id if metrics(b)[0] >= 1 or metrics(b)[1] >= 2 or metrics(b)[2] >= 3}
    priority = sorted(by_id, key=lambda b: (-metrics(b)[0], -metrics(b)[1], -metrics(b)[2], -metrics(b)[3], metrics(b)[4], b))
    for b in priority:
        if len(selected) >= 8:
            break
        selected.add(b)
    shortlist = []
    for b in priority:
        if b not in selected:
            continue
        first, top_three, ranked, points, best = metrics(b)
        shortlist.append({
            **by_id[b],
            "opening_support": {
                "first_place": first,
                "top_three": top_three,
                "ranked": ranked,
                "borda_points": points,
                "best_rank": best,
                "member_rankings": sorted(support[b]["member_rankings"], key=lambda r: (r["rank"], r["member_id"])),
                "laureate_proposals": sorted(support[b]["laureate_proposals"], key=lambda r: r["member_id"]),
            },
        })
    return {
        "schema_version": 1,
        "list_id": list_id,
        "run": run,
        "simulation_id": sim_id,
        "selection_rule": {
            "id": "opening-union-v1",
            "automatic": [
                "at least one first-place ranking",
                "at least two top-three rankings",
                "ranked in the top eight by at least three members",
            ],
            "minimum_candidates": 8,
            "fill_order": [
                "first_place descending",
                "top_three descending",
                "ranked descending",
                "borda_points descending (8 points for rank 1 through 1 for rank 8)",
                "best_rank ascending",
                "ballot_id ascending",
            ],
        },
        "shortlist": shortlist,
    }


def build_slate(sim: Path) -> dict:
    shortlist = {c["ballot_id"]: c for c in load_json(sim / "shortlist.json")["shortlist"]}
    _, list_id, run, sim_id = identity(sim)
    grouped: dict[str, dict] = {}
    for member in sorted(EXPECTED_MEMBERS):
        raw = check_round(sim, 2, member, shortlist)["preferred_configuration"]["prize_parts"]
        parts = canonical_parts(raw)
        key = json.dumps(parts, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        record = grouped.setdefault(key, {"prize_parts": parts, "explicit_supporters": [], "member_citations": []})
        record["explicit_supporters"].append(member)
        record["member_citations"].append({
            "member_id": member,
            "citations": [{"ballot_id": p["ballot_id"], "citation": p["citation"]} for p in raw],
        })
    proposals = [{
        "proposal_id": "P000", "prize_parts": [], "explicit_supporters": [],
        "member_citations": [], "meaning": "No award in this simulation",
    }]
    ordered = sorted(grouped.items(), key=lambda item: (-len(item[1]["explicit_supporters"]), item[0]))
    for index, (_, record) in enumerate(ordered, start=1):
        proposals.append({"proposal_id": f"P{index:03d}", **record, "meaning": "Award the listed prize part or parts"})
    return {
        "schema_version": 1, "list_id": list_id, "run": run, "simulation_id": sim_id,
        "source": "round2/*.json", "proposals": proposals,
    }


def build_decision(sim: Path) -> dict:
    slate = load_json(sim / "proposal_slate.json")
    if (sim / "proposal_slate.json").read_text(encoding="utf-8") != encode(build_slate(sim)):
        fail("proposal slate differs from the deterministic round-2 slate")
    _, list_id, run, sim_id = identity(sim)
    ballots = {m: check_final(sim, m, slate) for m in sorted(EXPECTED_MEMBERS)}
    proposals = {p["proposal_id"]: p for p in slate["proposals"]}
    active = set(proposals)
    majority = len(ballots) // 2 + 1
    borda = {p: sum(len(active) - r.index(p) for r in ballots.values()) for p in active}
    supporters = {p: len(proposals[p]["explicit_supporters"]) for p in active}
    rounds, winner = [], None
    while active:
        choices = {m: next(p for p in r if p in active) for m, r in ballots.items()}
        counts = Counter(choices.values())
        table = {p: counts.get(p, 0) for p in sorted(active)}
        leaders = [p for p, c in table.items() if c >= majority]
        if leaders or len(active) == 1:
            winner = sorted(leaders, key=lambda p: (-table[p], p))[0] if leaders else next(iter(active))
            rounds.append({"round": len(rounds) + 1, "counts": table, "eliminated": None})
            break
        minimum = min(table.values())
        eliminated = sorted((p for p, c in table.items() if c == minimum), key=lambda p: (supporters[p], borda[p], p))[0]
        rounds.append({
            "round": len(rounds) + 1, "counts": table, "eliminated": eliminated,
            "elimination_tie_break": {
                "fewest_current_votes": minimum,
                "round2_explicit_supporters": supporters[eliminated],
                "full_ballot_borda": borda[eliminated],
                "final_tie_break": "proposal_id ascending",
            },
        })
        active.remove(eliminated)
    crosswalk = load_json(sim / "ballot_map.json")["ballot_to_candidate"]
    longlist = {c["ballot_id"]: c for c in load_json(sim / "longlist.json")["candidates"]}
    parts = [{
        "ballot_id": p["ballot_id"],
        "candidate_id": crosswalk[p["ballot_id"]],
        "discovery": longlist[p["ballot_id"]]["discovery"],
        "laureates": p["laureates"],
    } for p in proposals[winner]["prize_parts"]]
    return {
        "schema_version": 1, "list_id": list_id, "run": run, "simulation_id": sim_id,
        "committee_model": execution(sim)[0], "reasoning_effort": execution(sim)[1],
        "rule": {
            "method": "instant runoff over exhaustive rankings",
            "majority_votes": majority,
            "elimination_order": [
                "fewest current first-active preferences",
                "fewest explicit round-2 supporters",
                "lowest full-ballot Borda score",
                "proposal_id ascending",
            ],
            "recusals": "disclosed but not adjudicated in this simulation",
        },
        "rounds": rounds,
        "winner": {"proposal_id": winner, "no_award": winner == "P000", "prize_parts": parts},
    }


def write_or_check(path: Path, value: dict, check: bool, guard: Path | None = None) -> None:
    if check:
        if not path.exists() or path.read_text(encoding="utf-8") != encode(value):
            fail(f"{path} differs from its deterministic value")
        return
    if guard is not None and guard.exists() and any(guard.glob("*.json")):
        fail(f"refusing to overwrite {path}: {guard} already has files")
    path.write_text(encode(value), encoding="utf-8")


# ---------------------------------------------------------------- full validation and progress

def validate_sim(sim: Path) -> dict:
    check_packet(sim)
    write_or_check(sim / "shortlist.json", build_shortlist(sim), check=True)
    shortlist = {c["ballot_id"]: c for c in load_json(sim / "shortlist.json")["shortlist"]}
    for member in EXPECTED_MEMBERS:
        check_round(sim, 1, member, shortlist)
    check_chair(sim)
    write_or_check(sim / "proposal_slate.json", build_slate(sim), check=True)
    decision = build_decision(sim)
    write_or_check(sim / "decision.json", decision, check=True)
    expected = {
        "longlist.json", "ballot_map.json", "metadata.json", "shortlist.json", "chair_summary_round1.json",
        "proposal_slate.json", "decision.json", "opening", "round1", "round2", "final_ballots",
    }
    present = {p.name for p in sim.iterdir()}
    if present != expected:
        fail(f"{sim}: unexpected or missing entries: extra={sorted(present - expected)}, missing={sorted(expected - present)}")
    for stage in ("opening", "round1", "round2", "final_ballots"):
        names = {p.name for p in (sim / stage).iterdir()}
        if names != {f"{m}.json" for m in EXPECTED_MEMBERS}:
            fail(f"{sim}/{stage}: files differ from the eight member files")
    return decision


def progress() -> None:
    manifest = load_json(MANIFEST) if MANIFEST.exists() else {}
    simulations = manifest.get("simulations", {})
    for list_id in LISTS:
        for run in RUNS:
            for sim_id in SIMS:
                key = f"{list_id}/run-{run}/{sim_id}"
                sim = ROOT / "results" / "physics" / list_id / f"run-{run}" / "committee" / "claude" / sim_id
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
                            cwd=ROOT, capture_output=True, text=True,
                        ).stdout.strip()
                        entry = {
                            "status": "complete",
                            "committee_model": decision["committee_model"],
                            "reasoning_effort": decision["reasoning_effort"],
                            "commit": tracked or entry.get("commit"),
                            "winner": [
                                {"candidate_id": p["candidate_id"], "laureates": p["laureates"]}
                                for p in decision["winner"]["prize_parts"]
                            ],
                        }
                elif sim.exists() and entry.get("status") != "failed":
                    entry = {"status": "running", "commit": None}
                simulations[key] = entry
    counts = Counter(e["status"] for e in simulations.values())
    MANIFEST.write_text(encode({
        "schema_version": 1,
        "committee_provider": PROVIDER,
        "totals": dict(sorted(counts.items())),
        "simulations": simulations,
    }), encoding="utf-8")
    print(f"OK: {MANIFEST.relative_to(ROOT)}: {dict(sorted(counts.items()))}")


# ---------------------------------------------------------------- one-shot baseline

ONESHOT_PROMPT = "prompts/physics_oneshot_claude_v1.md"


def check_oneshot(path: Path) -> dict:
    """Validate one no-input prediction at results/physics/oneshot/<model>/pred-XX.json."""
    value = load_json(path)
    keys = {"schema_version", "prediction_id", "model", "reasoning_effort", "prompt", "discovery", "laureates", "rationale"}
    if set(value) != keys:
        fail(f"{path}: top-level keys differ (expected {sorted(keys)})")
    if (
        type(value["schema_version"]) is not int or value["schema_version"] != 1
        or value["prediction_id"] != path.stem
        or value["model"] != path.parent.name
        or value["prompt"] != ONESHOT_PROMPT
    ):
        fail(f"{path}: metadata differs")
    nonempty_text(value["reasoning_effort"], f"{path}:reasoning_effort")
    nonempty_text(value["discovery"], f"{path}:discovery")
    names = value["laureates"]
    if not isinstance(names, list) or not 1 <= len(names) <= 3 or len(set(names)) != len(names) or not all(
        isinstance(n, str) and n.strip() for n in names
    ):
        fail(f"{path}: laureates must be one to three distinct names")
    nonempty_text(value["rationale"], f"{path}:rationale")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "shortlist", "slate", "tally", "validate"):
        p = sub.add_parser(name)
        p.add_argument("sims", nargs="+", type=Path)
        if name == "prepare":
            p.add_argument("--model", default=DEFAULT_MODEL)
            p.add_argument("--effort", default=DEFAULT_EFFORT)
        if name in ("shortlist", "slate", "tally"):
            p.add_argument("--check", action="store_true")
    p = sub.add_parser("check-member")
    p.add_argument("stage", choices=("opening", "round1", "round2", "final"))
    p.add_argument("sim", type=Path)
    p.add_argument("member", choices=sorted(EXPECTED_MEMBERS))
    p = sub.add_parser("check-oneshot")
    p.add_argument("sims", nargs="+", type=Path)
    p = sub.add_parser("check-chair")
    p.add_argument("sim", type=Path)
    sub.add_parser("progress")
    args = parser.parse_args()

    if args.command == "prepare":
        for sim in args.sims:
            prepare(sim, args.model, args.effort)
    elif args.command == "check-member":
        if args.stage == "opening":
            check_opening(args.sim, args.member)
        elif args.stage == "final":
            check_final(args.sim, args.member)
        else:
            check_round(args.sim, int(args.stage[-1]), args.member)
        print(f"OK: {args.stage}/{args.member}")
    elif args.command == "check-oneshot":
        for path in args.sims:
            value = check_oneshot(path)
            print(f"OK: {path}: {value['discovery']} - {'; '.join(value['laureates'])}")
    elif args.command == "check-chair":
        check_chair(args.sim)
        print("OK: chair summary")
    elif args.command == "shortlist":
        for sim in args.sims:
            value = build_shortlist(sim)
            write_or_check(sim / "shortlist.json", value, args.check, guard=sim / "round1")
            print(f"OK: {sim}: {len(value['shortlist'])} shortlisted")
    elif args.command == "slate":
        for sim in args.sims:
            value = build_slate(sim)
            write_or_check(sim / "proposal_slate.json", value, args.check, guard=sim / "final_ballots")
            print(f"OK: {sim}: {len(value['proposals'])} proposals")
    elif args.command == "tally":
        for sim in args.sims:
            value = build_decision(sim)
            write_or_check(sim / "decision.json", value, args.check)
            print(f"OK: {sim}: winner {value['winner']['proposal_id']}")
    elif args.command == "validate":
        for sim in args.sims:
            decision = validate_sim(sim)
            print(f"OK: {sim}: complete; winner {decision['winner']['proposal_id']}")
    elif args.command == "progress":
        progress()


if __name__ == "__main__":
    main()
