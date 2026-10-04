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

![Aggregate Medicine committee results](docs/figures/medicine-committee-aggregate-distribution.png)

#### Proposed recognition

- **Daniel J. Drucker, Jens Juul Holst, and Svetlana Mojsov** for GLP-1 physiology and the development of incretin therapies for diabetes and obesity.
- **Douglas R. Lowy, Ian H. Frazer, and John T. Schiller** for virus-like particle vaccines that prevent HPV infection and related cancers.
- **Jacques F. A. P. Miller and Max D. Cooper** for discovering distinct B- and T-lymphocyte lineages and their roles in adaptive immunity.
- **Daniel J. Drucker, Jens Juul Holst, and Lotte Bjerre Knudsen** for GLP-1 physiology and the development of incretin therapies, with alternate credit for long-acting GLP-1 drugs.
- **Kazutoshi Mori and Peter Walter** for the unfolded protein response and signaling from the endoplasmic reticulum.
- **Marc Feldmann and Ravinder N. Maini** for TNF blockade as a treatment for rheumatoid arthritis and inflammatory disease.
- **Arthur L. Horwich and F. Ulrich Hartl** for chaperonin-assisted protein folding.
- **Y. M. Dennis Lo** for fetal cell-free DNA in maternal blood and noninvasive prenatal screening.

#### What the simulation analysis reveals

The aggregate combines **120 committee decisions** from Claude Sonnet 5.5 and GPT-5.6 Terra. GLP-1 wins 89 decisions (74.2%): 85 select Drucker, Holst, and Mojsov, while four substitute Lotte Bjerre Knudsen for Mojsov. HPV vaccines place second with 18 decisions (15.0%). Five other discoveries account for the remaining 13 decisions.

1. **Different starting judgments drive the model gap.** Claude ranks GLP-1 first on 353 of 360 private opening ballots and awards it in all 60 simulations. Terra's openings are more dispersed: GLP-1 receives 146 first-place rankings, HPV vaccines 80, and B- and T-cell lineages 47.
2. **Discussion consolidates an existing lead.** In Terra, the eventual winner already has at least a share of the opening plurality in 58 of 60 simulations. From round 1 to round 2, 33 members switch toward the eventual winner and none switch away; its mean support rises from 3.3 members at opening to 4.4 in round 2.
3. **HPV wins by consensus; GLP-1 also wins through transfers.** A winning HPV proposal averages 5.0 of six round-2 supporters and needs a runoff only twice in 18 wins. Winning GLP-1 proposals average 4.3 supporters and need a runoff in 11 of 29 Terra wins, showing broader second-choice support when the committee is split.
4. **Attribution decides the GLP-1 laureate slate.** All 360 Claude round-2 positions support GLP-1, but 317 favor Mojsov and 43 favor Knudsen for the third seat. The final Claude decisions split 56–4; all 29 Terra GLP-1 decisions select Mojsov.

For details, check [the Medicine experiments](results/medicine/README.md).

### Economic Sciences

Results pending.

### Peace

Results pending.
