# Physics phase 2: candidate consolidation and committee simulation

## Scope

Phase 2 starts from the nomination JSON files produced in phase 1. The initial
batch contains six complete 100-nomination runs:

- `claude-opus-5-5`, runs 1-3
- `gpt-6-sol`, runs 1-3

Both run-4 directories are retained as incomplete inputs and are excluded until
they contain 100 valid nominations. Mixing partial and complete runs would make
the downstream outcome frequencies incomparable.

The list identifiers describe the model that originally proposed the nominator
sample. They do not describe the model used for consolidation or committee
simulation.

## Model and execution settings

Candidate consolidation uses `gpt-6.1-sol` with `high` reasoning effort through
Codex multi-agent orchestration. This explicit model identifier is recorded in
each `candidates.json` file. The choice balances long-context synthesis quality
and cost for a repeated, reviewable workflow. OpenAI's model-selection guidance
describes GPT-6.1 Sol as appropriate for complex technical work and coordinated
deliverables:

- https://developers.openai.com/api/docs/guides/model-selection
- https://developers.openai.com/api/docs/models/gpt-6.1-sol

The consolidation agents receive no web access. Their only evidence is the 100
nomination JSON files in the assigned run plus the versioned prompt in
`prompts/physics_merge_v1.md`.

## Consolidation policy

Consolidation is clerical rather than evaluative. It groups nominations that
refer to substantially the same discovery or invention. It does not eliminate a
valid nomination merely because it appears once or seems unlikely to win.

A source nomination that genuinely bundles distinct achievements is retained as
a compound candidate rather than being forced into a narrower group, split, or
counted twice.

Each source nomination must be assigned to exactly one candidate group. Related
but distinct achievements remain separate when combining them would obscure the
scientific contribution or materially change the appropriate laureates. When a
group names more than three people across its source nominations, the canonical
`nominees` field contains the three most frequently named people; all remaining
names are retained in `other_names`. This is only a compact representation for
committee review, not an eligibility judgment.

Every complete run produces:

- `candidates.json`: canonical groups and the full source-file assignment
- `candidates.csv`: compact consolidation audit table, including provenance
- `merge_notes.md`: ambiguous merges and other judgment calls

Candidate IDs are assigned after sorting by descending nomination count, then by
canonical discovery title. All raw nomination files remain unchanged.

## Validation

`scripts/validate_candidate_merge.py` checks that:

- the source run contains exactly 100 valid nomination JSON files;
- every source file appears in exactly one candidate group;
- no unknown or duplicate source file is present;
- counts, ordering, IDs, and the one-to-three canonical nominee limit agree;
- canonical nominee ordering is recomputed from the source records using
  explicit, machine-readable name-normalization mappings;
- `candidates.csv` exactly matches the canonical JSON representation; and
- the recorded model, reasoning effort, and prompt path are present.

Validation is structural. Semantic merge quality is reviewed separately before
committee deliberation.

## Committee abstraction

The simulation treats the Nobel Committee for Physics as the effective deciding
body. This intentionally omits the Physics Class and final Academy ratification.
The simplification is documented rather than presented as the literal legal
procedure.

For each run, all eight 2026 committee personas receive the consolidated
longlist. The planned committee protocol is:

1. private opening rankings;
2. a union shortlist based on committee support, not nomination count alone;
3. two written discussion rounds with chair summaries;
4. a private final ballot with runoffs if no proposal has a majority; and
5. one recorded prize configuration, which may contain one achievement and up
   to three laureates, two achievements sharing the prize, or no award.

All committee prompts, intermediate statements, summaries, ballots, and final
decisions will be saved under each run's `committee/` directory.

## Blinded committee opening packets

`scripts/prepare_committee_longlist.py` prepares packets only from complete,
validated runs with a matching consolidation CSV. It does not modify nomination
files or the consolidation output triplet. For the initial six-run batch:

```bash
python3 scripts/prepare_committee_longlist.py \
  results/physics/claude-opus-5-5/run-{1,2,3} \
  results/physics/gpt-6-sol/run-{1,2,3}
python3 scripts/prepare_committee_longlist.py --check \
  results/physics/claude-opus-5-5/run-{1,2,3} \
  results/physics/gpt-6-sol/run-{1,2,3}
```

