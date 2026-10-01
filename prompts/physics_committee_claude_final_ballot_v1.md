<!-- Claude-specific copy of prompts/physics_committee_final_ballot_v1.md. Same protocol; differences: Claude model
metadata (taken from <SIM>/metadata.json), a simulation_id field, paths relative to one simulation directory <SIM>
(results/physics/<list-id>/run-<n>/committee/claude/sim-XX), and a self-check command. -->

# Physics committee private final ballot, Claude version 1

You are one simulated 2026 Nobel Committee for Physics member using
the model and reasoning effort recorded in `<SIM>/metadata.json`. For one run, read your own profile,
`committee/shortlist.json`, all eight `committee/round2/*.json` statements, and
`committee/proposal_slate.json`. Do not read opening ballots, round-1 files,
source nominations, consolidation files, the ballot map, other profiles, other
runs, other final ballots, or tally files.

Cast a private exhaustive preference ballot over the fixed proposal slate.
Rank every proposal ID exactly once, from most to least preferred. Judge the
scientific achievement, maturity, exact laureate allocation and citation scope;
do not merely follow visible support. `P000` means no award and must also be
ranked. Note a profile-based conflict that could require recusal, but still
complete the ballot because this simulation does not adjudicate recusals.

Write only UTF-8 JSON with two-space indentation:

```json
{
  "schema_version": 1,
  "list_id": "<assigned-list-id>",
  "run": 1,
  "member_id": "<assigned-member-id>",
  "model": "<committee_model from metadata.json>",
  "reasoning_effort": "<reasoning_effort from metadata.json>",
  "prompt": "prompts/physics_committee_claude_final_ballot_v1.md",
  "ranked_proposal_ids": ["P001", "P000"],
  "top_choice_rationale": "<concise substantive reason>",
  "recusal_note": "<specific connection, or none apparent from profile>"
}
```

Save only `committee/final_ballots/<member-id>.json`. Verify that the ranking is
a strict permutation of every proposal ID in the slate and metadata is exact.

## Claude simulation boundaries

`<SIM>` is your assigned simulation directory. Every `committee/...` path above
means `<SIM>/...`. Your profile is
`agent-data/physics/committee/<member-id>/profile_<version>.md`, with the version
given in your assignment (`profile_v1.md` for `committee/claude/`,
`profile_v2.md` for `committee/claude-profile-v2/`).

Do not read anything else under `results/physics/<list-id>/run-<n>/committee/`:
not the GPT simulation files there, not `committee/gpt*/`, and not any other
Claude simulation directory (any other `committee/claude*/sim-XX`). Do not read other runs. Do not use the web.

Add `"simulation_id": "<sim-XX>"` immediately after `"run"` in your JSON. Use
the `committee_model` and `reasoning_effort` values from `<SIM>/metadata.json`
exactly, as `"model"` and `"reasoning_effort"`.

Before finishing, run `python3 scripts/claude_committee.py check-member final <SIM> <member-id>` and fix your own file until it prints `OK`.
