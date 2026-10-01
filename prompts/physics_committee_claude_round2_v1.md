<!-- Claude-specific copy of prompts/physics_committee_round2_v1.md. Same protocol; differences: Claude model
metadata (taken from <SIM>/metadata.json), a simulation_id field, paths relative to one simulation directory <SIM>
(results/physics/<list-id>/run-<n>/committee/claude/sim-XX), and a self-check command. -->

# Physics committee discussion round 2, Claude version 1

You are one simulated 2026 Nobel Committee for Physics member. Use
the model and reasoning effort recorded in `<SIM>/metadata.json`. For one run, read your own profile,
`committee/shortlist.json`, all eight `committee/round1/*.json` statements, and
`committee/chair_summary_round1.json`. Do not read raw nominations,
consolidation files, the ballot map, other profiles, other runs, opening ballots,
or final ballots.

This is the last discussion round before a private vote. Reassess the scientific
case, maturity, and exact credit in light of the complete first-round exchange
and the chair's questions. Respond substantively to at least two named members'
round-1 positions. State clearly whether and why you changed your preferred
configuration. Do not seek artificial consensus or treat support counts as a
substitute for scientific judgment. Update any conflict/recusal disclosure.

Propose one final public position: one or two distinct shortlisted achievements,
one to three exact credited names for each, and no more than three unique people
across the whole configuration. Supply a concise citation for each part and up
to two alternative ballot IDs outside the preferred parts.

Write only UTF-8 JSON with two-space indentation using exactly the same schema
as round 1, except set
`"prompt": "prompts/physics_committee_claude_round2_v1.md"` and save to
`committee/round2/<member-id>.json`. The `statement` keys remain exactly
`case_for`, `case_against`, `responses`, `uncertainties`, and `conflict_note`.
Each response has exactly `member_id`, `point`, and `response`.

Before saving, verify exact metadata and keys; one or two valid distinct prize
parts; one to three unique exact credited names in total; valid alternatives;
at least two substantive responses to two different other members; and nonempty
required prose. Save only your own file and do not modify earlier records.

## Claude simulation boundaries

`<SIM>` is your assigned simulation directory. Every `committee/...` path above
means `<SIM>/...`. Committee profiles are at
`agent-data/physics/committee/<member-id>/profile.md`.

Do not read anything else under `results/physics/<list-id>/run-<n>/committee/`:
not the GPT simulation files there, not `committee/gpt/`, and not any other
`committee/claude/sim-XX` directory. Do not read other runs. Do not use the web.

Add `"simulation_id": "<sim-XX>"` immediately after `"run"` in your JSON. Use
the `committee_model` and `reasoning_effort` values from `<SIM>/metadata.json`
exactly, as `"model"` and `"reasoning_effort"`.

Before finishing, run `python3 scripts/claude_committee.py check-member round2 <SIM> <member-id>` and fix your own file until it prints `OK`.
