#!/usr/bin/env python3
"""Render Economics figures in the repository's existing forecast chart style.

Counts are checked against all 50 decisions and 100 primary one-shot records.
The figure-data manifest keeps hashes of inputs; this script makes no model calls.
"""
from __future__ import annotations

import hashlib
import json
import textwrap
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results/economics'
FIGURES = ROOT / 'docs/figures'
INK, MUTED, ACCENT = '#23313D', '#687783', '#0B887C'
BAR_MUTED, GRID = '#91AFC0', '#E4E9EC'
CLAUDE_ALIASES = {'Steven T. Berry': 'Steven Berry', 'Gene Grossman': 'Gene M. Grossman',
                  'Marc Melitz': 'Marc J. Melitz'}
DESCRIPTIONS = {
    'E006': 'Collateral constraints, credit cycles and the financial accelerator',
    'E019': 'Firm heterogeneity, selection and the gains from trade',
    'E047': 'Technology, trade shocks and changes in labour demand',
    'E040': 'Quantile regression and distributional econometrics',
    'E011': 'Dynamic panel data models and GMM estimation',
    'E037': 'Partial identification and inference under weak assumptions',
    'E009': 'Dynamic discrete choice and structural estimation',
    'E035': 'Nominal rigidities and monetary-policy theory',
    'E048': 'Trade policy and the political economy of protection',
    'E045': 'Structural estimation of demand and competition',
    'E024': 'Intergenerational mobility measured with administrative data',
}
SOURCES: dict[str, str] = {}


def read(path: Path) -> dict:
    raw = path.read_bytes()
    SOURCES[path.relative_to(ROOT).as_posix()] = hashlib.sha256(raw).hexdigest()
    return json.loads(raw)


def key(parts: list[dict], names_field: str, aliases: dict | None = None,
        committee: bool = False) -> tuple:
    aliases = aliases or {}
    return tuple(sorted((part.get('candidate_id', '') if committee else '',
                         tuple(sorted(aliases.get(n, n) for n in part[names_field])))
                        for part in parts))


def label(configuration: tuple) -> str:
    def surname(name):
        return name.split()[-2] if name.endswith(' Jr.') else name.split()[-1]
    return ' / '.join('–'.join(sorted(surname(n) for n in names))
                      for _, names in configuration) or 'No award'


def committee_counts(stem: str, model: str) -> Counter:
    summary = read(RESULTS / f'{stem}_committee_summary.json')
    expected = Counter({key(c['prize_parts'], 'laureates', committee=True): c['count']
                        for c in summary['configurations']})
    actual = Counter()
    paths = sorted((RESULTS / 'committee' / model).glob('sim-*/decision.json'))
    for path in paths:
        decision = read(path)
        if decision['committee_model'] != model or decision['reasoning_effort'] != 'high':
            raise ValueError(f'Unexpected committee model/effort: {path}')
        actual[key(decision['winner']['prize_parts'], 'laureates', committee=True)] += 1
    if len(paths) != 25 or actual != expected or sum(actual.values()) != 25:
        raise ValueError(f'Committee records do not match summary: {model}')
    return actual


def oneshot_counts(model: str) -> Counter:
    base = RESULTS / 'oneshot' / model
    counts = Counter()
    if model.startswith('gpt-'):
        summary = read(base / 'summary.json')
        aliases = summary['name_aliases']
        sources = read(base / 'posthoc_transcription_summary.json')['source_records']
        if len(sources) != 25:
            raise ValueError(f'Expected 25 source records: {model}')
        for source in sources:
            directory = base / source['prediction_id']
            for filename, hash_key in [('response.txt', 'response_sha256'),
                                       ('result.json', 'result_sha256'),
                                       ('request.json', 'request_sha256'),
                                       ('runtime.jsonl', 'runtime_sha256')]:
                path = directory / filename
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                if digest != source[hash_key]:
                    raise ValueError(f'Source changed: {path}')
                SOURCES[path.relative_to(ROOT).as_posix()] = digest
            result = read(directory / 'result.json')
            counts[key(result['prize_configuration']['prize_parts'], 'credited_names', aliases)] += 1
        expected = Counter()
        for c in summary['configurations']:
            parts = c.get('prize_parts') or [{'credited_names': c['credited_names']}]
            expected[key(parts, 'credited_names', aliases)] += c['count']
        if counts != expected:
            raise ValueError(f'Primary records do not match summary: {model}')
    else:
        paths = sorted(base.glob('pred-*.json'))
        if len(paths) != 25:
            raise ValueError(f'Expected 25 Claude predictions: {model}')
        for path in paths:
            prediction = read(path)
            if prediction['model'] != model or prediction['reasoning_effort'] != 'high':
                raise ValueError(f'Unexpected one-shot model/effort: {path}')
            counts[key([prediction], 'laureates', CLAUDE_ALIASES)] += 1
    if sum(counts.values()) != 25:
        raise ValueError(f'Expected 25 primary predictions: {model}')
    return counts


