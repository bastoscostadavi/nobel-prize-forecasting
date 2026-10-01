# Physics experiment design

## Experimental units

Physics uses 12 nomination runs: six from each independently drafted nominator
list.

- `results/physics/claude-opus-5-5/run-1` through `run-6`
- `results/physics/gpt-6-sol/run-1` through `run-6`

The nominator-list directory identifies the source of the nominator sample. It
does not identify the model that later simulates the committee.

## Primary committee arms

Every nomination run is evaluated by both committee models. Each model performs
five independent full committee simulations per run.

| Arm | Model | Reasoning | Simulations per nomination run | Total |
|---|---|---:|---:|---:|
| Claude committee | `claude-sonnet-5-5` | `high` | 5 | 60 |
| OpenAI committee | `gpt-5.6-terra` | `high` | 5 | 60 |

This paired allocation yields 120 full committee simulations. It prevents
nominator-list source from being confounded with committee model.

The required output roots are:

```text
results/physics/<list-id>/run-<n>/committee/claude/sim-01..05/
results/physics/<list-id>/run-<n>/committee/gpt-5.6-terra/sim-01..05/
```

Each full simulation must retain the complete discussion record described in
`docs/PHYSICS_PHASE2.md`: blinded longlist and crosswalk, eight private opening
assessments, shortlist, eight round-1 statements, chair synthesis, eight
round-2 statements, frozen proposal slate, eight private final ballots, tally,
decision, and runtime metadata.

## Global zero-context baseline

A separate comparison arm consists of 60 independent one-shot requests to
`gpt-6.1-sol` at `high` reasoning effort. This arm is global rather than paired
to nomination runs. The complete user content of every request is the same
fixed question: `Who do you predict will win the 2026 Nobel Prize in Physics?`

The one-shot model must not receive or inspect:

- a candidate list or nomination file;
- a nominator-list ID or nomination-run ID;
- committee-member profiles;
- committee prompts, discussions, ballots, or decisions; or
- another one-shot prediction.

## GPT-6 Luna sensitivity arm

To test whether the simulation-based forecast is robust to the OpenAI
committee model, a secondary arm repeats the complete Terra allocation with
`gpt-6-luna` at `high` reasoning effort. GPT-6 Luna was chosen as OpenAI's
efficient focused/high-volume model; the official model page confirms that the
exact `gpt-6-luna` identifier supports `high` reasoning:
https://developers.openai.com/api/docs/models/gpt-6-luna

The arm contains five independent Luna committees for every one of the same 12
nomination runs, for 60 additional full simulations. Candidate inputs,
committee personas, evidence boundaries, substantive prompt instructions,
shortlist rule, discussion structure, proposal construction, and instant-runoff
rule are held fixed. Each model arm has its own deterministic seed namespace,
so the hidden ballot codes and shuffled candidate order are independent
realizations rather than position-matched pairs. This is a model-arm
sensitivity comparison over randomized order, not an exact prompt-token pair.
Its output roots are:

```text
results/physics/<list-id>/run-<n>/committee/gpt-6-luna/sim-01..05/
results/physics/luna_committee_runtime/<list-id>/run-<n>/sim-01..05/
```

The model-locked entry points are `scripts/luna_committee.py` and
`scripts/run_luna_committee_codex.py`. Luna is a sensitivity analysis, not a
replacement for either primary committee arm and not a zero-context baseline.

Outputs are stored independently as:

```text
results/physics/oneshot/gpt-6.1-sol/pred-001/
...
results/physics/oneshot/gpt-6.1-sol/pred-060/
```

Each prediction must record the exact fixed prompt, exact runtime model,
reasoning effort, prediction ID, answer, and concise rationale. The baseline
has no simulated committee discussion and must never be counted as a committee
simulation.

## Counts and comparisons

The complete design produces 240 outputs in total:

- 60 full Claude committee simulations;
- 60 full GPT-5.6 Terra committee simulations;
- 60 full GPT-6 Luna sensitivity committee simulations; and
- 60 GPT-6.1 Sol zero-context one-shot predictions.

The 180 committee simulations and 60 one-shot predictions are distinct
experimental arms. Primary committee comparisons should preserve the shared
nomination-run structure. The Sol baseline is analyzed only as a global
comparison distribution; it has no valid run-level pairing. Terra versus Luna
comparisons must also disclose that the two arms use independent deterministic
candidate-order shuffles rather than position-matched ballot codes.

## Legacy pilot outputs

Six earlier flat committee simulations under the run-level `committee/`
directories used GPT-6.1 Sol. Preserve them as legacy/pilot records. They are
excluded from all four analysis arms, must not be relabeled as GPT-5.6 Terra,
and must not be used as evidence by a new simulation.

## Reproducibility metadata

Every generated artifact must report the actual model identifier and actual
reasoning setting exposed by its runtime. Never infer, substitute, or relabel a
model. Also record the prompt version, output ID, and input identity. For a
committee simulation, the input identity is its nomination-list ID and run. For
the global one-shot baseline, the input identity is the fixed prompt version
and prediction ID only.
