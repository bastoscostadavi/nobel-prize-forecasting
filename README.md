# Nobel Prize Forecasting 2026

Forecast the 2026 Nobel Prizes by **simulating the nominations and the committee deliberations** and aggregating the outcomes over many runs.

## Idea

The simulation mirrors the real process in two stages.

1. **Nomination.** 100 nominator agents, each conditioned on a real physicist's `profile.md`, submit one nomination each. Nominations are merged into a candidate list.
2. **Committee.** One agent per real committee member, each conditioned on that member's `profile.md`, deliberates over the candidate list and votes; a voting rule mirroring the real procedure picks the winner.

Profiles (`agent-data/PROFILE_TEMPLATE.md`, `agent-data/NOMINATOR_PROFILE_TEMPLATE.md`) describe expertise and taste but deliberately contain no nominations or predictions.

Each stage is repeated over several runs; the share of runs a candidate wins is its forecast probability. Scope: Physics first, then Chemistry, Medicine, Economics, Peace (Literature dropped: its real decision is a second vote by the full Swedish Academy).

```
nominator agents ──► nominations ──► candidate list ──► committee agents ──► deliberation ──► ballot ──► winner
                                                                                                         │
                                                         × runs ──► win probabilities ◄──────────────────┘
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
  committee/<member-slug>/   one folder per committee member (profile.md)
  nominators/<list-id>/      one folder per nominator list, named after the model that drafted it
    nominators.csv           the 100 nominators
    list_note.md             how the list was drafted
    <slug>/profile.md        one profile per nominator (NOMINATOR_PROFILE_TEMPLATE.md)
scripts/                     orchestration
results/<category>/<list-id>/
  run-<n>/nominations/       raw nominations from one nomination run
  run-<n>/candidates.csv     merged candidate list for that run
  run-<n>/committee/         committee transcript, ballots, winner
  summary.csv                win share per candidate across runs
```

## Pipeline

Agents are run as Claude Code subagents (no API key needed), each given only its profile and the task.

1. **Nominator list:** a model drafts 100 nominators matching the eligible nominator groups, countries and subfields (`scripts/generate_nominator_list.py`, or a subagent). Physics has lists drafted by Claude Opus 5.5 and GPT-6 Sol.
2. **Nominator profiles:** each nominator gets a web-researched `profile.md` (checked alive and current affiliation; biography, research footprint, persona; no nominations or predictions).
3. **Nomination:** 10 runs × 100 nominator subagents. Each run's nominations are merged into that run's `candidates.csv`.
4. **Committee:** for each run, persona-conditioned member agents give private opening rankings, hold 2–3 discussion rounds with random speaker order and chair summaries, then vote by secret ballot (majority, runoff if needed). Candidate order is shuffled per run.
