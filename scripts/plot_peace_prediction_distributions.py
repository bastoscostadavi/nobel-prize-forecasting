"""Render Peace outcome figures using the existing forecast chart format."""
import hashlib
import json
from collections import Counter

import plot_physics_prediction_distributions as style

ROOT = style.ROOT
SHORT_NAMES = {
    'International Court of Justice': 'ICJ', 'International Criminal Court': 'ICC',
    'HALO Trust': 'HALO', 'Mines Advisory Group': 'MAG', "Norwegian People's Aid": 'NPA',
    'International Atomic Energy Agency': 'IAEA', "Sudan's Emergency Response Rooms": 'Sudan ERRs',
}
DESCRIPTIONS = {'PE06': 'International justice and peaceful dispute resolution',
                'PE24': 'Demining and clearing explosive remnants of war',
                'PE33': 'Civilian emergency relief in Sudan',
                'PE38': 'Nuclear safety and safeguards in wartime'}


def label(parts):
    return ' / '.join(sorted('–'.join(SHORT_NAMES.get(n, n) for n in sorted(p['laureates'])) for p in parts)) or 'No award'


def main():
    summary = json.loads((ROOT / 'results/peace/final_summary.json').read_text())
    if summary['completed_simulations'] != 50 or len(summary['source_decisions']) != 50:
        raise ValueError('Expected 50 validated Peace decisions')
    for source in summary['source_decisions']:
        path = ROOT / source['path']
        if hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
            raise ValueError(f'Decision changed: {path}')
    descriptions = {}
    def counts(rows):
        result = Counter()
        for row in rows:
            key = label(row['prize_parts'])
            result[key] += row['count']
            descriptions[key] = ' / '.join(description for _, description in sorted((label([p]), DESCRIPTIONS[p['candidate_id']]) for p in row['prize_parts'])) or 'No award'
        return result
    aggregate = counts(summary['recipient_configurations'])
    terra = counts(summary['models']['gpt-5.6-terra']['configurations'])
    claude = counts(summary['models']['claude-sonnet-5-5']['configurations'])
    if sum(aggregate.values()) != 50 or aggregate != terra + claude:
        raise ValueError('Aggregate does not match the two model cohorts')
    style.SLATE_COLORS.update({key: ['#167D8D', '#7162AA', '#C17B35', '#4FA3AE', '#9A8CC8'][i % 5]
                              for i, key in enumerate(sorted(aggregate))})
    style.FIGURES.mkdir(parents=True, exist_ok=True)
    # Long organization descriptions are wrapped within the existing two-column chart.
    import textwrap
    descriptions = {k: '\n'.join(textwrap.wrap(v, 70)) for k, v in descriptions.items()}
    style.ranked_plot('peace-committee-top5.png', '2026 Nobel Peace Prize', aggregate, descriptions, limit=5)
    style.ranked_plot('peace-committee-full-distribution.png', '2026 Nobel Peace Prize', aggregate, descriptions)
    rows = max(len(terra), len(claude))
    style.plot('peace-terra-committee-distribution.png', 'Terra committee', 'GPT-5.6 Terra', terra, rows)
    style.plot('peace-claude-committee-distribution.png', 'Claude committee', 'Claude Sonnet 5.5', claude, rows)
    print({'aggregate': dict(aggregate), 'terra': dict(terra), 'claude': dict(claude)})


if __name__ == '__main__':
    main()
