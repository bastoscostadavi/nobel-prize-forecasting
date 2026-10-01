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
- `candidates.csv`: compact committee-facing longlist
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
