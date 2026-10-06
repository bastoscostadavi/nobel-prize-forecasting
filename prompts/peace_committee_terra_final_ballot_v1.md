# Peace committee private final ballot, GPT-5.6 Terra version 1

The supplied longlist contains 47 achievement-centered Peace candidate entries.
The nominator stage was omitted. Five simulated voting members participate:
`frydnes-jorgen-watne` (chair), `toje-asle`, `enger-anne`, `clemet-kristin`, and
`larsen-gry`. A majority requires three votes. Secretary Kristian Berg Harpviken
is nonvoting and absent from these deliberations. This is a forecasting
abstraction, not a claim about confidential proceedings.

Use only the assigned neutral `profile_terra_vN.md` snapshot, where N is the
coordinator-supplied profile version (1 through 5), for either model. Profiles
contain public biographical facts and attributed public statements. Do not
invent temperament, political preferences, voting habits, personal motives, or
confidential committee knowledge. Apply common criteria across all fields;
expertise, political affiliation, and source-list membership do not establish
candidate merit. Conflicts are disclosed but not adjudicated.

Assess contributions toward fraternity among nations, reduction of armed forces,
and promotion of peace, anchored in Nobel's will. Weigh demonstrated peace
outcomes, human rights and democracy, international law, disarmament, and
humanitarian work as relevant to the particular achievement. Distinguish
lasting outcomes from publicity, intentions, or unsupported causal claims.
Assess the specific achievement, defensible attribution, durability and timing,
and uncertainty using supplied evidence and clearly identified existing public
knowledge. Do not claim access to confidential nominations or decisions. Public
nomination reports are not evidence of committee endorsement.

For compatibility with the shared packet and validators, `discovery` means
Peace achievement, `subfield` means Peace field, and the chair-summary key
`scientific_disputes` means substantive disputes about peace merit and outcomes.
These are compatibility labels for the Peace assessment. Candidate
`credited_names` can name individuals and organizations. An entry may pool
several associated actors; this does not imply they deserve a joint award.
Choose exact credited names only when their contributions support coherent,
defensible credit. Across an entire prize configuration, award at most three
unique individuals and/or organizations total, including repeated names across
parts only once.

The integer `run` remains 1 for compatibility with the candidate nomination-run
identity. The coordinator assigns independent `sim-NN` simulations, grouped into
five profile versions with five repeats per version; `profile_version` and
`repeat_index` identify that design in coordinator metadata. Never inspect
another repeat or profile to influence this one. Keep output JSON keys exactly
as shown; do not add profile-version or repeat-index keys to stage output.

You are one simulated 2026 Norwegian Nobel Committee member. Use provider
`openai`, model `gpt-5.6-terra`, and reasoning effort `high`. Record the assigned `list_id`, `simulation_id`, and integer `run` (always 1).
`<SIM>` has the
shape `results/peace/committee/gpt-5.6-terra/sim-NN`.

Confirm execution settings in `<SIM>/metadata.json` only, then read only your assigned profile, `<SIM>/shortlist.json`, all five validated
`<SIM>/round2/*.json` files, and `<SIM>/proposal_slate.json`. Do not read
opening ballots, round-1 files, other final ballots, tally files, source
nominations, consolidation files, the ballot map, another profile, another
simulation or run, or external sources.

Privately rank every proposal ID exactly once from most to least preferred.
Judge achievement, maturity, attribution, and citation scope rather than visible
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
  "model": "gpt-5.6-terra",
  "reasoning_effort": "high",
  "prompt": "prompts/peace_committee_terra_final_ballot_v1.md",
  "ranked_proposal_ids": ["P001", "P000"],
  "top_choice_rationale": "<concise substantive reason>",
  "recusal_note": "<specific connection, or none apparent from profile>"
}
```

Run `python3 scripts/peace_committee.py check-member final <SIM> <member-id>`
and fix only your output until it prints `OK`.

The coordinator assigns the profile version N explicitly; use that exact profile
path and never substitute or inspect another version. Write only the assigned
output file. Do not modify the profile, packet, or earlier-stage records. Do not
read other models' simulations, other simulations or runs, or future-stage files;
do not consult or message other agents outside the validated stage files. Do not
use the web.
