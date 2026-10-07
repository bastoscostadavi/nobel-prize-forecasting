# 2026 Literature committee and one-shot experiments

Final records are published in `results/literature/`: 25 GPT-5.6 Terra/high committee simulations, 25 Claude Sonnet 5.5/high committee simulations, 25 independent GPT-6.1 Sol/high forecasts and 25 independent Claude Opus 5.5/high forecasts. Committee outcomes and one-shot forecasts are summarized separately.

## Fixed design

The requested experiment has 25 GPT-5.6 Terra/high committees and 25 Claude Sonnet 5.5/high committees, matching the Peace model choices. Each cohort has five repetitions of each of five neutral profile versions. Same-numbered committees in the two model cohorts receive the same profile version and deterministic candidate shuffle.

| Simulation IDs in each cohort | Profile version | Repetitions |
|---|---|---|
| sim-01–05 | 1 | 5 |
| sim-06–10 | 2 | 5 |
| sim-11–15 | 3 | 5 |
| sim-16–20 | 4 | 5 |
| sim-21–25 | 5 | 5 |

Each simulation includes Anders Olsson (chair), Ellen Mattson, Anne Swärd, Steve Sem-Sandberg, Anna-Karin Palm and co-opted Ingrid Carlberg. For this experiment all six vote; the majority is four. Carlberg’s actual committee voting status is undocumented, so including her vote is an explicit modeling assumption. The full Swedish Academy’s final decision is not simulated. The outcome represents a committee recommendation under this abstraction.

All five profiles per member contain identical retained facts, statements, quotations, links and source caveats, with editorial changes to headings and block order. Persona instructions and inferred literary tastes are removed from every version. Original profiles remain intact. The builder and hash manifest are documented in `agent-data/literature/committee/terra_profiles.md`.

## Candidate input and protocol

Both committee cohorts use the same frozen `agent-data/literature/candidates/codex/candidates.json` (list ID `literature-2026-codex-50`). This is the Codex-curated 50-writer selection from an archived 190-person coverage draft, not a merger with a separate Claude candidate draft. The completed records verify identical candidate source hashes, member/profile inputs and candidate shuffles for all 25 paired simulations. No nomination stage is used. Current public contender discussion informed the author’s curation; market evidence, selection reasons, source provenance and reservations were omitted from model packets and never used as voting weights. Blinded packets contain only ballot ID, literary contribution and representative works (`discovery`), genre/language (`subfield`) and exact writer name (`credited_names`). Compatibility JSON keys retain their established spelling; prompts explain their Literature meanings.

This experiment selects one writer and oeuvre per award, using one prize part and one exact credited name. This scope reflects modern single-laureate practice; it does not assert that historical shared Literature awards were prohibited. The no-award proposal remains available.

Each committee performs six private opening top-eight rankings, deterministic shortlisting, six round-one statements, a chair synthesis, six round-two statements, a deterministic proposal slate and six exhaustive private ballots. The inherited instant-runoff tally requires four votes. Shortlisting uses the established rules: a first-place ranking, two top-three rankings or three top-eight rankings qualifies automatically, with deterministic filling to at least eight.

Every request starts a fresh session in an empty temporary directory, with tools and browsing disabled. It receives only its assigned profile and permitted stage evidence. The coordinator validates the exact model identity, schema and inputs, and preserves every attempt’s raw response, errors, evidence hashes and execution metadata. An invalid output cannot enter the canonical result. Resumption reuses valid artifacts; no model fallback is allowed.

## Execution and reproduction

Each stage uses a new tools-disabled session with only the permitted member/stage evidence. The OpenAI committee dispatcher ran one member request at a time; the Claude dispatcher used up to three. The scripts keep separate locks and directories and support resumption without changing validated inputs. The optional `--after-peace` scheduling gate remains available; the completed Literature experiment ran concurrently with the remaining Peace work.

The launch helper defaults to a future reviewed common list but accepts an explicit independent source with `--candidates`. Reproduce these experiments with the frozen source explicitly:

```sh
python3 scripts/run_literature_committee_codex.py run --sims 1-25 --candidates agent-data/literature/candidates/codex/candidates.json --jobs 1 --max-attempts 2
python3 scripts/run_literature_committee_claude.py run --sims 1-25 --candidates agent-data/literature/candidates/codex/candidates.json --jobs 3 --max-attempts 2
python3 scripts/summarize_literature_committees.py
```

The existing scripts validate canonical stage JSON and recompute every shortlist, proposal slate and instant-runoff decision. `results/literature/final_summary.json` freezes all 50 decision and metadata hashes and reports aggregate, per-model and per-profile counts. Every profile has five runs, so pooled and equal-profile-weight frequencies coincide. These are experimental frequencies, not calibrated probabilities of the actual Academy’s decision.

## Independent one-shot baselines

The Sol and Opus questions are identical:

> Who will win the 2026 Nobel Prize in Literature? Predict the laureate and the literary achievement. Answer from your own knowledge only; do not search the web or read any files.

Each forecast used a new conversation in an empty temporary directory with tools and browsing disabled. Neither arm received the 50-writer list, profiles or committee records. Sol received only the versioned user question and returned free-form text; Opus also received a system instruction requesting the three JSON fields `laureate`, `achievement` and `rationale`. This output-format difference is documented rather than treated as a fully identical model comparison.

Sol’s 25 primary picks were transcribed clerically from the explicit opening sentence. Exact source excerpts, names and SHA-256 hashes are retained; alternative names would not be counted. No extra model calls were used for transcription. Runtime events confirm fresh sessions and no tool activity. The Codex CLI records the requested model but does not independently expose a returned model alias; this limitation is retained in the summary. The Opus audit matches each saved JSON answer to its raw runtime, checks the actual model identifier and rejects conversation reuse or tool activity.

```sh
python3 scripts/literature_oneshot.py prepare
python3 scripts/launch_literature_oneshot.py
python3 scripts/transcribe_literature_oneshot_sol.py
python3 scripts/summarize_literature_oneshot_claude.py
python3 scripts/plot_literature_results.py
```

Saved Sol answers are under `results/literature/oneshot/gpt-6.1-sol/`; the Opus answers are under `results/literature/oneshot/claude-opus-5-5/`. Model changes and context changes are confounded when comparing one-shot and committee outcomes; the experiment does not isolate a causal effect of deliberation.
