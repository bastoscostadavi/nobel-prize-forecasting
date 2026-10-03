# 2026 Chemistry candidate list

`candidates.json` is the single candidate list for the Chemistry committee simulations: 69 discoveries, each with a discovery, subfield and pool of credited names. The nominator stage was skipped; the list was prepared directly (3 October 2026).

- `candidates.json`: the list, with scientific basis, reservations, attribution notes, historical (deceased) contributors, prior-award and committee flags, and sources per entry.
- `candidates.csv`: the same entries as a flat table (`candidate_id, discovery, subfield, credited_names`).
- `attribution_review.md`: the per-entry merge and attribution decisions, plus the trimmed entries by reason.
- `merge/consolidate.py`: rebuilds the three files above from the two drafts.
- `codex/` and `claude-opus-5/`: the two independent drafts (72 and 106 entries).

**Merge.** Union by discovery: 53 Codex entries matched one or more Claude entries, 19 are Codex-only and 60 are Claude-only. Codex's scope splits were kept: ATRP/RAFT, base/prime editing, fluorescent/phosphorescent OLEDs, Car-Parrinello/metadynamics, alkane C-H activation/selective C-H functionalization, and carbon supercapacitors/MXenes. Claude names were added to shared pools where supported. Claude's combined self-healing/vitrimer entry was split. Pools can exceed three; an award must name at most three people.

**Trim.** The 132-entry union was cut to 69 for simulation. The 63 removed entries are recorded in `trimmed_entries` (JSON) with one of five reasons:
- substantial overlap with an already rewarded achievement (15);
- central discoverers dead (11);
- biology-centred or already in the Medicine list (9);
- a broad field rather than a defined discovery (10);
- narrower, superseded or weaker than a retained entry in the same area (18).

To restore an entry, delete its key from `TRIM` in `merge/consolidate.py` and rerun.

**Living status.** Every pooled name was checked against Wikidata, with Wikipedia as a fallback, on 2026-10-03. Known deceased contributors appear only in `historical_contributors`. Becke (d. 2025), who was in the Codex DFT pool, was moved there. Maurice Brookhart, listed as deceased in the Claude draft, is living and is in the olefin-polymerization pool. Many younger researchers have no registry entry and are assumed living. Of the older names, this applies to A. Stephen K. Hashmi, Massimo Olivucci, Bruce Dunn, Anthony P. F. Turner, J. Leighton Read, Barry A. Morgan, Tatsuo Ido, Takeshi Imanishi and Yoshio Hori. Elderly pioneers whose status could not be verified were left out of the pools and are named in the attribution notes.

**Committee.** No pool contains a 2026 committee member. Three topics were not added because a member is in or next to the credit pool: microED (Zou), biomolecular free-energy simulation (Åqvist) and cytochrome c oxidase proton pumping (Brzezinski). Two retained entries carry flags to resolve before dispatch:
- zeolites: Zou–Corma coauthorship;
- semiconductor nanowires: Linke–Samuelson.

Radical enzymology, the third flagged entry, was trimmed.

**Sources.** Codex entries keep their primary and award sources. Claude-only entries cite Wikipedia overviews, and death dates cite Wikidata.
