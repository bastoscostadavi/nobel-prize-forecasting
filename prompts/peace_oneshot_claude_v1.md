# Peace one-shot prize prediction, Claude version 1

Baseline for the committee simulations: the model is asked directly who will
win the 2026 Nobel Peace Prize. It receives no nominations, candidate list,
profiles or committee material, and has no tools or web access. Each prediction
is an independent, fresh Claude CLI call.

## Prompt given to the model

The user message is identical to the GPT-6.1 Sol Peace arm
(`prompts/peace_oneshot_gpt_6_1_sol_v1.txt`):

```
Who will win the 2026 Nobel Prize in Peace? Predict the prize: the achievement, and the one to three individuals and/or organizations. Answer from your own knowledge only; do not search the web or read any files.
```

System prompt (output format only):

```
Answer with only a JSON object with exactly these keys: "achievement" (string), "laureates" (array of one to three individual and/or organization names), "rationale" (string, concise).
```

## Output

`scripts/run_peace_oneshot_claude.py` saves each answer to
`results/peace/oneshot/claude-opus-5-5/pred-XX.json`, and the raw CLI event
stream to `runtime/pred-XX-attempt-N.jsonl` in the same directory:

```json
{
  "schema_version": 1,
  "prediction_id": "pred-01",
  "model": "claude-opus-5-5",
  "reasoning_effort": "high",
  "prompt": "prompts/peace_oneshot_claude_v1.md",
  "achievement": "<predicted achievement>",
  "laureates": ["<individual or organization>"],
  "rationale": "<concise reason>"
}
```