def ordered(counts: Counter) -> list:
    rows = sorted(counts.items(), key=lambda item: (-item[1], label(item[0])))
    if len({label(k) for k, _ in rows}) != len(rows):
        raise ValueError('Abbreviated labels would merge distinct configurations')
    return rows


def save(figure, filename):
    figure.savefig(FIGURES / filename, dpi=220, facecolor='white')
    plt.close(figure)


def ranked_plot(counts: Counter, filename: str, limit: int | None = None):
    rows = ordered(counts)[:limit]
    total, n = sum(counts.values()), len(rows)
    figure = plt.figure(figsize=(12.4, 2.05 + 0.92 * n), facecolor='white')
    figure.text(0.025, 0.965, '2026 Nobel Prize in Economic Sciences', color=INK,
                fontsize=22, fontweight='bold', va='top')
    labels = figure.add_axes([0.025, 0.11, 0.47, 0.75])
    bars = figure.add_axes([0.515, 0.11, 0.455, 0.75], sharey=labels)
    labels.set_xlim(0, 1)
    labels.set_ylim(n - 0.5, -0.5)
    labels.axis('off')
    highest = 100 * rows[0][1] / total
    step = 10 if highest <= 50 else 20
    maximum = min(100, max(step * 2, step * (int(highest / step) + 1)))
    bars.set_xlim(0, maximum * 1.35)
    for row, (configuration, count) in enumerate(rows):
        first, share = row == 0, 100 * count / total
        color = ACCENT if first else INK
        labels.text(0, row - 0.10, f'{row+1:02d}  {label(configuration).replace("–", " · ")}',
                    color=color, fontsize=13.2, fontweight='bold' if first else 'normal', va='center')
        description = ' / '.join(DESCRIPTIONS[candidate] for candidate, _ in configuration)
        labels.text(0, row + 0.22, textwrap.fill(description, 62), color=MUTED,
                    fontsize=9.8, va='center')
        bars.barh(row, share, height=0.42, color=ACCENT if first else BAR_MUTED, zorder=3)
        bars.text(share + maximum * 0.015, row, f'{count}/{total} ({share:.1f}%)',
                  fontsize=12.3, color=color, fontweight='bold' if first else 'normal', va='center')
    ticks = list(range(0, maximum + 1, step))
    bars.set_xticks(ticks, [f'{v}%' for v in ticks])
    bars.set_yticks([])
    bars.grid(axis='x', color=GRID, linewidth=0.8, zorder=0)
    bars.tick_params(axis='x', colors=MUTED, labelsize=9.5, length=0, pad=8)
    bars.set_xlabel('Share of simulations', color=MUTED, fontsize=10, labelpad=10)
    bars.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
    save(figure, filename)


def marker(configuration, model):
    names = {name for _, people in configuration for name in people}
    if model == 'gpt-5.6-terra' and 'Philippe Aghion' in names:
        return ' †'
    if 'Jonathan Eaton' in names:
        return ' ‡'
    return ''


def color_for(configuration):
    names = {name for _, people in configuration for name in people}
    for member, color in [('Ariel Pakes', '#167D8D'), ('John Moore', '#7162AA'),
                          ('Elhanan Helpman', '#C17B35'), ('Jonathan Eaton', '#C17B35'),
                          ('Philippe Aghion', '#B76353'), ('Michael Woodford', '#4FA3AE'),
                          ('Ernst Fehr', '#9A8CC8')]:
        if member in names:
            return color
    return '#8C9BA6'


