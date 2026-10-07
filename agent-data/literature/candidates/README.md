# 2026 Literature simulation candidate list

Both completed committee cohorts use **the same 50 writers** in `codex/candidates.json`, with candidate source hashes verified across all 25 paired GPT and Claude simulations. The list is writer-centered, with one author and body of work per entry. It was selected by Codex from a 190-writer coverage draft at the user’s request. A separate Claude candidate draft was not merged into this experiment.

- `codex/candidates.json`, `candidates.csv` and `candidates.md`: the active frozen 50-writer input and readable views.
- `codex/selection_50.json`: reasons for retaining each writer and contextual sources.
- `codex/coverage-190.json`, `coverage-190.csv` and `recovered_seed.json`: the original coverage archive.
- `codex/trimmed_entries.json`: complete accounting for the 140 removals: 139 comparative forecasting cuts and one confirmed eligibility exclusion.
- `merge/consolidate.py`: an unused future merge tool. It requires actual independent drafts and explicit reviewed dispositions; it never invents a second draft or changes a frozen list.

The output is alphabetical and original candidate IDs are retained; neither is a ranking. Candidate selection is an author forecasting judgment, not a list of actual nominations or calibrated probabilities. Eligibility/status review was targeted and the original literary summaries are retained with their stated verification limits. Geographic labels describe contexts rather than verified citizenship.

Simulation packets omit selection judgments, market evidence, source-model provenance, reservations and source crosswalks. Only shuffled ballot IDs, literary contribution and representative works, genre/language, and the exact writer name are embedded. Every simulation freezes candidate, profile and prompt hashes. A later change to the source must belong to a separate experiment rather than silently replacing this input.
