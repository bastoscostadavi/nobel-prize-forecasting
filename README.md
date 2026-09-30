# Nobel Prize Forecasting 2026

Forecast the 2026 Nobel Prizes by **simulating the committee deliberations** and aggregating the outcomes over many runs.

## Idea

1. Each prize category has a committee. Each committee member is modelled as an LLM agent with a persona (field, institution, known scholarly leanings, past nominations and statements, voting record where public).
2. For each simulation, the agents are given the same candidate shortlist and dossiers, **discuss over several rounds**, then **cast a vote**.
3. A voting rule that mirrors the real procedure turns the votes into a winner (or shared winners).
4. Repeat **1000 times** per category. The share of runs each candidate wins is its forecast probability.

```
candidates + dossiers ──► committee agents ──► deliberation rounds ──► secret ballot ──► winner
                                   ▲                                                       │
                                   └───────────────── ×1000 runs ──► win probabilities ◄───┘
```

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
  committee/<member-slug>/   one folder per committee member = that agent's data
                             (profile.md, persona prompt, sources, notes)
  candidates/                shortlist + dossiers for that category (to be built)
scripts/                     orchestration (to be built)
runs/                        raw transcripts and votes from every simulation
results/                     aggregated probabilities per category
```

## Planned pipeline (`scripts/`)

- `build_personas` – turns each `committee/<member>/profile.md` into a persona prompt in that same member folder.
- `simulate` – runs one deliberation: N rounds of discussion, then structured votes; writes to `runs/`.
- `run_batch` – repeats `simulate` 1000× per category with varied seeds/temperature and speaker order.
- `aggregate` – counts winners across runs, outputs probabilities with uncertainty to `results/`.

## Caveats

- Nobel deliberations are secret for 50 years. Personas are built only from public information and are an approximation.
- Probabilities reflect the model's simulated behaviour, not ground truth. We should backtest on past years (e.g. 2015–2025) to check calibration.
- Committee rosters were compiled from public sources; verify against nobelprize.org before relying on them.