Each run receives two files:

- `committee/longlist.json`: the member-facing packet, with only
  `schema_version: 1` and a `candidates` array. Every entry contains exactly
  `ballot_id`, `discovery`, `subfield`, and `credited_names`. IDs are consecutive
  `B001`, `B002`, etc. All names from `nominees` and `other_names` are combined
  and alphabetized by `(name.casefold(), name)`. No source IDs, nomination counts,
  nominator identities, model-list identity, or frequency-derived name ordering
  appear in this packet.
- `committee/ballot_map.json`: coordinator-only reproducibility metadata and
  crosswalk. Its fields are `schema_version: 1`, `list_id`, `run`, `shuffle`
  (with `algorithm` and `seed_label`), and `ballot_to_candidate`, mapping every
  neutral ballot ID to its original candidate ID. Never provide this file to
  opening-ballot agents.

The shuffle algorithm is `sha256-sort-v1`. The fixed versioned seed label is
`physics-committee-opening-v1`; the per-run label appends
`:<list_id>/run-<run>`. For each
candidate, serialize its public payload (`discovery`, `subfield`, alphabetized
`credited_names`) as UTF-8 JSON with sorted object keys, no spaces, and unescaped
Unicode. Hash the UTF-8 encoding of `per_run_seed + "\u0000" + payload` using
SHA-256 and sort by ascending hexadecimal digest, then serialized payload,
then source candidate ID solely as a final tie breaker for identical payloads.
Assign ballot IDs after sorting. Nomination frequency, original candidate order,
and nominee/other-name partition do not determine the shuffle. Packets contain
no timestamps and are reproducible byte for byte.

Preparation validates bijective source coverage and compares regeneration with
reversed source-candidate order. `--check` also compares both saved packets
against their exact deterministic serialization without writing. Missing,
modified, incomplete, or inconsistent inputs fail validation. This is
reproducible blinding against presentation of phase-1 popularity, not
cryptographic secrecy from someone with access to the source files.
Once any opening-ballot JSON exists, packet preparation refuses to overwrite the
dispatched longlist or crosswalk.

The versioned opening protocol is
`prompts/physics_committee_opening_v1.md`. Dispatch each member separately using
`gpt-6.1-sol` and `high` reasoning effort, supplying their member ID, own profile,
this run's `longlist.json`, and a private
`committee/opening/<member-id>.json` output path. Only the assigned profile and
longlist are evidence for that opening assessment; other members' work and
consolidation provenance are excluded. The member ranks exactly eight distinct
ballot IDs and proposes one to three laureates per selected candidate, drawn
only from its credited names. The JSON records member/model/prompt metadata,
the assigned list and run, consecutive ranks, proposed laureates, and concise assessments of Nobel
worthiness, attribution, maturity and uncertainty. No opening ballots or later
committee deliberation are generated by the preparation script.

## Opening-rank validation and shortlist

`scripts/validate_committee_opening.py` requires one private ballot from each of
the eight documented 2026 committee personas. It checks the member, model,
reasoning, prompt, list and run metadata; exactly eight distinct consecutive
rankings; valid blinded ballot IDs; one to three distinct laureates drawn from
the candidate's credited names; and complete assessment fields.
It also regenerates both committee packets from the validated consolidation and
requires exact equality, so an edited packet cannot silently reinterpret a
submitted ballot.

After all eight ballots validate, `scripts/build_committee_shortlist.py` creates
`committee/shortlist.json`. A candidate enters automatically if it receives at
least one first-place ranking, at least two top-three rankings, or appears in at
least three members' top eights. If that union has fewer than eight candidates,
it is filled to eight by, in order: first-place support, top-three support,
number of rankings, Borda points (8 for rank 1 through 1 for rank 8), best rank,
and blinded ballot ID. There is no maximum: the rule preserves all candidates
that independently meet a support condition. The shortlist retains the blinded
candidate text, member rankings, and proposed laureate configurations, but no
phase-1 nomination counts or source candidate IDs.
