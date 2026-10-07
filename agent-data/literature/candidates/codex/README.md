# Independent Codex Literature list: 50 candidates

`candidates.json`, `candidates.csv` and `candidates.md` are the **active 50-writer list**, reduced from the recovered 190-writer draft at the user’s request on 6 October 2026. The entries retain their original IDs and alphabetical order; neither is a likelihood ranking.

The selection weighs mature and distinctive whole-oeuvre achievement, international recognition and current public contender discussion. It does not impose geographical or gender quotas, assume a male/female alternation rule, copy a betting-market ordering or attach artificial probabilities. `selection_50.json` records a specific inclusion reason and contextual sources for every retained writer.

The cut is restricted to the original 190 names; it does not claim these are the globally most likely 50 irrespective of omissions from that pool. Current contender coverage was checked against the 6 October Betsson release and late-September/early-October literary reporting. International lifetime-prize records and targeted status searches supply additional context. These sources support selection and targeted eligibility checks, not complete per-work verification of the inherited literary summaries.

**Source accounting:** all 190 original entries remain in `coverage-190.json` and `coverage-190.csv`, and the exact recovered seed remains in `recovered_seed.json`. `trimmed_entries.json` accounts for every original writer: 50 retained, 139 removed for lower comparative 2026 likelihood, and one excluded for ineligibility. Péter Nádas died on 26 August 2026, before the announcement, as confirmed by [Rowohlt](https://www.rowohlt.de/magazin/aus-dem-verlag/wir-trauern-um-peter-nadas) and [Müpa](https://mupa.hu/en/about/news/a-farewell-to-peter-nadas-on-22-september-20260902); that primary evidence overrides his stale inclusion in a betting release.

The original seed was recovered from this Literature chat’s 3 October command record after its temporary file disappeared. Its original research had not completed per-writer verification. That limitation is retained explicitly. Countries/context labels are not verified citizenship; current living-status checks are targeted rather than an exhaustive registry audit. Removed writers can still be credible future or surprise winners. No actual 2026 nominations or committee preferences are known.

Reproduce the archive and active selection:

```sh
python3 scripts/restore_literature_codex_draft.py
python3 scripts/curate_literature_candidates.py
```

The restoration script writes only the 190-person archive and never replaces the active 50-person list. The selection script verifies exactly 50 retained, 140 removed, stable IDs and complete source accounting. The later merge with Claude uses this active 50-person draft. Simulation packets omit selection judgments, public market evidence and draft provenance.
