# Provenance of the physics committee profiles

This covers the two versioned profiles in each of the eight member folders.
Every completed committee arm through 2026-09-30 used the files now named
`<member-id>/profile_v1.md`: Claude Sonnet 5.5, GPT-5.6 Terra, GPT-6 Luna and
the original six GPT-6.1 Sol simulations. The `profile_v2.md` files were added
for new profile-sensitivity simulations and have not been used in those earlier
results.

## Who wrote them

- **Author:** Claude Opus 5.5 (`claude-opus-5-5`), running as a Claude Code
  general-purpose subagent. The main Claude Code session, also Claude Opus 5.5,
  launched one research subagent per prize category, so a single subagent wrote
  all eight physics profiles.
- **Date:** 2026-09-30, committed in `a6fb8db` ("Add committee member profiles
  and experiment plan"). On 2026-10-01 the files were renamed from `profile.md`
  to `profile_v1.md` without changing their contents.
- **Earlier state:** the initial scaffold (`9526420`) had three stub profiles
  (Eriksson, Johansson, Lindroth), each a header with "Persona notes: TODO". The
  subagent rewrote those three and created the other five (Pearce, Danielsson,
  Kröll, Mehlig, Olsson) after confirming the 2026 roster on nobelprize.org.

## How they were written

- **Template:** `agent-data/PROFILE_TEMPLATE.md`, with the sections Biography,
  Research / intellectual footprint, Public statements and values, Connections,
  Persona (a 150–250 word "You are …" paragraph) and Uncertainty.
- **Sources:** web research (nobelprize.org, kva.se, university pages, Wikipedia,
  OpenAlex, interviews and news), cited in each file's Sources list.
- **Rules given to the subagent:**
  - facts must be sourced and inferences marked;
  - the Persona must not name anyone the member would vote for, predict a 2026
    laureate, or claim how the member voted in the past.
- **Inferred, not sourced:** the temperament and taste in each Persona are
  largely the subagent's inference from the member's career and a few public
  quotes. Each file's Uncertainty section says so.

## Observed effect on the simulations

Two personas emphasise precision measurement, and both are grounded in sources:

- **Kröll:** the persona's line that progress is limited by how precisely we can
  measure paraphrases his own quote in a Lund University news piece, which the
  profile cites. The profile also records a year in John Hall's lab in Boulder.
- **Lindroth:** her persona's emphasis on precision and theory–experiment
  agreement reflects her publication record in precision atomic structure.

In every committee arm these two members rank optical lattice clocks (Katori,
Ye) first in most opening ballots, while the other six rarely do. This may be
genuine signal about how the real members would vote. It may also be partly an
artefact of how strongly one writer phrased the personas: a model can turn a
trait into a near-certain vote. Variant profile sets, written independently from
the same sources, test how sensitive the outcome is to that phrasing.

## Version 2: neutral factual profiles

- **Author and date:** Codex, 2026-10-01, at the user's request.
- **Location:** `<member-id>/profile_v2.md`, next to `profile_v1.md`.
- **Roster:** the same eight people, rechecked against the live 2026
  NobelPrize.org committee page.
- **Method:** retained sourced biographical detail, research topics, public
  professional connections and short attributed quotations. Removed inferred
  intellectual tastes, discussion styles, evidentiary preferences, field
  preferences and likely voting tendencies.
- **Simulation instruction:** the factual Persona paragraph tells the model to
  apply the common protocol and candidate evidence. It does not translate a
  research history or quotation into a member-specific decision rule.

New simulation metadata should record whether `profile_v1.md` or
`profile_v2.md` was used. The version should remain fixed for all eight members
within a simulation.
