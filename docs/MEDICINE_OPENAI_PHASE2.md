# OpenAI Medicine committee simulations

The Medicine simulation uses the reviewed common candidate list and the six neutral, in-place `agent-data/medicine/committee/<member-id>/profile.md` files. The nominator stage is omitted. Execution uses OpenAI `gpt-5.6-terra` with `high` reasoning, matching the Physics Terra arm.

The dispatcher accepts the coordinator's canonical input path explicitly. The selected simulation range and any candidate exclusions must agree with the user-approved allocation and the comparison arm. Exclusions are recorded by canonical candidate ID in every simulation's metadata; the dispatcher never silently drops an entry. The source list is preserved.

## Protocol

Each independent simulation saves six private top-eight opening rankings, a deterministic union shortlist, six first-round statements, a neutral chair summary by Per Svenningsson, six second-round statements, a deterministic configuration slate, six private exhaustive final ballots, and an instant-runoff decision. The shortlist, configuration grouping, and tally use the shared Physics implementation. An award can include one or two achievements with no more than three unique recipients total. No award is always available on the final slate.

The six-person Committee is treated as the effective deciding body, including the Secretary-General as a simulated voter. A majority is four. Nobel Assembly ratification is outside this forecasting abstraction. To preserve comparison with the Physics procedure, conflicts are disclosed but not adjudicated, and all six ballots count. This run-specific policy governs the simulation even where the earlier candidate handoff proposed a different recusal approach. Linnarsson's documented spatial-transcriptomics coauthorship remains relevant to disclosure.

Every member request runs in a fresh ephemeral session, with tools and external browsing disabled. The dispatcher embeds only that member's profile and the evidence permitted at the current stage. The coordinator-only crosswalk, source dossier, other profiles, other simulations, and other private final ballots are excluded. General scientific knowledge can inform assessment; agents must identify uncertainty and cannot claim independent verification. The public-evidence cutoff is 2 October 2026.

## Integrity and resumption

The coordinator freezes the canonical candidate input, all six profiles, and all five stage prompts by SHA-256. Neutral packets preserve all eligible entries and exact credited-name strings, alphabetize names, and use a reproducible per-simulation shuffle. Validators check the packet, output schemas, identities, attribution pools, recipient limits, supporter claims, and deterministic derived artifacts. Each accepted response has a runtime audit containing execution settings, permitted-evidence hashes, token usage, and rejected attempts when applicable.

Prepared inputs cannot be replaced. Resumption validates and reuses accepted outputs; incomplete stages request only missing member artifacts. An unresolved failure stops the batch and records its status rather than generating the remaining simulations from a broken setup. A process lock prevents a duplicate dispatcher. Outcome summaries combine canonical candidate IDs and recipient sets rather than shuffled ballot IDs. Frequencies describe completed simulations, not calibrated probabilities.

## Files and commands

- Coordinator: `scripts/medicine_committee.py`
- Dispatcher: `scripts/run_medicine_committee_codex.py`
- Stage prompts: `prompts/medicine_committee_terra_*_v1.md`
- Simulations: `results/medicine/committee/gpt-5.6-terra/sim-NN/`
- Runtime audit: `results/medicine/terra_committee_runtime/`
- Progress: `results/medicine/terra_committee_progress.json`
- Summary: `results/medicine/terra_committee_summary.json`

Run `python3 scripts/run_medicine_committee_codex.py run --candidates <canonical-path> --sims <approved-range> --jobs 3`, adding `--exclude <candidate-id>` only for approved exclusions. Reuse the same arguments to resume. Use the dispatcher's `validate` command with the same simulation range to check completed results. The `plan` command is read-only and does not make model requests.
