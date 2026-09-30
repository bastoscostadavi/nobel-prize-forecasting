# Nominator list: Physics 2026 (claude-opus-5-5, 2026-09-30)

## How the sample was balanced

The aim was to match the likely population of people who actually submit nominations, not the population of famous physicists.

- **Groups (per §7 of the Nobel statutes, physics rules).** Most nominations come from professors at universities that the Academy invites on a rotating basis, so they make up the majority (55). Tenured Nordic physics professors are permanent nominators and are over-represented relative to their numbers, so they get 13. Living laureates nominate at a high rate per head but are few, so they get 12. Other individually invited scientists, mainly at non-university institutes (CERN, Max Planck, national labs, RIKEN, CAS, Perimeter, Weizmann, AMOLF, ICFO, Flatiron), get 12. Royal Swedish Academy physics-class members get 8. `nobel_committee_member` has 0 rows because all members of the 2026 committee are excluded (members: Mark Pearce (chair), Olle Eriksson, Göran Johansson, Stefan Kröll, Eva Lindroth; co-opted: Ulf Danielsson (secretary), Bernhard Mehlig, Eva Olsson). Former committee members appear as Academy members.
- **Regions.** North America 31, Nordic 22, rest of Europe 26, East and South Asia 17, Israel 2, Oceania 1, Latin America 1. The US is the largest single source. The Nordic countries are heavily over-represented relative to their population because of their permanent rights. China's share is rising. Russia is not included, given how weak scientific ties with Sweden have been since 2022. This is a judgement call.
- **Subfields.** The sample leans towards condensed matter, AMO/quantum optics and quantum information, which make up the largest parts of physics faculty. It also covers astrophysics and cosmology, particle and astroparticle physics, photonics, statistical and soft-matter physics, and materials/applied physics.
- **Institutions.** Within each country, the sample favours large research-university departments that are likely to be on invitation lists, plus some mid-sized departments. Well-known prize candidates are not over-sampled.

## Sources used for checking

- NobelPrize.org, "The Nobel Committee for Physics" and "Nomination and selection of physics laureates" (committee composition and nominator categories)
- Wikipedia and institutional pages for affiliation and status checks, including:
  - Klaus Mølmer (University of Copenhagen research portal)
  - Robert Myers (Perimeter news: director term ended in 2024, now faculty)
  - Hideo Ohno (Tohoku: special honorary professor after serving as president 2018–2024)
  - Susanne Viefers (UiO)
  - Joseph Lykken (Fermilab Quantum Division)
  - Lars Samuelson (Lund and SUSTech)
  - Rudolf Gross (TUM emeritus of excellence since March 2025)
  - Mete Atatüre (head of the Cavendish Laboratory)
- The remaining affiliations come from model knowledge (cutoff mid-2026) and were not all checked individually online. Being alive and current affiliation are believed correct but are not guaranteed.

Web access was allowed for this task.

## Exact task prompt

```
The Nobel Prize in Physics is decided in October 2026. Nominations were due 31 January 2026.

Produce a sample of 100 real, living people who plausibly submitted a nomination for the 2026 Nobel Prize in Physics.
The sample should be representative of the actual population of nominations: match the mix of eligible nominator groups (per the Nobel statutes), countries, institutions and subfields in the proportions you believe they contribute nominations, not the proportions of fame.

Exclude members of the 2026 Nobel Committee for Physics.
For each person give: name, institution, country, subfield, nominator group (one of: academy_member, nobel_committee_member, laureate, nordic_professor, invited_university_professor, other_invited), and a one-sentence reason they fit the sample. Do not say whom they would nominate.
```
