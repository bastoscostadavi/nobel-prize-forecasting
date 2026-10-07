#!/usr/bin/env python3
"""Validate clerical primary-pick transcriptions of saved Sol Literature answers.

No model calls are made. The transcription map preserves exact name strings,
binds each entry to its source hash, and includes an exact supporting excerpt.
"""

import hashlib
import json
from collections import defaultdict

import literature_oneshot as protocol


def main() -> None:
    root = protocol.ARM_ROOT
    transcriptions = json.loads((root / "transcriptions.json").read_text())
    if set(transcriptions) != set(protocol.PREDICTION_IDS):
        raise ValueError("Transcriptions must cover all 25 prediction IDs exactly")
    groups = defaultdict(list)
    sources = []
    for prediction_id in protocol.PREDICTION_IDS:
        directory = root / prediction_id
        raw = (directory / "response.txt").read_bytes()
        answer = raw.decode("utf-8")
        transcription = transcriptions[prediction_id]
        digest = hashlib.sha256(raw).hexdigest()
        if transcription["response_sha256"] != digest:
            raise ValueError(f"Source response changed: {prediction_id}")
        if transcription["primary_excerpt"] not in answer:
            raise ValueError(f"Primary-pick excerpt is not verbatim: {prediction_id}")
        parts = transcription["prize_parts"]
        for part in parts:
            for name in part["credited_names"]:
                if name not in transcription["primary_excerpt"]:
                    raise ValueError(f"Credited name missing from primary excerpt: {prediction_id}: {name}")
        execution = json.loads((directory / "execution.json").read_text())
        if execution["requested_model"] != protocol.MODEL or execution["tool_calls_observed"]:
            raise ValueError(f"Unexpected execution model or tools: {prediction_id}")
        if execution["user_messages"] != [protocol.EXACT_PROMPT] or not execution["ephemeral"]:
            raise ValueError(f"Unexpected model-visible input: {prediction_id}")
        usage = execution["usage"]
        usage = dict(usage)
        for line in (directory / "runtime.jsonl").read_text().splitlines():
            event = json.loads(line)
            if event.get("type") == "turn.completed":
                usage["reasoning_tokens"] = event.get("usage", {}).get("reasoning_output_tokens")
        result = {
            "schema_version": 1,
            "arm_id": protocol.ARM_ID,
            "prediction_id": prediction_id,
            "prompt_version": protocol.PROMPT_VERSION,
            "execution": {
                "provider": "openai",
                "interface": execution["interface"],
                "requested_model": protocol.MODEL,
                # The Codex CLI dispatch identifies the requested model; its
                # event stream does not independently report a returned alias.
                "returned_model": protocol.MODEL,
                "reasoning_effort": protocol.REASONING_EFFORT,
                "request_id": execution["thread_id"],
                "response_id": None,
                "created_at_utc": execution["completed_at_utc"],
                "usage": {key: usage[key] for key in
                          ("input_tokens", "output_tokens", "reasoning_tokens", "total_tokens")},
            },
            "response_file": "response.txt",
            "response_sha256": digest,
            "prize_configuration": {
                "outcome": "award" if parts else "no_award",
                "prize_parts": parts,
            },
            "rationale": transcription.get("rationale"),
        }
        result_path = directory / "result.json"
        encoded = protocol.shared.encode_json(result)
        if result_path.exists() and result_path.read_text() != encoded:
            raise ValueError(f"Refusing to overwrite a different transcription: {prediction_id}")
        result_path.write_text(encoded)
        protocol.shared.validate_result(directory)
        signature = tuple(sorted(tuple(sorted(p["credited_names"])) for p in parts))
        groups[signature].append(prediction_id)
        sources.append({
            "prediction_id": prediction_id,
            "response_sha256": digest,
            "result_sha256": hashlib.sha256(result_path.read_bytes()).hexdigest(),
            "request_sha256": hashlib.sha256((directory / "request.json").read_bytes()).hexdigest(),
            "runtime_sha256": hashlib.sha256((directory / "runtime.jsonl").read_bytes()).hexdigest(),
        })
    summary = {
        "schema_version": 1,
        "arm_id": protocol.ARM_ID,
        "record_type": "post_hoc_transcription_summary",
        "source_record_count": 25,
        "model": protocol.MODEL,
        "reasoning_effort": protocol.REASONING_EFFORT,
        "method": "Clerical transcription of the primary prize configuration in each saved answer. Exact names and supporting excerpts are retained in transcriptions.json; alternative predictions are excluded. No additional model calls were made.",
        "configuration_counts": [
            {"prize_parts": [{"credited_names": list(names)} for names in signature],
             "count": len(ids), "frequency": len(ids) / 25, "prediction_ids": ids}
            for signature, ids in sorted(groups.items(), key=lambda x: (-len(x[1]), x[0]))
        ],
        "source_records": sources,
        "returned_model_note": "The recorded returned_model field follows the requested Codex CLI model; the runtime does not independently expose a returned model alias.",
    }
    (root / "posthoc_transcription_summary.json").write_text(protocol.shared.encode_json(summary))
    protocol.shared.progress(write=True)
    print(f"Validated and summarized {len(sources)} Literature one-shot predictions.")


if __name__ == "__main__":
    main()
