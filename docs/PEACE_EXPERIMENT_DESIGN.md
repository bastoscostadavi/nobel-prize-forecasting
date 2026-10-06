# 2026 Peace committee experiment

Launched 6 October 2026. Each model has **25 committee simulations**: five neutral profile versions, with five independent repetitions per version. The models are **GPT-5.6 Terra/high** and **Claude Sonnet 5.5/high**, following the preceding committee experiments. There are 50 simulations across both models.

## Fixed inputs and pairing

Both models use Claude's consolidated `agent-data/peace/candidates/candidates.json`: 47 achievement-centered entries and their credited recipient pools. No additional trimming or nomination stage is performed here. An award can name at most three individuals and/or organizations across the entire configuration; a credit pool is not an automatic shared award.

The voting members are Jørgen Watne Frydnes (chair), Asle Toje, Anne Enger, Kristin Clemet and Gry Larsen. The non-voting secretary Kristian Berg Harpviken is excluded from voting and simulated discussion. A majority requires three votes.

| Simulation IDs, in each model cohort | Profile file for every member | Repetitions |
|---|---|---|
| sim-01–05 | profile_terra_v1.md | 5 |
| sim-06–10 | profile_terra_v2.md | 5 |
| sim-11–15 | profile_terra_v3.md | 5 |
| sim-16–20 | profile_terra_v4.md | 5 |
| sim-21–25 | profile_terra_v5.md | 5 |

The `terra` filenames identify the neutral editorial profiles; **both models receive the same versions**. The builder retains factual wording, quotations, links and caveats while varying headings, section order and paragraph presentation. Persona instructions and unsupported preference inferences are removed uniformly. Original `profile.md` files remain intact. See `agent-data/peace/committee/terra_profiles.md` and the hash manifest beside it.

Candidate ordering is deterministically shuffled by simulation ID using a common seed prefix. The same-numbered simulations in the two model cohorts receive identical blinded candidate packets. Model-specific prompts differ in execution identifiers and checker paths. Each metadata file freezes the candidate source, profile and prompt hashes and records `profile_version` and `repeat_index`. The legacy `run=1` denotes the common candidate-input run; repetition is identified by `simulation_id` and `repeat_index`.

Blinded packets contain only ballot IDs, achievement text, field and credited names. For compatibility with existing validators, achievement and field are stored as `discovery` and `subfield`. Source IDs, draft model provenance, nomination labels and consolidation flags are absent from the model packets. Public knowledge may inform assessments; the protocol requires uncertainty and prohibits claims of confidential proceedings or source verification.

## Protocol and execution

Each committee performs five private opening rankings, a deterministic shortlist, five round-one statements, the chair's synthesis, five round-two statements, a deterministic proposal slate and five exhaustive private ballots. The shared instant-runoff implementation selects the winning configuration. The shortlist rule is inherited from previous experiments: a first-place ranking, two top-three rankings, or three top-eight rankings qualifies automatically, with deterministic filling to at least eight candidates.

Every model request starts a new session in an empty temporary directory. Tools, browsing, external apps and subagent creation are disabled. Only that member's assigned profile and the allowed stage files are embedded. The coordinator validates and publishes the returned JSON. No model can access another simulation, the other model cohort, the source crosswalk or future-stage files. Each attempt preserves the prompt, evidence hashes, raw output, errors and execution metadata.

The dispatchers process the 25 committees sequentially within each model cohort, with up to three concurrent member requests. Both model cohorts run independently. Valid existing artifacts are checked and reused on resumption; a failed attempt is retained separately and cannot enter the canonical result. There is no model fallback. Conflict notes are disclosed but do not change the five-vote simulation roster.

## Files and resumption

- `scripts/peace_committee.py`: model-locked packet preparation and shared stage validation, shortlist, slate and tally.
- `scripts/claude_peace_committee.py`: Claude entry point to the same protocol.
- `scripts/run_peace_committee_codex.py` and `scripts/run_peace_committee_claude.py`: independent model dispatchers.
- `scripts/launch_peace_cohort.py`: starts one detached cohort and records its deployment.
- `results/peace/committee/gpt-5.6-terra/sim-NN/` and `results/peace/committee/claude-sonnet-5-5/sim-NN/`: canonical simulation records.
- `results/peace/{terra,claude}_committee_progress.json`: current run and stage counts.
- `results/peace/{terra,claude}_committee_runtime/`: isolated request audit trails.
- `results/peace/{terra,claude}_committee_summary.json`: pooled and per-profile summaries as committees complete.

To resume a stopped cohort, use the relevant command below with the existing frozen inputs. The dispatcher lock prevents concurrent duplicate execution.

```sh
python3 scripts/run_peace_committee_codex.py run --sims 1-25 --candidates agent-data/peace/candidates/candidates.json --jobs 3 --max-attempts 2
python3 scripts/run_peace_committee_claude.py run --sims 1-25 --candidates agent-data/peace/candidates/candidates.json --jobs 3 --max-attempts 2
```

An initial sandboxed Terra launch failed before model calls because the account runtime could not initialize. The authorized detached launch with runtime access succeeded; the earlier failed attempts remain in the audit trail. Neither failed requests nor pending simulations are results.

## Validation and interpretation

The launch preparation passed 28 offline tests covering the five-member roster, majority of three, fixed five-by-five assignment, paired model packets, full candidate coverage, immutable inputs, isolation boundaries, model locking, Claude runtime auditing, rejection handling and aggregation. The profile builder verifies identical retained fact-token, quotation and source-link inventories across all versions. Actual first-stage responses from both cohorts also passed the schema validators before launch was reported successful.

Report results for each profile version and each model as well as the aggregate. Each profile has equal weight; summaries do not silently count missing results as losses. Frequencies describe this experiment and are not calibrated probabilities of the Nobel Committee's decision. Editorial variants test presentation sensitivity while holding the factual record fixed.

## Independent one-shot arm

On 6 October 2026, 50 GPT-6.1 Sol/high forecasts were launched and completed. This arm receives only the versioned question in `prompts/peace_oneshot_gpt_6_1_sol_v1.txt`; it does not receive candidate or committee context. Every request uses a fresh ephemeral Codex CLI session in an empty temporary directory with tools disabled. All 50 requests have distinct conversation IDs. Responses are retained verbatim, and primary-pick transcriptions include exact supporting excerpts and SHA-256 hashes. They are analyzed separately from committee decisions.

The one-shot arm is prepared and validated by `scripts/peace_oneshot.py`, dispatched by `scripts/run_peace_oneshot_codex.py`, and transcribed with `scripts/transcribe_peace_oneshot_sol.py`. All 50 answers passed validation. No extra model calls were used to transcribe or aggregate the primary predictions. The details README includes the completed comparison.

The completed Claude Opus 5.5/high one-shot arm also contains 50 forecasts, using the same user question and an additional JSON-format system instruction. Each saved structured answer was matched to a successful raw runtime response, with the Opus model identity, empty tool configuration and distinct session ID verified. Three exact recipient-name aliases are grouped without changing source answers. Both arms select Sudan's Emergency Response Rooms in all 50 forecasts and appear side by side in the details README. `scripts/summarize_peace_oneshot_claude.py` reproduces the Opus validation summary; `scripts/plot_peace_oneshot.py` reproduces both figures. These 100 one-shot forecasts remain separate from the 50 committee decisions.
