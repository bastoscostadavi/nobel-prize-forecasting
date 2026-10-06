# 2026 Peace candidate list

`candidates.json` is the shared Peace list for both the Claude and GPT committees: 47 achievement-centred entries, each with a field and a pool of credited names. The nominator stage was skipped (6 October 2026).

- `candidates.json`: the list, with evidence labels, flags (prior awards, committee proximity, status) and the source entries from each draft; also `trimmed_entries` and `proximity_exclusions`.
- `candidates.csv`: flat table (`candidate_id, achievement, field, credited_names`) for blinded packets.
- `merge/consolidate.py`: rebuilds both files from the drafts and refuses to write unless every draft entry is either kept or trimmed.
- `claude-opus-5-5/` and `codex/`: the independent drafts (94 entries; 108 plus 8 repeat-award entries).

**Award rule.** Pools can exceed three; an award names at most three laureates (individuals and/or organisations).

**Merge.** Union by achievement. Overlapping entries were combined into one entry with a joint pool: Ukraine's children (Kuleba, Save Ukraine, Save the Children), displacement (UNHCR, NRC, Egeland), CPJ/RSF, Amaglobeli/Poczobut (joint Sakharov 2025), B'Tselem/Al-Haq, Bellingcat/Forensic Architecture, the Assad-era disappeared, HD/Sant'Egidio, and the Gaza ceasefire (Trump with the US, Qatari, Egyptian and Turkish mediators). Codex repeat-award entries (MSF, ICRC, UNHCR, IAEA, Amnesty) were matched to Claude's.

**Trim.** 90 draft entries were removed:
- most unlikely outcomes (35), e.g. Zelenskyy, Murkowski/Chemnitz, Pope Leo XIV, Hak Ja Han, Coale, Concordis, Yad Vashem, Carney, the Armenia–Azerbaijan and DRC–Rwanda deals, Svalbard Seed Vault;
- weaker or narrower than a retained entry in the same area (50);
- substantial overlap with a recent laureate (5): ICAN, WFP, Yazda, Thurlow/Marshall Islands, Ukrainian war-crimes documentation.

To restore one, delete its key from `TRIM` in `merge/consolidate.py`, add it to `CANDIDATES`, and rerun.

**Committee proximity.** CARE (Larsen) and PEN (Frydnes) were excluded before the merge. MSF is retained but flagged: chair Frydnes worked for MSF 2004–2011 and later sat on the MSF Norway board. NRC and Norwegian People's Aid are flagged as Norwegian.
