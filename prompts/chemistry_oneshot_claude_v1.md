# Chemistry one-shot prize prediction, Claude version 1

Baseline for the committee simulations: the model is asked directly who will
win the 2026 Nobel Prize in Chemistry. It receives no nominations, candidate
list, profiles or committee material, and has no web access. Each prediction is
an independent call.

## Prompt given to the model

```
Who will win the 2026 Nobel Prize in Chemistry? Predict the prize: the discovery
or invention, and the one to three laureates. Answer from your own knowledge
only; do not search the web or read any files.
```

## Output

The coordinator saves each answer to
`results/chemistry/oneshot/<model>/pred-XX.json`:

```json
{
  "schema_version": 1,
  "prediction_id": "pred-01",
  "model": "<exact model ID the agent reports running as>",
  "reasoning_effort": "<effort set by the coordinator>",
  "prompt": "prompts/chemistry_oneshot_claude_v1.md",
  "discovery": "<predicted discovery or invention>",
  "laureates": ["<name>"],
  "rationale": "<concise reason>"
}
```

`scripts/claude_chemistry_committee.py check-oneshot` validates the files.
