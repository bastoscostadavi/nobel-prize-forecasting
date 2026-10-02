# Nobel Prize Forecasting 2026

Forecast the 2026 Nobel Prizes by giving simulated committees a list of candidates, then repeating their deliberations and votes to compare the winning slates.

## Committee discussion

**Candidate list → committee discussion → vote → winning slate.**

Each candidate entry identifies a discovery or contribution and the people who could receive the prize for it. One agent per committee member, conditioned on that member's profile, reviews the list independently. The agents form a shortlist, hold two written discussion rounds with a chair synthesis between them, and cast private ranked ballots. A majority selects the winner; otherwise, an instant runoff transfers votes until a proposal wins. Repeat the committee simulation on the same candidate list to estimate each slate's share of wins. Save the assessments, discussion, ballots, and decisions so the results can be audited. The simulation ends at the committee decision, omitting subsequent ratification.

See the [committee protocol](docs/PHYSICS_PHASE2.md) for the implemented deliberation and voting rules.

![Committee discussion workflow: private opening rankings, support-based shortlisting, two discussion rounds, chair synthesis, proposal construction, private final ballots, instant-runoff voting, and a saved decision](docs/figures/committee-discussion-workflow-v2.png)

## Results

### Physics

![Aggregated Physics committee distribution across GPT-5.6 Terra and Claude Sonnet 5.5, with v1 and v2 profiles](docs/figures/physics-committee-aggregate-distribution.png)

This is the distribution obtained by aggregating **all 240 decisions from the four primary committee experiments**: GPT-5.6 Terra and Claude Sonnet 5.5, each with v1 and v2 profiles. Each experiment contributes 60 decisions; one-shot predictions are excluded. **Katori–Ye wins 202/240 decisions (84.2%)**.

The saved deliberations suggest two reasons for this concentration:

1. **A consistent case from the atomic-physics members.** The simulated Stefan Kröll and Eva Lindroth have research backgrounds overlapping the atomic and precision-measurement physics behind Katori–Ye. They usually rank clocks highly and converge on a consistent case for the achievement's maturity, reproducibility, and attribution.
2. **A broadly acceptable second choice.** Clocks provide a natural fallback when other members' preferred options divide support among topological insulators, magic-angle graphene, IceCube, and other candidates. Their established performance and relatively clear two-person attribution help attract agreement across those divisions, although the discussions still raise questions about timing and credit.

These are interpretations of the simulated discussions, rather than claims about the real committee's preferences.

#### Breakdown by model and profile

Each of the four distributions below already aggregates substantial variation: **two independently drafted nominator lists × six nomination runs per list × five fresh committee simulations per candidate list = 60 decisions per experiment**. Each plot therefore combines 12 candidate lists and repeated deliberations, rather than showing a single committee conversation.

**v1** uses the original `profile_v1.md` files, including inferred personality traits and evaluative preferences. For **v2**, we rewrote the profiles as more neutral, factual `profile_v2.md` files, retaining documented expertise while removing speculative personality and prize-selection preferences. The aim was to bias the simulated committees less through the profile text. The candidate lists and deliberation protocol stay the same.

Neutral profiles (**v2**) appear first, followed by original profiles (**v1**); OpenAI is on the left and Claude on the right.

<table>
  <tr>
    <td align="center"><img src="docs/figures/physics-openai-committee-v2-distribution.png" alt="OpenAI committee profile v2 probability distribution" width="470"></td>
    <td align="center"><img src="docs/figures/physics-claude-committee-v2-distribution.png" alt="Claude committee profile v2 probability distribution" width="470"></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/figures/physics-openai-committee-v1-distribution.png" alt="OpenAI committee profile v1 probability distribution" width="470"></td>
    <td align="center"><img src="docs/figures/physics-claude-committee-v1-distribution.png" alt="Claude committee profile v1 probability distribution" width="470"></td>
  </tr>
</table>

#### One-shot comparison

For comparison, the final two graphs show **one-shot forecasts from our most advanced baseline models: GPT-6.1 Sol and Claude Opus 5.5**. Each model receives only the fixed question asking who will win the 2026 Nobel Prize in Physics, with no candidate list, member profiles, or committee discussion. Each distribution aggregates 60 predictions and is kept separate from the committee aggregate above.

<table>
  <tr>
    <td align="center"><img src="docs/figures/physics-openai-oneshot-distribution.png" alt="OpenAI one-shot probability distribution" width="470"></td>
    <td align="center"><img src="docs/figures/physics-claude-oneshot-distribution.png" alt="Claude one-shot probability distribution" width="470"></td>
  </tr>
</table>

#### Proposed recognition

- **Hidetoshi Katori and Jun Ye** for optical lattice atomic clocks and precision timekeeping.
- **Charles L. Kane, Eugene J. Mele, and Laurens W. Molenkamp** for the theoretical prediction and experimental discovery of topological insulators and the quantum spin Hall effect.
- **Michael Berry and Yakir Aharonov** for geometric phases and the role of electromagnetic potentials in quantum interference.
- **John Pendry and David R. Smith** for electromagnetic metamaterials, negative refraction, and transformation optics.
- **John Pendry, David R. Smith, and Ulf Leonhardt** for metamaterials and transformation optics, including optical cloaking proposals.
- **John Pendry, David R. Smith, and Nader Engheta** for metamaterials and engineered electromagnetic response.
- **Allan H. MacDonald, Pablo Jarillo-Herrero, and Rafi Bistritzer** for magic-angle twisted bilayer graphene and moiré flat-band quantum matter.
- **Harald Rose, Maximilian Haider, and Ondrej L. Krivanek** for aberration correction in electron microscopy, enabling sub-ångström imaging.
- **Ignacio Cirac, Peter Zoller, and Rainer Blatt** for quantum computation and simulation with trapped ions.
- **Ignacio Cirac, Immanuel Bloch, and Peter Zoller** for quantum simulation of many-body physics with ultracold atoms in optical lattices.
- **Jocelyn Bell Burnell** for the discovery of pulsars.
- **Alexandre Blais, Andreas Wallraff, and Robert J. Schoelkopf** for circuit quantum electrodynamics.
- **Eli Yablonovitch and Sajeev John** for photonic crystals and photonic band gaps that control light propagation.
- **Eli Yablonovitch, Sajeev John, and John Pendry** for photonic band-gap crystals and metamaterials for controlling light.

### Chemistry

Committee results pending; simulations will start from a supplied candidate list.

### Physiology or Medicine

Candidate lists prepared; committee results pending.

### Economic Sciences

Committee results pending; simulations will start from a supplied candidate list.

### Peace

Committee results pending; simulations will start from a supplied candidate list.
