"""Validate 50 Peace decisions and save outcome and discussion summaries."""
import hashlib
import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

import peace_committee as terra
import run_peace_committee_claude as claude

ROOT = terra.ROOT


def signature(parts):
    return json.dumps(sorted([{'candidate_id': p['candidate_id'], 'discovery': p['discovery'],
                             'laureates': sorted(p['laureates'])} for p in parts],
                            key=lambda p: (p['candidate_id'], p['laureates'])), sort_keys=True, ensure_ascii=False)


def count_rows(counts, total):
    return [{'prize_parts': json.loads(key), 'count': count, 'frequency': count / total}
            for key, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))]


def main():
    aggregate, sources, models = Counter(), [], {}
    for protocol in (terra, claude.protocol):
        counts, profiles, openings, round2 = Counter(), defaultdict(Counter), Counter(), Counter()
        members = defaultdict(Counter)
        achievements, first_ballot, runoffs = Counter(), Counter(), 0
        outcomes = []
        for number in range(1, 26):
            sim = protocol.RESULTS / protocol.COHORT / f'sim-{number:02d}'
            decision = protocol.validate_sim(sim)
            parts = decision['winner']['prize_parts']
            key = signature(parts)
            counts[key] += 1
            aggregate[key] += 1
            version = protocol.simulation_profile_version(sim)
            profiles[version][key] += 1
            achievements.update(set(p['candidate_id'] for p in parts))
            runoffs += len(decision['rounds']) > 1
            mapping = json.loads((sim / 'ballot_map.json').read_text())['ballot_to_candidate']
            initial = Counter()
            for member in sorted(protocol.MEMBERS):
                opening = json.loads((sim / 'opening' / f'{member}.json').read_text())
                cid = mapping[opening['rankings'][0]['ballot_id']]
                openings[cid] += 1
                initial[cid] += 1
                members[member][cid] += 1
                statement = json.loads((sim / 'round2' / f'{member}.json').read_text())
                round2[signature([{'candidate_id': mapping[p['ballot_id']],
                                  'discovery': next(c['discovery'] for c in json.loads((sim / 'longlist.json').read_text())['candidates'] if c['ballot_id'] == p['ballot_id']),
                                  'laureates': p['laureates']} for p in statement['preferred_configuration']['prize_parts']])] += 1
            outcomes.append({'simulation_id': sim.name, 'profile_version': version,
                             'winning_configuration': json.loads(key), 'opening_first_places': dict(initial),
                             'instant_runoff_rounds': len(decision['rounds'])})
            source = sim / 'decision.json'
            sources.append({'path': str(source.relative_to(ROOT)),
                            'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                            'model': protocol.MODEL, 'profile_version': version,
                            'validated_full_local_records': True})
        if sum(counts.values()) != 25 or any(sum(c.values()) != 5 for c in profiles.values()):
            raise ValueError('Incomplete five-by-five design')
        models[protocol.MODEL] = {
            'completed_simulations': 25, 'configurations': count_rows(counts, 25),
            'profile_groups': {v: {'completed_simulations': 5, 'configurations': count_rows(c, 5)} for v, c in sorted(profiles.items())},
            'achievement_inclusion_counts': dict(achievements),
            'opening_first_place_counts': dict(openings),
            'member_opening_first_places': dict(members),
            'round2_configuration_counts': count_rows(round2, 125),
            'immediate_majority_decisions': 25 - runoffs, 'runoff_decisions': runoffs,
            'simulation_outcomes': outcomes,
        }
    summary = {'schema_version': 1, 'category': 'peace', 'status': 'complete',
               'snapshot_time_utc': datetime.now(UTC).isoformat(), 'completed_simulations': 50,
               'model_counts': {m: 25 for m in models},
               'aggregation_rule': 'One vote per completed committee decision; shared awards remain distinct configurations; no one-shot answers are pooled.',
               'design': 'Five identical neutral profile versions per model, five paired shuffles/repetitions per version; 47 candidates and five voting members.',
               'candidate_input_sha256': hashlib.sha256(terra.default_candidates().read_bytes()).hexdigest(),
               'recipient_configurations': count_rows(aggregate, 50), 'models': models,
               'source_decisions': sources}
    (ROOT / 'results/peace/final_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'decisions': 50, 'configurations': len(aggregate),
                      'models': {m: {'openings': v['opening_first_place_counts'],
                                     'runoffs': v['runoff_decisions']} for m, v in models.items()}}, indent=2))


if __name__ == '__main__':
    main()
