# One-shot nominator sample: Physics 2026 (claude-opus-5-5, 2026-09-30)

## How the sample was balanced

- **Source:** Model knowledge only. No web search and no files were used. Nominators are confidential, so every row shows a plausible nominator, not a confirmed one.
- **Group mix (weighted by expected nominations submitted, not by invitations sent):**
  - `invited_university_professor` 35: This is the largest pool. The Academy invites chair holders at a rotating set of universities worldwide, but response rates are modest.
  - `nordic_professor` 22: Every permanent physics professor in Sweden, Denmark, Finland, Iceland and Norway is invited each year. Weighted by country: SE 8, DK 5, FI 4, NO 4, IS 1.
  - `academy_member` 15: Mostly Swedish members of the Class for Physics, who are engaged and nominate at a high rate. One foreign member is included.
  - `laureate` 15: Laureates have a permanent right to nominate and use it at a high rate. The rows lean US-based, with recent laureates included.
  - `other_invited` 13: Scientists invited individually, mainly directors and researchers at research institutes and laboratories (Max Planck, CERN, RIKEN, CAS, CNRS, IAS).
  - `nobel_committee_member` 0: The 2026 committee is excluded. No current members are included.
- **Regions:** Nordic 37, rest of Europe 27, North America 23, Asia (including Israel) 11, Oceania 1, Latin America 1. The Nordic share is inflated on purpose, because the statutes give Nordic professors and Academy members automatic nominating rights and they respond at a high rate.
- **Subfields:** Condensed matter and quantum/atomic/optical physics dominate, as they do across the physics professoriate. Particle physics, astrophysics and cosmology, and applied or materials physics make up the rest.
- **Selection:** Where possible, I picked working, mid-career or senior professors rather than only famous names, and I included only people I believe are alive. I recorded no view on whom any of them would nominate.

## Exact prompt

```
The Nobel Prize in Physics is decided in October 2026. Nominations were due 31 January 2026.

Produce a sample of 100 real, living people who plausibly submitted a nomination for the 2026 Nobel Prize in Physics.
The sample should be representative of the actual population of nominations: match the mix of eligible nominator groups (per the Nobel statutes), countries, institutions and subfields in the proportions you believe they contribute nominations, not the proportions of fame.

Exclude members of the 2026 Nobel Committee for Physics.
For each person give: name, institution, country, subfield, nominator group (one of: academy_member, nobel_committee_member, laureate, nordic_professor, invited_university_professor, other_invited), and a one-sentence reason they fit the sample. Do not say whom they would nominate.

Save two files with Write:
1. /Users/davicosta/Desktop/projects/nobel-prize-forecasting/results/physics/nominators/oneshot_claude-opus-5-5_2026-09-30.csv with header: name,institution,country,subfield,group,reason (quote fields containing commas).
2. /Users/davicosta/Desktop/projects/nobel-prize-forecasting/results/physics/nominators/oneshot_claude-opus-5-5_2026-09-30_note.md containing a short note explaining how you balanced the sample, and the exact prompt above.

Final reply: just "done" plus the counts by group and by region.
```
