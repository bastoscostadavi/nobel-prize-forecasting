# Economics one-shot prize prediction, Claude version 1

Baseline for the committee simulations: the model is asked directly who will
win the 2026 Nobel Prize in Economic Sciences. It receives no nominations,
candidate list, profiles or committee material, and has no tools or web access.
Each prediction is an independent, fresh Claude CLI call.

## Prompt given to the model

The user message is identical to the GPT-6.1 Sol Economics arm
(`prompts/economics_oneshot_gpt_6_1_sol_v1.txt`):

```
Who will win the 2026 Nobel Prize in Economic Sciences? Predict the prize: the contribution, and the one to three laureates. Answer from your own knowledge only; do not search the web or read any files.
```

System prompt (output format only):

```
Answer with only a JSON object with exactly these keys: "contribution" (string), "laureates" (array of one to three names), "rationale" (string, concise).
```

## Output

`scripts/run_oneshot_claude.py economics --n 25` saves each answer to
`results/economics/oneshot/claude-opus-5-5/pred-XX.json`, and the raw CLI event
stream to `runtime/pred-XX-attempt-N.jsonl` in the same directory The Sonnet 5.5 arm uses the same prompt via
`--model claude-sonnet-5-5` and saves to `results/economics/oneshot/claude-sonnet-5-5/`:

```json
{
  "schema_version": 1,
  "prediction_id": "pred-01",
  "model": "claude-opus-5-5",
  "reasoning_effort": "high",
  "prompt": "prompts/economics_oneshot_claude_v1.md",
  "contribution": "<predicted contribution>",
  "laureates": ["<laureate>"],
  "rationale": "<concise reason>"
}
```
