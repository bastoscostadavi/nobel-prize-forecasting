# Nobel Prize Forecasting 2026

Forecast the 2026 Nobel Prizes by **simulating the nominations and the committee deliberations** and aggregating the outcomes over many runs.

## Idea

The simulation mirrors the real process in two stages.

1. **Nomination.** 100 nominator agents, sampled to match the nominator population (subfield and country shares from OpenAlex publication data), each read their own `profile.md` and submit one nomination. Nominations are merged into a candidate list.
2. **Committee.** Committee agents deliberate over the candidate list and vote; a voting rule mirroring the real procedure picks the winner.

Each stage is repeated over several runs; the share of runs a candidate wins is its forecast probability. Scope: Physics first, then Chemistry, Medicine, Economics, Peace (Literature dropped: its real decision is a second vote by the full Swedish Academy).

```
nominator agents ──► nominations ──► candidate list ──► committee agents ──► deliberation ──► ballot ──► winner
                                                                                                         │
                                                         × runs ──► win probabilities ◄──────────────────┘
```

## Experiments

| # | Name | Setup |
|---|---|---|
| 1 | One-shot | A single model call per run, asked directly who will win. No agents, no discussion. |
| 2 | Multi-agent discussion | Committee-sized group of agents deliberates and votes, with no persona conditioning (generic "member of the committee"). |
| 3 | Multi-agent in-context | Same as 2, but each agent is conditioned on its member's `profile.md` (the `## Persona` section plus supporting sections). |

Comparing 2 vs 1 isolates the effect of deliberation; 3 vs 2 isolates the effect of personas. Profiles follow `agent-data/PROFILE_TEMPLATE.md` and deliberately contain no forecasts, so 3 vs 2 is not confounded by a prediction baked into the prompt.

## Categories

| Folder | Prize | Deciding body (real world) |
|---|---|---|
| `agent-data/physics/` | Physics | Nobel Committee for Physics → Royal Swedish Academy of Sciences |
| `agent-data/chemistry/` | Chemistry | Nobel Committee for Chemistry → Royal Swedish Academy of Sciences |
| `agent-data/medicine/` | Physiology or Medicine | Nobel Committee → Nobel Assembly at Karolinska Institutet |
| `agent-data/literature/` | Literature | Nobel Committee → Swedish Academy |
| `agent-data/peace/` | Peace | Norwegian Nobel Committee |
| `agent-data/economics/` | Economic Sciences (Riksbank Prize) | Committee for the Prize → Royal Swedish Academy of Sciences |

> Open design question: in most categories a small committee proposes and a larger body ratifies. We start by simulating the committee only, and may add a second-stage ratifying vote later.

## Repository layout

```
agent-data/<category>/
  committee/<member-slug>/   one folder per committee member (profile.md)
  nominators/
    frame/                   sampling frame: OpenAlex subfield/region shares, KVA physics
                             class, living laureates, Nordic professor estimate, fetch scripts
    <list-id>/<slug>/        one profile.md per nominator (NOMINATOR_PROFILE_TEMPLATE.md),
                             e.g. oneshot-claude/ = profiles for the Claude one-shot list
scripts/                     orchestration
results/<category>/
  nominators/                nominator lists produced by models (e.g. one-shot baseline)
  <candidate-list-id>/       one folder per way of producing a candidate list
    nominations/             raw nominations
    candidates.csv           merged candidate list
    winners/<experiment>/    runs/<run_id>.json + summary.csv (win share per candidate)
```

## Pipeline

Agents are run as Claude Code subagents (no API key needed), each given only its profile and the task, with no web access.

- **Stage 1 (nomination):** 10 runs × 100 nominator subagents. Each run's nominations are merged into `results/<category>/<candidate-list-id>/candidates.csv`.
- **Nominator lists:** a model is asked in one shot for 100 representative nominators (`scripts/oneshot_nominators.py` via API, or a single subagent), saved to `results/<category>/nominators/oneshot_<model>_<date>.csv`. Physics has lists from Claude Opus 5.5 and GPT-6 Sol. These are compared against the OpenAlex-based frame in `agent-data/<category>/nominators/frame/`.
- **Nominator profiles:** each nominator on a list gets a web-researched `profile.md` (verified alive and affiliation, biography, research footprint, persona with no nominations or predictions). Done for the Claude physics list.
- **Stage 2 (committee):** private opening rankings, 2–3 discussion rounds with random speaker order and chair summaries, then a secret ballot (majority, runoff if needed). Candidate order is shuffled per run. Run-to-run variation comes from shuffling and model sampling (temperature is not controllable on most frontier models).
