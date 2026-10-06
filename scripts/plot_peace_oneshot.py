"""Render the validated 50-answer Sol Peace distribution."""
import hashlib
import json
from collections import Counter

import peace_oneshot as protocol
import plot_physics_prediction_distributions as style


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
    style.plot('peace-openai-oneshot-distribution.png', 'OpenAI one-shot', 'GPT-6.1 Sol', counts, len(counts))
    print(dict(counts))


if __name__ == '__main__':
    main()
