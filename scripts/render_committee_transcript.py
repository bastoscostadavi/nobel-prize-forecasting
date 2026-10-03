"""Render one committee simulation's saved records as a readable Markdown transcript.

Usage: python3 scripts/render_committee_transcript.py SIM_DIR OUTPUT.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

NAMES = {
    "danielsson-ulf": "Ulf Danielsson", "eriksson-olle": "Olle Eriksson", "johansson-goran": "Göran Johansson",
    "kroll-stefan": "Stefan Kröll", "lindroth-eva": "Eva Lindroth", "mehlig-bernhard": "Bernhard Mehlig",
    "olsson-eva": "Eva Olsson", "pearce-mark": "Mark Pearce",
    "el-manira-abdel": "Abdel El Manira", "linnarsson-sten": "Sten Linnarsson", "perlmann-thomas": "Thomas Perlmann",
    "sandberg-rickard": "Rickard Sandberg", "svenningsson-per": "Per Svenningsson",
    "wahren-herlenius-marie": "Marie Wahren-Herlenius",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def name(member: str) -> str:
    return NAMES.get(member, member)


def render(sim: Path) -> str:
    meta = load(sim / "metadata.json")
    longlist = {c["ballot_id"]: c for c in load(sim / "longlist.json")["candidates"]}
    title = lambda b: longlist[b]["discovery"]
    members = sorted(p.stem for p in (sim / "opening").glob("*.json"))
    out = [f"# Committee transcript: {sim.as_posix().split('results/')[-1]}", ""]
    out += [f"Model: `{meta['committee_model']}` (reasoning effort `{meta['reasoning_effort']}`). "
            f"Candidates: {len(longlist)}. Members: {', '.join(name(m) for m in members)}.", ""]
    out += ["Everything below is the saved record of the simulation, reproduced verbatim from the JSON files.", ""]

    out += ["## 1. Private opening rankings", ""]
    for m in members:
        out += [f"### {name(m)}", ""]
        for e in load(sim / "opening" / f"{m}.json")["rankings"]:
            a = e["assessment"]
            out += [f"**{e['rank']}. {e['ballot_id']} — {title(e['ballot_id'])}** "
                    f"(proposed: {', '.join(e['proposed_laureates'])})", "",
                    f"- *Nobel worthiness:* {a['nobel_worthiness']}",
                    f"- *Attribution:* {a['attribution']}",
                    f"- *Maturity:* {a['maturity']}"]
            if a["uncertainties"]:
                out += [f"- *Uncertainties:* {' '.join(a['uncertainties'])}"]
            out += [""]

    out += ["## 2. Shortlist", ""]
    out += ["| Ballot | Discovery | First places | Top three | Ranked by |", "|---|---|---|---|---|"]
    for c in load(sim / "shortlist.json")["shortlist"]:
        s = c["opening_support"]
        out += [f"| {c['ballot_id']} | {c['discovery']} | {s['first_place']} | {s['top_three']} | {s['ranked']} |"]
    out += [""]

    def statements(stage: str, heading: str) -> None:
        nonlocal out
        out += [heading, ""]
        for m in members:
            v = load(sim / stage / f"{m}.json")
            st = v["statement"]
            parts = "; ".join(f"{p['ballot_id']} {title(p['ballot_id'])} ({', '.join(p['laureates'])})"
                              for p in v["preferred_configuration"]["prize_parts"])
            out += [f"### {name(m)}", "", f"**Proposed prize:** {parts}", ""]
            for p in v["preferred_configuration"]["prize_parts"]:
                out += [f"> *Citation ({p['ballot_id']}):* {p['citation']}", ""]
            if v["alternatives"]:
                out += [f"**Alternatives:** {', '.join(f'{b} {title(b)}' for b in v['alternatives'])}", ""]
            out += [f"**Case for.** {st['case_for']}", "", f"**Case against.** {st['case_against']}", ""]
            for r in st["responses"]:
                out += [f"**To {name(r['member_id'])}.** *{r['point']}* {r['response']}", ""]
            if st["uncertainties"]:
                out += [f"**Uncertainties.** {' '.join(st['uncertainties'])}", ""]
            out += [f"**Conflict note.** {st['conflict_note']}", ""]

    statements("round1", "## 3. Discussion round 1")

    chair = load(sim / "chair_summary_round1.json")
    s = chair["summary"]
    out += [f"## 4. Chair summary ({name(chair['chair_id'])})", ""]
    for p in s["leading_positions"]:
        out += [f"- **{' + '.join(p['ballot_ids'])}** — supporters: "
                f"{', '.join(name(x) for x in p['explicit_supporters'])}. {p['synthesis']}"]
    out += [""]
    for key, label in [("areas_of_agreement", "Areas of agreement"), ("scientific_disputes", "Scientific disputes"),
                       ("attribution_disputes", "Attribution disputes"), ("maturity_disputes", "Maturity disputes"),
                       ("conflict_or_recusal_flags", "Conflict or recusal flags"),
                       ("questions_for_round2", "Questions for round 2")]:
        if s[key]:
            out += [f"**{label}**", ""] + [f"- {x}" for x in s[key]] + [""]
    out += [f"**Chair observation.** {s['chair_observation']}", ""]

    statements("round2", "## 5. Discussion round 2")

    out += ["## 6. Proposal slate", "", "| Proposal | Prize | Round-2 supporters |", "|---|---|---|"]
    slate = load(sim / "proposal_slate.json")["proposals"]
    for p in slate:
        prize = " + ".join(f"{title(x['ballot_id'])} ({', '.join(x['laureates'])})" for x in p["prize_parts"]) or "No award"
        out += [f"| {p['proposal_id']} | {prize} | {', '.join(name(x) for x in p['explicit_supporters']) or '—'} |"]
    out += [""]

    out += ["## 7. Private final ballots", ""]
    for m in members:
        v = load(sim / "final_ballots" / f"{m}.json")
        out += [f"### {name(m)}", "", f"**Ranking:** {' > '.join(v['ranked_proposal_ids'])}", "",
                f"**Top-choice rationale.** {v['top_choice_rationale']}", "",
                f"**Recusal note.** {v['recusal_note']}", ""]

    d = load(sim / "decision.json")
    out += ["## 8. Instant-runoff tally and decision", ""]
    ids = [p["proposal_id"] for p in slate]
    out += ["| Round | " + " | ".join(ids) + " | Eliminated |", "|" + "---|" * (len(ids) + 2)]
    for r in d["rounds"]:
        out += [f"| {r['round']} | " + " | ".join(str(r["counts"].get(i, "—")) for i in ids)
                + f" | {r['eliminated'] or '—'} |"]
    w = d["winner"]
    prize = " + ".join(f"{p['discovery']} ({', '.join(p['laureates'])})" for p in w["prize_parts"]) or "No award"
    out += ["", f"**Decision: {w['proposal_id']} — {prize}.**", ""]
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sim", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.write_text(render(args.sim), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
