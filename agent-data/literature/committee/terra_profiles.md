# Five neutral Literature committee profile versions

All six listed committee members have `profile_terra_v1.md` through `profile_terra_v5.md`: Anders Olsson, Ellen Mattson, Anne Swärd, Steve Sem-Sandberg, Anna-Karin Palm and Ingrid Carlberg. Both model cohorts use these same 30 files.

The versions hold the retained public factual record constant while changing headings, section order and the order of complete literary-work blocks. The original `profile.md` files remain untouched. Persona sections and inferred literary tastes are removed uniformly, including in version 1. Public statements are retained with their existing source caveats. Statements delivered for the Academy or committee are not treated as proof of personal preference. No new biographies, personalities or voting preferences are invented.

`scripts/build_literature_profile_variants.py` reproduces the files, compares retained fact-token, quotation and source-link inventories for each member’s five versions, and freezes source/output hashes in `terra_profile_variants.json`. The inherited biographies and citations are not newly source-verified in this task.

Simulations 01–05 use version 1, 06–10 version 2, 11–15 version 3, 16–20 version 4 and 21–25 version 5. Each simulation uses its assigned version consistently through every stage. Five repetitions of each version have equal weight.

Carlberg is a co-opted member. Whether she votes inside the actual committee is undocumented in the repository’s roster. The prepared simulation protocol includes all six listed members as voting participants by explicit modeling assumption, requiring four votes. It predicts a committee recommendation; the final vote of the full Swedish Academy is not modeled.
