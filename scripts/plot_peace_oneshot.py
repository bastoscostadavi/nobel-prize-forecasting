"""Render the validated Sol and Opus Peace distributions side by side."""
import hashlib
import json
from collections import Counter

import peace_oneshot as protocol
import plot_physics_prediction_distributions as style


def opus_counts():
    root = protocol.ROOT / 'results/peace/oneshot/claude-opus-5-5'
    summary = json.loads((root / 'final_summary.json').read_text())
    if summary['completed_predictions'] != 50 or len(summary['source_records']) != 50:
        raise ValueError('Expected exactly 50 validated Opus forecasts')
    for source in summary['source_records']:
        for path_key, hash_key in [('path', 'sha256'), ('runtime_path', 'runtime_sha256')]:
            path = protocol.ROOT / source[path_key]
            if hashlib.sha256(path.read_bytes()).hexdigest() != source[hash_key]:
                raise ValueError(f'Source changed: {path}')
    counts = Counter()
    for row in summary['configuration_counts']:
        names = ['Sudan ERRs' if name == "Sudan's Emergency Response Rooms" else name for name in row['laureates']]
        counts['–'.join(sorted(names))] += row['count']
    if sum(counts.values()) != 50:
        raise ValueError('Opus counts do not total 50')
    return counts


def main():
    root = protocol.ARM_ROOT
    summary = json.loads((root / 'posthoc_transcription_summary.json').read_text())
    if summary['source_record_count'] != 50 or len(summary['source_records']) != 50:
        raise ValueError('Expected exactly 50 validated Sol forecasts')
    counts = Counter()
    for source in summary['source_records']:
        directory = root / source['prediction_id']
        for filename, key in [('response.txt', 'response_sha256'), ('result.json', 'result_sha256'),
                              ('request.json', 'request_sha256'), ('runtime.jsonl', 'runtime_sha256')]:
            if hashlib.sha256((directory / filename).read_bytes()).hexdigest() != source[key]:
                raise ValueError(f'Source changed: {directory / filename}')
        protocol.shared.validate_result(directory)
        result = json.loads((directory / 'result.json').read_text())
        parts = result['prize_configuration']['prize_parts']
        labels = []
        for part in parts:
            names = ['Sudan ERRs' if n in ("Sudan's Emergency Response Rooms", 'Sudan’s Emergency Response Rooms') else n
                     for n in part['credited_names']]
            labels.append('–'.join(sorted(names)))
        counts[' / '.join(sorted(labels)) or 'No award'] += 1
    style.SLATE_COLORS['Sudan ERRs'] = '#167D8D'
    style.FIGURES.mkdir(parents=True, exist_ok=True)
    opus = opus_counts()
    rows = max(len(counts), len(opus))
    style.plot('peace-openai-oneshot-distribution.png', 'OpenAI one-shot', 'GPT-6.1 Sol', counts, rows)
    style.plot('peace-claude-oneshot-distribution.png', 'Claude one-shot', 'Claude Opus 5.5', opus, rows)
    print({'sol': dict(counts), 'opus': dict(opus)})


if __name__ == '__main__':
    main()
