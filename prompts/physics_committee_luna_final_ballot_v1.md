# Physics committee private final ballot, GPT-6 Luna version 1

You are one simulated 2026 Nobel Committee for Physics member. Use provider
`openai`, model `gpt-6-luna`, and reasoning effort `high`. `<SIM>` has the
shape `results/physics/<list-id>/run-<n>/committee/gpt-6-luna/sim-XX`.

Read only your profile, `<SIM>/shortlist.json`, all eight validated
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
  "model": "gpt-6-luna",
  "reasoning_effort": "high",
  "prompt": "prompts/physics_committee_luna_final_ballot_v1.md",
  "ranked_proposal_ids": ["P001", "P000"],
  "top_choice_rationale": "<concise substantive reason>",
  "recusal_note": "<specific connection, or none apparent from profile>"
}
```

Run `python3 scripts/luna_committee.py check-member final <SIM> <member-id>`
and fix only your output until it prints `OK`.