def model_plot(counts: Counter, model: str, title: str, filename: str, kind: str):
    rows, total = ordered(counts), sum(counts.values())
    notes = []
    if kind == 'oneshot' and model == 'gpt-5.6-terra':
        notes.append('† Repeats work awarded in 2025 (12 runs); retained in the counts.')
    if kind == 'oneshot' and any(marker(k, model) == ' ‡' for k in counts):
        notes.append('‡ Includes Jonathan Eaton, who died in 2024 (1 run).')
    footer = 0.72 + 0.19 * len(notes)
    header, height = 1.55, 1.55 + 0.76 * len(rows) + 0.19 * len(notes)
    figure = plt.figure(figsize=(7.4, height), facecolor='white')
    axis = figure.add_axes([0.045, footer / height, 0.91, (height-header-footer+0.50) / height])
    axis.set_xlim(0, 129)
    axis.set_ylim(len(rows) - 0.28, -0.3)
    figure.text(0.045, 1 - 0.24/height, title, color=INK, fontsize=15, fontweight='bold', va='top')
    figure.text(0.045, 1 - 0.57/height, f'{total} runs · High reasoning effort', color=MUTED,
                fontsize=10, va='top')
    for row, (configuration, count) in enumerate(rows):
        share = 100 * count / total
        suffix = marker(configuration, model) if kind == 'oneshot' else ''
        axis.text(0, row - 0.035, label(configuration).replace('–', ' · ') + suffix,
                  color=INK, fontsize=11, va='center')
        axis.barh(row + 0.32, 100, height=0.13, color='#F0F3F5', zorder=1)
        axis.barh(row + 0.32, share, height=0.13, color=color_for(configuration), zorder=2)
        axis.text(129, row + 0.015, f'{share:.1f}%', fontsize=12, fontweight='bold',
                  ha='right', va='center', color=INK)
        axis.text(129, row + 0.31, f'{count} / {total}', fontsize=9, ha='right', va='center', color=MUTED)
    axis.set_yticks([])
    axis.set_xticks([0, 25, 50, 75, 100], ['0', '25', '50', '75', '100%'])
    axis.tick_params(axis='x', colors=MUTED, length=0, pad=8, labelsize=9)
    axis.spines[['top', 'right', 'left', 'bottom']].set_visible(False)
    axis.set_xlabel('Share of runs', fontsize=10, color=MUTED, labelpad=9)
    for row, note in enumerate(notes):
        figure.text(0.045, (0.13 + 0.19 * (len(notes)-row-1))/height,
                    note, fontsize=8, color=MUTED, va='bottom')
    save(figure, filename)


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    terra = committee_counts('terra', 'gpt-5.6-terra')
    claude = committee_counts('claude', 'claude-sonnet-5-5')
    combined = terra + claude
    ranked_plot(combined, 'economics-committee-top5.png', limit=5)
    ranked_plot(combined, 'economics-committee-full-distribution.png')
    series = [('committee-aggregate', combined)]
    for model, title, counts, slug in [('gpt-5.6-terra', 'GPT-5.6 Terra', terra, 'terra'),
                                      ('claude-sonnet-5-5', 'Claude Sonnet 5.5', claude, 'claude')]:
        model_plot(counts, model, title + ' · Committee', f'economics-{slug}-committee-distribution.png', 'committee')
        series.append(('committee-' + model, counts))
    for model, title, slug in [('gpt-6.1-sol', 'GPT-6.1 Sol', 'sol'),
                               ('gpt-5.6-terra', 'GPT-5.6 Terra', 'terra'),
                               ('claude-opus-5-5', 'Claude Opus 5.5', 'opus'),
                               ('claude-sonnet-5-5', 'Claude Sonnet 5.5', 'sonnet')]:
        counts = oneshot_counts(model)
        model_plot(counts, model, title + ' · One-shot', f'economics-{slug}-oneshot-distribution.png', 'oneshot')
        series.append(('oneshot-' + model, counts))
    data = {'schema_version': 1, 'aggregation': 'Observed frequencies; primary picks only; recipient configurations remain separate.',
            'claude_name_aliases': CLAUDE_ALIASES,
            'tie_rule': 'Descending count, then alphabetical abbreviated figure label.',
            'series': [{'id': name, 'total': sum(counts.values()),
                        'rows': [{'label': label(k), 'configuration': k, 'count': count,
                                  'frequency': count/sum(counts.values())} for k, count in ordered(counts)]}
                       for name, counts in series],
            'source_hashes': SOURCES}
    (RESULTS / 'figure_data.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({name: {'runs': sum(c.values()), 'configurations': len(c)} for name,c in series}))


if __name__ == '__main__':
    main()
