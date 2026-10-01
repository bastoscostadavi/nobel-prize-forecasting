# Physics committee private final ballot, version 1

You are one simulated 2026 Nobel Committee for Physics member using
`gpt-6.1-sol` with `high` reasoning effort. For one run, read your own profile,
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
  "model": "gpt-6.1-sol",
  "reasoning_effort": "high",
  "prompt": "prompts/physics_committee_final_ballot_v1.md",
  "ranked_proposal_ids": ["P001", "P000"],
  "top_choice_rationale": "<concise substantive reason>",
  "recusal_note": "<specific connection, or none apparent from profile>"
}
```

Save only `committee/final_ballots/<member-id>.json`. Verify that the ranking is
a strict permutation of every proposal ID in the slate and metadata is exact.
