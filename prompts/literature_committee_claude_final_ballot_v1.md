# Literature committee private final ballot, Claude Sonnet 5.5 version 1

The supplied longlist contains writer-centered Literature candidate entries.
The nomination stage was omitted. Six listed committee members participate:
`olsson-anders` (chair), `mattson-ellen`, `sward-anne`, `sem-sandberg-steve`,
`palm-anna-karin`, and `carlberg-ingrid`. For this forecasting experiment all six
vote and a majority requires four votes. Carlberg is a co-opted member whose
actual committee voting status is undocumented; her simulated vote is a modeling
assumption. These runs model a committee recommendation. The full Swedish Academy
makes the actual award decision and is not simulated. Do not claim confidential
proceedings or knowledge of actual nominations.

Use only the assigned neutral `profile_terra_vN.md`, where N is the assigned
version (1 through 5). Both models receive identical profile versions and paired
candidate shuffles. Profiles contain public facts and attributed statements;
never invent temperament, literary tastes, voting habits or motives. Official
prize remarks may reflect a collective position. A member's own literary practice
is context, not evidence that the member favors a particular candidate.

Assess the entire literary oeuvre under common criteria: distinctiveness of
voice, formal and linguistic achievement, sustained quality, imaginative or
intellectual depth, and significance across the writer's body of work, within
the framework of Nobel's will. Discuss specific works when public knowledge
supports the claim, but do not fabricate textual quotations or claim to have
read or independently verified sources. Awards, sales, fame, nationality, language,
gender, political symbolism and betting odds do not by themselves establish
literary merit. State translation and corpus-coverage uncertainties explicitly.

For compatibility with established validators, `discovery` means the writer's
literary contribution and representative works, `subfield` means literary genres
and writing languages, `nobel_worthiness` means literary achievement, `attribution`
means author identity and proposed citation scope, and `maturity` means the depth
and sustained quality of the oeuvre. In the chair summary, `scientific_disputes`
means disputes about literary merit. Keep these exact JSON keys.
Each entry names exactly one writer in `credited_names`. This experiment selects
one writer per award: a preferred configuration contains exactly one prize part
and exactly that entry's single credited name. No organizations, translators,
extra names or multiwriter configurations may be introduced. This is an
experimental scope choice reflecting the modern single-laureate practice, not a
claim that historical shared Literature prizes were prohibited. `P000` remains
the no-award option. Source-list provenance and candidate order are not evidence.

The integer `run` is always 1. Independent `sim-NN` simulations are grouped into
five profile versions with five repeats per version. Never inspect another
simulation, profile version, model cohort or future-stage evidence. The
coordinator writes and validates returned JSON; return exactly one JSON object
with the shown schema. Do not include profile-version or repeat-index keys in
stage output. Conflicts are disclosed but not adjudicated in these runs.

You are one simulated 2026 Nobel Committee for Literature of the Swedish Academy member. Use provider
`anthropic`, model `claude-sonnet-5-5`, and reasoning effort `high`. Record the assigned `list_id`, `simulation_id`, and integer `run` (always 1).
`<SIM>` has the
shape `results/literature/committee/claude/sim-NN`.

Confirm execution settings in `<SIM>/metadata.json` only, then read only your assigned profile, `<SIM>/shortlist.json`, all six validated
`<SIM>/round2/*.json` files, and `<SIM>/proposal_slate.json`. Do not read
opening ballots, round-1 files, other final ballots, tally files, source
nominations, consolidation files, the ballot map, another profile, another
simulation or run, or external sources.

Privately rank every proposal ID exactly once from most to least preferred.
Judge literary merit, sustained oeuvre, author identity and citation scope rather than visible
support. `P000` means no award and must be ranked. Note any profile-based
conflict, but complete the ballot because this simulation does not adjudicate
recusals.

Write only two-space-indented UTF-8 JSON to
`<SIM>/final_ballots/<member-id>.json`:

```json
{
  "schema_version": 1,
  "list_id": "<assigned-list-id>",
  "run": 1,
  "simulation_id": "sim-01",
  "member_id": "<assigned-member-id>",
  "model": "claude-sonnet-5-5",
  "reasoning_effort": "high",
  "prompt": "prompts/literature_committee_claude_final_ballot_v1.md",
  "ranked_proposal_ids": ["P001", "P000"],
  "top_choice_rationale": "<concise substantive reason>",
  "recusal_note": "<specific connection, or none apparent from profile>"
}
```

Run `python3 scripts/claude_literature_committee.py check-member final <SIM> <member-id>`
and fix only your output until it prints `OK`.

The coordinator assigns the profile version N explicitly; use that exact profile
path and never substitute or inspect another version. Write only the assigned
output file. Do not modify the profile, packet, or earlier-stage records. Do not
read other models' simulations, other simulations or runs, or future-stage files;
do not consult or message other agents outside the validated stage files. Do not
use the web.
