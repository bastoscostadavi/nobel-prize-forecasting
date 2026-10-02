# Physics experiment details

## Simulation variants

The [Physics result](../../README.md#physics) pools four experiments: **GPT-5.6 Terra and Claude Sonnet 5.5, each with v1 and v2 profiles**. Each experiment combines 12 candidate lists and five fresh committees per list: **60 decisions per experiment, 240 in total**. Those lists come from six nomination runs for each of two independently drafted nominator lists. **v1** profiles combine documented background with inferred personality traits and selection preferences. **v2** removes those inferences, providing a more reliable factual basis for representing the members with fewer assumptions about their preferences. Candidate lists and discussion rules are the same. The plots show v2 first, then v1.

<table>
  <tr>
    <td align="center"><img src="../../docs/figures/physics-openai-committee-v2-distribution.png" alt="OpenAI committee profile v2 probability distribution" width="470"></td>
    <td align="center"><img src="../../docs/figures/physics-claude-committee-v2-distribution.png" alt="Claude committee profile v2 probability distribution" width="470"></td>
  </tr>
  <tr>
    <td align="center"><img src="../../docs/figures/physics-openai-committee-v1-distribution.png" alt="OpenAI committee profile v1 probability distribution" width="470"></td>
    <td align="center"><img src="../../docs/figures/physics-claude-committee-v1-distribution.png" alt="Claude committee profile v1 probability distribution" width="470"></td>
  </tr>
</table>

## One-shot comparison

For comparison, we asked **GPT-6.1 Sol and Claude Opus 5.5** who would win, without simulating a committee. Each graph summarizes 60 independent answers.

<table>
  <tr>
    <td align="center"><img src="../../docs/figures/physics-openai-oneshot-distribution.png" alt="OpenAI one-shot probability distribution" width="470"></td>
    <td align="center"><img src="../../docs/figures/physics-claude-oneshot-distribution.png" alt="Claude one-shot probability distribution" width="470"></td>
  </tr>
</table>

Additional slates appearing in this comparison:

- **John Pendry and David R. Smith** for electromagnetic metamaterials, negative refraction, and transformation optics.
- **John Pendry, David R. Smith, and Ulf Leonhardt** for metamaterials and transformation optics, including optical cloaking proposals.
- **John Pendry, David R. Smith, and Nader Engheta** for metamaterials and engineered electromagnetic response.
- **Ignacio Cirac, Immanuel Bloch, and Peter Zoller** for quantum simulation of many-body physics with ultracold atoms in optical lattices.
- **Eli Yablonovitch and Sajeev John** for photonic crystals and photonic band gaps that control light propagation.
- **Eli Yablonovitch, Sajeev John, and John Pendry** for photonic band-gap crystals and metamaterials for controlling light.
