# Literature one-shot prize prediction, Claude version 1

Baseline for the committee simulations: the model is asked directly who will
win the 2026 Nobel Prize in Literature. It receives no candidate list, profiles
or committee material, and has no tools or web access. Each prediction is an
independent, fresh Claude CLI call.

## Prompt given to the model

```
Who will win the 2026 Nobel Prize in Literature? Predict the laureate and the literary achievement. Answer from your own knowledge only; do not search the web or read any files.
```

System prompt (output format only):

```
Answer with only a JSON object with exactly these keys: "laureate" (string, one writer's name), "achievement" (string), "rationale" (string, concise).
```

## Output

`scripts/run_oneshot_claude.py literature --n 25` saves each answer to
`results/literature/oneshot/claude-opus-5-5/pred-XX.json`, and the raw CLI
event stream to `runtime/pred-XX-attempt-N.jsonl` in the same directory:

```json
{
  "schema_version": 1,
  "prediction_id": "pred-01",
  "model": "claude-opus-5-5",
  "reasoning_effort": "high",
  "prompt": "prompts/literature_oneshot_claude_v1.md",
  "achievement": "<literary achievement>",
  "laureate": "<writer>",
  "rationale": "<concise reason>"
}
```
