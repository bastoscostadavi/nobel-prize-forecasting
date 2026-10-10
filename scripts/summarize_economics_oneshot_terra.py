"""Summarize validated Terra primary picks without dropping factual mistakes.

Only explicit spelling/accent aliases are combined. Quality flags are a
post-hoc annotation; they never affect the model input or the raw frequencies.
"""
from collections import defaultdict
import hashlib
import json
from pathlib import Path

import economics_oneshot_terra as protocol

ALIASES = {'Jordi Gali': 'Jordi Galí', 'David H. Autor': 'David Autor'}
PRIZE_2025 = 'https://www.nobelprize.org/prizes/economic-sciences/2025/press-release/'
EATON_OBITUARY = 'https://www.bu.edu/econ/?p=34458'

def main():
    root = protocol.ARM_ROOT
    groups = defaultdict(list)
    flags = []
    thread_ids = set()
    records = []
    for pid in protocol.PREDICTION_IDS:
        directory = root/pid
        protocol.shared.validate_result(directory)
        result = json.loads((directory/'result.json').read_text())
        execution = json.loads((directory/'execution.json').read_text())
        assert execution['requested_model'] == protocol.MODEL
        assert execution['reasoning_effort'] == protocol.REASONING_EFFORT
        assert execution['ephemeral'] and not execution['tool_calls_observed']
        assert execution['user_messages'] == [protocol.EXACT_PROMPT]
        assert execution['thread_id'] and execution['thread_id'] not in thread_ids
        thread_ids.add(execution['thread_id'])
        parts = result['prize_configuration']['prize_parts']
        signature = tuple(sorted(tuple(sorted(ALIASES.get(name, name) for name in p['credited_names'])) for p in parts))
        groups[signature].append(pid)
        names = {name for p in parts for name in p['credited_names']}
        if {'Philippe Aghion', 'Peter Howitt'} <= names:
            flags.append({'prediction_id': pid, 'kind': 'previously_awarded_contribution',
                          'names': sorted(names & {'Philippe Aghion', 'Peter Howitt', 'Joel Mokyr'}),
                          'reason': 'The predicted innovation-driven/Schumpeterian growth contribution was already recognised by the 2025 Economics prize.',
                          'source': PRIZE_2025})
        if 'Jonathan Eaton' in names:
            flags.append({'prediction_id': pid, 'kind': 'deceased_proposed_laureate',
                          'names': ['Jonathan Eaton'], 'reason': 'Jonathan Eaton died in February 2024.',
                          'source': EATON_OBITUARY})
        records.append({'prediction_id': pid, 'response_sha256': result['response_sha256'],
                        'result_sha256': hashlib.sha256((directory/'result.json').read_bytes()).hexdigest(),
                        'thread_id': execution['thread_id']})
    configurations = [{'prize_parts': [{'credited_names': list(names)} for names in signature],
                       'count': len(ids), 'frequency': len(ids)/25, 'prediction_ids': ids}
                      for signature, ids in sorted(groups.items(), key=lambda item: (-len(item[1]), item[0]))]
    flagged_ids = sorted({f['prediction_id'] for f in flags})
    summary = {'schema_version': 1, 'arm_id': protocol.ARM_ID, 'model': protocol.MODEL,
               'reasoning_effort': protocol.REASONING_EFFORT, 'prediction_count': 25,
               'prompt_sha256': protocol.shared.sha256_bytes(protocol.shared.prompt_bytes()),
               'primary_pick_only': True, 'name_aliases': ALIASES,
               'method': 'All 25 primary picks are retained. Explicitly conditional or possible additional laureates are alternatives and excluded from the primary configuration. Exact strings and supporting excerpts remain in transcriptions.json. Accent/spelling aliases above affect summary grouping only. Factual flags are post-hoc and do not trigger retries.',
               'configurations': configurations, 'quality_flags': flags,
               'flagged_prediction_count': len(flagged_ids), 'flagged_prediction_ids': flagged_ids,
               'quality_review_scope': 'Observed repeat predictions of the 2025 growth contribution and the deceased Jonathan Eaton. This is not an exhaustive certification of eligibility or attribution for every answer.',
               'source_records': records}
    (root/'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
    lines = ['# Terra Economics one-shot predictions for 2026', '',
             'All **25 predictions** completed using **GPT-5.6 Terra at high reasoning effort**, matching the committee agents. Each request received the same question as the Sol batch in a fresh tools-disabled session, with no candidate list, profiles or prior answers.', '',
             '| Primary recipient configuration | Runs | Share of 25 runs |', '|---|---:|---:|']
    for c in configurations:
        names = '; '.join(', '.join(part['credited_names']) for part in c['prize_parts']) or 'No award'
        lines.append(f"| {names} | {c['count']} | {c['frequency']:.0%} |")
    repeat_count = sum(f['kind'] == 'previously_awarded_contribution' for f in flags)
    death_count = sum(f['kind'] == 'deceased_proposed_laureate' for f in flags)
    death_phrase = 'prediction names' if death_count == 1 else 'predictions name'
    lines += ['', f"{repeat_count} predictions repeat innovation-driven growth work already recognised by the [2025 Economics prize]({PRIZE_2025}). {death_count} {death_phrase} [Jonathan Eaton, who died in 2024]({EATON_OBITUARY}). All raw outputs remain in the counts. These flags describe observed factual problems rather than failed execution or schema validation.", '',
              'Conditional alternative laureates are excluded from the primary-pick table. Full answers and exact supporting excerpts are retained. Run frequencies are not calibrated probabilities of the actual prize.', '',
              '[Summary and factual flags](summary.json) · [Exact transcriptions](transcriptions.json) · [Raw answers](pred-001/response.txt) · [Execution manifest](manifest.json)', '']
    (root/'README.md').write_text('\n'.join(lines))
    print(f'Summarized all 25 Terra predictions; {len(flagged_ids)} have observed factual flags.')

if __name__ == '__main__':
    main()
