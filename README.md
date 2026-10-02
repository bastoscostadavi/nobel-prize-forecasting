# Nobel Prize Forecasting 2026

Forecast the 2026 Nobel Prizes by giving simulated committees a list of candidates, then repeating their deliberations and votes to compare the winning slates.

## Committee discussion

**Candidate list → committee discussion → vote → winning slate.**

Each candidate entry identifies a discovery or contribution and the people who could receive the prize for it. One agent per committee member, conditioned on that member's profile, reviews the list independently. The agents form a shortlist, hold two written discussion rounds with a chair synthesis between them, and cast private ranked ballots. A majority selects the winner; otherwise, an instant runoff transfers votes until a proposal wins.

Repeat the committee simulation on the same candidate list to estimate each slate's share of wins. Save the assessments, discussion, ballots, and decisions so the results can be audited. The simulation ends at the committee decision, omitting subsequent ratification.

Other domains will use supplied candidate lists directly, without a simulated nomination stage. The existing Physics experiments retain their earlier nomination-derived candidate lists. The figure illustrates the current eight-member Physics committee implementation; committee membership and majority thresholds depend on the domain.

The Physics plots compare neutral profiles (**v2**), original profiles (**v1**), and separate **one-shot baselines**, each with 60 runs. These are empirical simulation frequencies, conditional on the inputs and model, rather than calibrated probabilities of the real outcome. The listings describe proposed recognition topics within the experiments.

See the [committee protocol](docs/PHYSICS_PHASE2.md) for the implemented deliberation and voting rules.

![Committee discussion workflow: private opening rankings, support-based shortlisting, two discussion rounds, chair synthesis, proposal construction, private final ballots, instant-runoff voting, and a saved decision](docs/figures/committee-discussion-workflow-v2.png)

## Results

### Physics

<table>
  <tr>
    <td align="center"><img src="docs/figures/physics-openai-committee-v2-distribution.png" alt="OpenAI committee profile v2 probability distribution" width="470"></td>
    <td align="center"><img src="docs/figures/physics-claude-committee-v2-distribution.png" alt="Claude committee profile v2 probability distribution" width="470"></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/figures/physics-openai-committee-v1-distribution.png" alt="OpenAI committee profile v1 probability distribution" width="470"></td>
    <td align="center"><img src="docs/figures/physics-claude-committee-v1-distribution.png" alt="Claude committee profile v1 probability distribution" width="470"></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/figures/physics-openai-oneshot-distribution.png" alt="OpenAI one-shot probability distribution" width="470"></td>
    <td align="center"><img src="docs/figures/physics-claude-oneshot-distribution.png" alt="Claude one-shot probability distribution" width="470"></td>
  </tr>
</table>

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
