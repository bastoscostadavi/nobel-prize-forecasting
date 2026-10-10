"""Save live Economics status and the final report while the batch runs.

Local reporting only: no model requests, external messages or input changes.
The dispatcher owns execution; this process stops on completion or failure.
"""
import fcntl
import json
import os
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT/'results/economics'

def load(path):
    for attempt in range(3):
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            if attempt == 2:
                raise
            time.sleep(0.2)

def write(path, value):
    temp = path.with_name(f'.{path.name}.{os.getpid()}.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
    temp.replace(path)

def snapshot():
    progress = load(RESULTS/'terra_committee_progress.json')
    sims = {}
    for number in range(1, 26):
        path = RESULTS/'committee/gpt-5.6-terra'/f'sim-{number:02d}'
        stages = {stage: len(list((path/stage).glob('*.json'))) for stage in ('opening','round1','round2','final_ballots')}
        stages['chair'] = int((path/'chair_summary_round1.json').is_file())
        record = progress['simulations'][path.name]
        sims[path.name] = {'profile_version': record['profile_version'], 'validated_complete': record['status']=='complete', 'accepted_outputs': stages}
    completed = sum(s['validated_complete'] for s in sims.values())
    value = {'schema_version': 1, 'updated_at_utc': datetime.now(UTC).isoformat(),
             'committee_status': progress['status'], 'committee_completed': completed,
             'committee_requested': 25, 'accepted_stage_outputs': sum(sum(s['accepted_outputs'].values()) for s in sims.values()),
             'expected_stage_outputs': 1125, 'committee_error': progress.get('error'),
             'one_shots': load(RESULTS/'oneshot/gpt-6.1-sol/progress.json'), 'simulations': sims}
    terra_progress = RESULTS/'oneshot/gpt-5.6-terra/progress.json'
    if terra_progress.exists():
        value['terra_one_shots'] = load(terra_progress)
    write(RESULTS/'live_progress.json', value)
    return value

def report(value):
    oneshot = load(RESULTS/'oneshot/gpt-6.1-sol/summary.json')
    terra_status = (f" Terra one-shots: **{value['terra_one_shots']['complete']}/25 validated**."
                    if 'terra_one_shots' in value else '')
    lines = ['# Economics predictions for 2026', '',
             f"Updated {value['updated_at_utc']}. Committee simulations: **{value['committee_completed']}/25 complete** ({value['committee_status']}). Sol one-shots: **{value['one_shots']['complete']}/25 validated**.{terra_status}", '',
             'The committee pool contains 50 contributions. Eleven listed participants vote by modeling assumption, with John Hassler chairing and a majority of six. Five factual profile versions receive five simulations each. Committee requests use GPT-5.6 Terra at high effort. Independent one-shot batches use GPT-6.1 Sol and, in the additional comparison arm, GPT-5.6 Terra, both at high effort. All model sessions are fresh and tools are disabled.', '',
             '[Candidate list](../../agent-data/economics/candidates/README.md) · [Candidate CSV](../../agent-data/economics/candidates/candidates.csv) · [Experiment design](../../docs/ECONOMICS_EXPERIMENT_DESIGN.md) · [Live status](live_progress.json)', '',
             '## Sol one-shot results', '',
             '| Primary recipient configuration | Runs | Share of 25 runs |', '|---|---:|---:|']
    for c in oneshot['configurations']:
        lines.append(f"| {', '.join(c['credited_names'])} | {c['count']} | {c['frequency']:.0%} |")
    lines += ['', 'These counts aggregate primary recipient configurations. Contribution wording remains in the source answers and transcriptions. Only the explicitly documented middle-initial aliases for Grossman and Melitz are combined. Run frequencies are not calibrated probabilities of the actual prize.', '',
              '[Raw answers and execution records](oneshot/gpt-6.1-sol/) · [Validated transcription summary](oneshot/gpt-6.1-sol/posthoc_transcription_summary.json)', '']
    terra_path = RESULTS/'oneshot/gpt-5.6-terra/summary.json'
    if terra_path.exists():
        terra = load(terra_path)
        lines += ['## Terra one-shot results', '',
                  'The additional batch matches the committee model and reasoning effort: GPT-5.6 Terra, high. The question is byte-identical to the Sol prompt, and no committee or candidate context is supplied.', '',
                  '| Primary recipient configuration | Runs | Share of 25 runs |', '|---|---:|---:|']
        for c in terra['configurations']:
            names = '; '.join(', '.join(p['credited_names']) for p in c['prize_parts']) or 'No award'
            lines.append(f"| {names} | {c['count']} | {c['frequency']:.0%} |")
        lines += ['', f"{terra['flagged_prediction_count']}/25 answers have observed factual flags for already-awarded work or a deceased proposed laureate. These outputs remain in the frequencies. Conditional alternative laureates are excluded from the primary-pick table.", '',
                  '[Terra results and source explanations](oneshot/gpt-5.6-terra/README.md) · [Summary and factual flags](oneshot/gpt-5.6-terra/summary.json)', '']
    lines += ['## Committee results', '']
    summary_path = RESULTS/'terra_committee_summary.json'
    if summary_path.exists():
        summary = load(summary_path)
        lines += [f"The summary includes {summary['completed_simulations']} completed simulations. Distinct contribution and recipient configurations remain separate.", '',
                  '| Contribution | Recipients | Completed simulations |', '|---|---|---:|']
        for c in summary['configurations']:
            parts = c['prize_parts']
            contribution = '; '.join(p['discovery'] for p in parts) or 'No award'
            recipients = '; '.join(', '.join(p['laureates']) for p in parts) or '—'
            lines.append(f"| {contribution} | {recipients} | {c['count']} |")
        lines += ['', '[Committee summary with profile groups](terra_committee_summary.json)', '']
    else:
        lines += ['The batch is running. Decisions will appear here after complete simulations pass validation.', '']
    if value['committee_error']:
        lines += ['Execution stopped with this recorded error:', '', '```', value['committee_error'], '```', '']
    target = RESULTS/'README.md'
    temp = target.with_name(f'.README.{os.getpid()}.tmp')
    temp.write_text('\n'.join(lines));temp.replace(target)

def main():
    once = '--once' in __import__('sys').argv
    with (RESULTS/'status_writer.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        while True:
            value = snapshot()
            if value['committee_status'] == 'complete':
                summary = RESULTS/'terra_committee_summary.json'
                if not summary.exists() or load(summary)['completed_simulations'] != value['committee_completed']:
                    # The dispatcher publishes completion immediately before
                    # writing the final summary. Wait for that write to land.
                    time.sleep(1)
                    continue
            report(value)
            if once or value['committee_status'] in ('complete', 'failed'):
                print(json.dumps({k: value[k] for k in ('committee_status','committee_completed','accepted_stage_outputs')}), flush=True)
                return
            time.sleep(30)

if __name__ == '__main__': main()
