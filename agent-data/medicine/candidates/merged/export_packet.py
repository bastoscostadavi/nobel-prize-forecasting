"""Validate the consolidated source list and rebuild its neutral agent packet.

Run with Python 3 from any directory. This does not simulate nominators or agents.
"""
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SEED = 'medicine-consolidated-longlist-v1'


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def main():
    data = json.loads((HERE / 'candidates.json').read_text())
    rows = data['candidates']
    ids = [r['candidate_id'] for r in rows]
    keys = [r['discovery_key'] for r in rows]
    assert len(rows) == data['candidate_count'] == len(set(ids)) == len(set(keys))
    assert ids == [f'M{i:03d}' for i in range(1, len(rows) + 1)]
    assert rows == sorted(rows, key=lambda r: (r['discovery'].casefold(), r['discovery_key']))
    all_input_refs = Counter((ref['list_id'], ref['candidate_id']) for r in rows for ref in r['input_entries'])
    aliases = {'Adrian Bird': 'Adrian P. Bird', 'Zhijian J. Chen': 'Zhijian James Chen', 'Mark Skolnick': 'Mark H. Skolnick'}
    source_to_row = {(ref['list_id'], ref['candidate_id']): r for r in rows for ref in r['input_entries']}
    expected_refs = set()
    for spec in data['inputs']:
        path = ROOT / spec['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == spec['sha256'], f'Input changed: {path}'
        original = json.loads(path.read_text())['candidates']
        assert len(original) == spec['candidate_count']
        for item in original:
            ref = (spec['list_id'], item['candidate_id'])
            expected_refs.add(ref)
            assert all_input_refs[ref] == 1, f'Missing or duplicate input: {ref}'
            names = item.get('credited_names', item.get('nominees', [])) + item.get('other_names', [])
            assert {aliases.get(n, n) for n in names} <= set(source_to_row[ref]['credited_names']), f'Dropped input name: {ref}'
    assert set(all_input_refs) == expected_refs
    for r in rows:
        assert r['credited_names'] == sorted(set(r['credited_names']))
        assert r['credited_names'] and r['source_ids']
        assert set(r['source_ids']) <= set(data['sources'])
        assert set(r.get('related_discovery_keys', [])) <= set(keys)
        for person in r.get('historical_contributors', []):
            assert person['name'] not in r['credited_names']
            assert person['eligible_credit_pool'] is False
            assert set(person['source_ids']) <= set(data['sources'])
    # Public payload determines order: input list identity and editorial assessments do not.
    shuffled = []
    for r in rows:
        payload = {k: r[k] for k in ('discovery', 'subfield', 'credited_names')}
        serial = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
        digest = hashlib.sha256((SEED + '\0' + serial).encode()).hexdigest()
        shuffled.append((digest, serial, r['candidate_id'], payload))
    shuffled.sort()
    packet = {'schema_version': 1, 'candidates': []}
    mapping = {'schema_version': 1, 'list_id': 'merged', 'list_version': data['version'], 'shuffle': {'algorithm': 'sha256-sort-v1', 'seed_label': SEED}, 'ballot_to_candidate': {}}
    for i, (_, _, candidate_id, payload) in enumerate(shuffled, 1):
        ballot = f'B{i:03d}'
        packet['candidates'].append({'ballot_id': ballot, **payload})
        mapping['ballot_to_candidate'][ballot] = candidate_id
    dump(HERE / 'committee_longlist.json', packet)
    dump(HERE / 'ballot_map.json', mapping)
    assert set(packet) == {'schema_version', 'candidates'}
    assert all(set(r) == {'ballot_id', 'discovery', 'subfield', 'credited_names'} for r in packet['candidates'])
    assert len(set(mapping['ballot_to_candidate'].values())) == len(rows)
    for r in packet['candidates']:
        original = next(x for x in rows if x['candidate_id'] == mapping['ballot_to_candidate'][r['ballot_id']])
        assert all(r[k] == original[k] for k in ('discovery', 'subfield', 'credited_names'))

    # Candidate identity / coauthorship are supported flags. Expertise alone is informational.
    flags = []
    by_id = {r['candidate_id']: r for r in rows}
    inverse = {v: k for k, v in mapping['ballot_to_candidate'].items()}
    for r in rows:
        for flag in r['conflict_flags']:
            entry = {'candidate_id': r['candidate_id'], 'ballot_id': inverse[r['candidate_id']], **flag}
            entry['interpretation'] = 'expertise_only_not_a_conflict_finding' if flag['type'] == 'closely_related_methods_expertise' else 'simulation_conflict_requiring_explicit_handling'
            flags.append(entry)
    dump(HERE / 'coordinator_manifest.json', {
        'schema_version': 1, 'category': 'medicine', 'prize_year': 2026,
        'list_id': 'merged', 'list_version': data['version'],
        'input_files': data['inputs'], 'merge_summary': data['merge_summary'],
        'packet_sha256': hashlib.sha256((HERE / 'committee_longlist.json').read_bytes()).hexdigest(),
        'canonical_sha256': hashlib.sha256((HERE / 'candidates.json').read_bytes()).hexdigest(),
        'shuffle': mapping['shuffle'],
        'conflict_and_expertise_flags': flags,
        'flags_are_not_real_committee_disqualification_findings': True,
        'eligibility_review': {
            'scope': 'Targeted checks of known deceased pioneers and two persons assumed living in the Claude draft; not a full current living-status audit of all retained persons.',
            'historical_credit_only': [dict(candidate_id=r['candidate_id'], **p) for r in rows for p in r['historical_contributors']],
            'additional_institutional_checks': [
                {'name': 'Jonathan C. Cohen', 'finding': 'Current Hobbs-Cohen institutional lab evidence; no longer retained solely on an absent Wikidata record.', 'source_ids': ['cohen_lab']},
                {'name': 'Vijay G. Sankaran', 'finding': 'Current institutional appointment and 2026 research evidence; no longer retained solely on an absent Wikidata record.', 'source_ids': ['sankaran_profile']},
                {'name': 'Max D. Cooper', 'finding': 'Winter 2026 institutional interview states he is still working.', 'source_ids': ['cooper2026']},
            ],
            'remaining_action': 'Recheck current life status and prior-award overlap for recipients shortlisted by the agents.'
        },
        'validation': {'input_entries_accounted_for_once': len(expected_refs), 'discoveries': len(rows), 'unique_credited_names': len({n for r in rows for n in r['credited_names']}), 'source_references_resolve': True, 'no_input_credit_names_dropped': True, 'public_packet_has_only_opening_fields': True},
    })
    print(f'Validated {len(expected_refs)} input entries -> {len(rows)} discoveries; all input credit names retained; neutral packet and map match.')


if __name__ == '__main__':
    main()
