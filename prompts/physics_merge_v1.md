# Physics nomination consolidation prompt, version 1

Consolidate one complete simulated Nobel Physics nomination run into a candidate
longlist. Work only from the 100 JSON files in the assigned run's `nominations/`
directory. Do not use web search, external knowledge, committee profiles, other
runs, or existing candidate outputs.

The purpose is clerical consolidation, not winner selection.

## Grouping rules

1. Assign every nomination file to exactly one candidate group.
2. Group nominations only when they concern substantially the same discovery or
   invention. Different wording and different subsets of credited scientists do
   not by themselves make separate candidates.
3. Keep related but scientifically distinct achievements separate when merging
   would obscure the contribution or materially change the appropriate laureates.
4. If one source nomination genuinely bundles two or more scientifically
   distinct achievements and no existing group preserves the full bundle, keep
   that source as a compound candidate rather than forcing it into one narrower
   group. Do not split or duplicate one source across groups.
5. Do not discard valid one-off nominations. Frequency is not an eligibility
   threshold.
6. Select a concise canonical discovery title and one representative subfield.
7. Count how often each named scientist appears in the group's source
   nominations. Put the three most frequently named people in `nominees`.
   Break ties by first appearance in lexicographic source-file order. Preserve
   every remaining named person in `other_names`, in the same frequency/tie-break
   order.
8. Preserve source provenance as nomination filenames relative to the run
   directory, for example `nominations/example-slug.json`.
9. Sort candidate groups by decreasing number of source nominations, then by
   canonical discovery title. Assign IDs `c01`, `c02`, and so on after sorting.

If spelling variants for one person are normalized, record the canonical output
name and every differing source spelling in the top-level `name_normalizations`
object. Do not list exact spellings there.

## Required `candidates.json`

Write `candidates.json` beside the `nominations/` directory with this shape:

```json
{
  "schema_version": 1,
  "list_id": "<list directory name>",
  "run": 1,
  "source_nominations": 100,
  "name_normalizations": {
    "Canonical Person": ["Source Spelling", "Source Spelling 2"]
  },
  "consolidation": {
    "model": "gpt-6.1-sol",
    "reasoning_effort": "high",
    "prompt": "prompts/physics_merge_v1.md"
  },
  "candidates": [
    {
      "candidate_id": "c01",
      "discovery": "Canonical discovery or invention",
      "nominees": ["Person One", "Person Two"],
      "other_names": ["Person Three"],
      "subfield": "Representative subfield",
      "n_nominations": 4,
      "nomination_files": [
        "nominations/example-slug.json"
      ]
    }
  ]
}
```

Use UTF-8 JSON with two-space indentation. Do not add undocumented keys.

## Required notes

Write `merge_notes.md` beside `candidates.json`. Record genuinely ambiguous
merge or split decisions, name normalizations that could affect counting, and
any malformed source record. Do not add scientific ranking or winner analysis.

After writing both files, run:

```bash
python3 scripts/validate_candidate_merge.py <run-directory> --write-csv
```

Fix every validation error. A successful run must end with 100/100 source
nominations assigned exactly once.
