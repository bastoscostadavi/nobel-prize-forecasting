# Nobel Prize Forecasting 2026

We simulate Nobel Prize committee decisions to forecast the 2026 winners.

## Committee discussion

One agent per committee member reviews the candidates, participates in two discussion rounds, and casts a private ranked ballot. A majority decides the winner, with an instant runoff when needed. The [protocol](docs/PHYSICS_PHASE2.md) documents the voting rules and saved records.

**Caveat.** The committee is not the body that formally awards the prize: a larger assembly votes on its recommendation. That assembly almost always follows the committee, so simulating the committee is a good proxy for the decision. Literature is the exception, and our least reliable prediction: the final vote is taken by the 18 members of the Swedish Academy, of whom the Nobel Committee is only a small subset, and the other members vote independently and have overruled it.

![Committee discussion workflow: private opening rankings, support-based shortlisting, two discussion rounds, chair synthesis, proposal construction, private final ballots, instant-runoff voting, and a saved decision](docs/figures/committee-discussion-workflow-v2.png)

## Results

### Physics

![Physics results](docs/figures/physics-terra-sonnet-aggregate-distribution.png)

#### Proposed recognition

- **Hidetoshi Katori and Jun Ye** for optical lattice atomic clocks and precision timekeeping.
- **Charles L. Kane, Eugene J. Mele, and Laurens W. Molenkamp** for the theoretical prediction and experimental discovery of topological insulators and the quantum spin Hall effect.
- **Allan H. MacDonald, Pablo Jarillo-Herrero, and Rafi Bistritzer** for magic-angle twisted bilayer graphene and moiré flat-band quantum matter.
- **Harald Rose, Maximilian Haider, and Ondrej L. Krivanek** for aberration correction in electron microscopy, enabling sub-ångström imaging.
- **Michael Berry and Yakir Aharonov** for geometric phases and the role of electromagnetic potentials in quantum interference.
- **Ignacio Cirac, Peter Zoller, and Rainer Blatt** for quantum computation and simulation with trapped ions.
- **Jocelyn Bell Burnell** for the discovery of pulsars.
- **Alexandre Blais, Andreas Wallraff, and Robert J. Schoelkopf** for circuit quantum electrodynamics.

#### What the simulation analysis reveals

Reviewing the saved discussions reveals two recurring patterns:

1. **Aligned expertise.** Kröll and Lindroth make a consistent case for clocks, drawing on research backgrounds that overlap with Katori–Ye's work.
2. **Broad second-choice support.** Clocks attract agreement while other members split among topological insulators, magic-angle graphene, IceCube, and other options.

For details, including a full example of one committee discussion, check [the Physics experiments](results/physics/README.md#example-discussion).

### Chemistry

Results pending.

### Physiology or Medicine

#### Claude committees

![Medicine results from Claude committees](docs/figures/medicine-claude-committee-distribution.png)

##### Proposed recognition

- **Daniel J. Drucker, Jens Juul Holst, and Svetlana Mojsov** for GLP-1 physiology and the development of incretin therapies for diabetes and obesity.
- **Daniel J. Drucker, Jens Juul Holst, and Lotte Bjerre Knudsen** for the same achievement, crediting the development of long-acting GLP-1 drugs.

##### What the simulation analysis reveals

**Decided before discussion.** GLP-1 is ranked first in 353 of 360 private opening ballots, by every member whatever their field, and wherever it appears in the shuffled list. The committees debate only the third laureate.

For details, check [the Medicine experiments](results/medicine/README.md).

#### Terra committees — preliminary results

As of October 3, 2026, **20 of 60 planned GPT-5.6 Terra/high simulations are complete**, using the shared list of 52 discoveries and neutral committee profiles.

| Proposed recognition | Laureates | Wins | Share of completed simulations |
| --- | --- | ---: | ---: |
| GLP-1 physiology and incretin therapies | Daniel J. Drucker, Jens Juul Holst, Svetlana Mojsov | 9 | 45% |
| HPV virus-like particle vaccines | Douglas R. Lowy, Ian H. Frazer, John T. Schiller | 8 | 40% |
| Unfolded protein response | Kazutoshi Mori, Peter Walter | 1 | 5% |
| TNF blockade for inflammatory disease | Marc Feldmann, Ravinder N. Maini | 1 | 5% |
| B- and T-lymphocyte lineages | Jacques F. A. P. Miller, Max D. Cooper | 1 | 5% |

GLP-1 and HPV vaccines account for **17 of 20 outcomes (85%)**. Terra's completed committees divide between these two discoveries, while the Claude committees favor GLP-1 and debate its third laureate. These percentages describe simulated committee outcomes, not calibrated probabilities of winning the Nobel Prize; the Terra sample remains incomplete.

See the [Terra result summary](results/medicine/terra_committee_summary.json), [current batch progress](results/medicine/terra_committee_progress.json), and [OpenAI Medicine protocol](docs/MEDICINE_OPENAI_PHASE2.md).

### Economic Sciences

Results pending.

### Peace

Results pending.
