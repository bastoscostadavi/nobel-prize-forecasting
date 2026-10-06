"""Validate existing Opus Peace forecasts against their raw runtime records."""
import hashlib
import json
from collections import Counter, defaultdict

import run_peace_oneshot_claude as runner

ALIASES = {
    "Sudan's Emergency Response Rooms": "Sudan's Emergency Response Rooms",
    'Emergency Response Rooms (Sudan)': "Sudan's Emergency Response Rooms",
    "Sudan's Emergency Response Rooms (ERRs)": "Sudan's Emergency Response Rooms",
}


def canonical_names(names):
    return tuple(sorted(ALIASES.get(name, name) for name in names))


def audit(path, record):
    raw = path.read_text()
    value, models = runner.parse(raw)
    if value != {key: record[key] for key in ('achievement', 'laureates', 'rationale')}:
        raise ValueError(f'Runtime answer differs from saved prediction: {path}')
    events = [json.loads(line) for line in raw.splitlines() if line.strip()]
    initializations = [e for e in events if e.get('type') == 'system' and e.get('subtype') == 'init']
    if len(initializations) != 1 or not initializations[0].get('session_id'):
        raise ValueError(f'Missing unique runtime session: {path}')
    def no_tools(node):
        if isinstance(node, dict):
            if node.get('type') in ('tool_use', 'tool_result', 'server_tool_use', 'mcp_tool_use'):
                raise ValueError(f'Tool activity in {path}')
            for child in node.values():
                no_tools(child)
        elif isinstance(node, list):
            for child in node:
                no_tools(child)
    no_tools(events)
    for event in events:
        if event.get('type') == 'result' and event.get('modelUsage'):
            if set(event['modelUsage']) != {runner.MODEL}:
                raise ValueError(f'Model usage differs from locked Opus model: {path}')
    return initializations[0]['session_id'], models


def main():
    expected = {f'pred-{number:02d}.json' for number in range(1, 51)}
    paths = sorted(runner.OUT.glob('pred-*.json'))
    if {p.name for p in paths} != expected:
        raise ValueError('Expected exactly 50 Opus Peace forecasts')
    groups, aliases, sources, sessions = defaultdict(list), Counter(), [], set()
    for path in paths:
        record = json.loads(path.read_text())
        expected_keys = {'schema_version', 'prediction_id', 'model', 'reasoning_effort',
                         'prompt', 'achievement', 'laureates', 'rationale'}
        if set(record) != expected_keys or record['schema_version'] != 1 or record['prediction_id'] != path.stem:
            raise ValueError(f'Prediction identity differs: {path}')
        if record['model'] != runner.MODEL or record['reasoning_effort'] != runner.EFFORT or record['prompt'] != runner.PROMPT_FILE:
            raise ValueError(f'Model or prompt differs: {path}')
        runner.validate({key: record[key] for key in ('achievement', 'laureates', 'rationale')})
        matches = []
        for runtime in sorted((runner.OUT / 'runtime').glob(path.stem + '-attempt-*.jsonl')):
            try:
                session, models = audit(runtime, record)
            except (ValueError, RuntimeError):
                continue
            matches.append((runtime, session, models))
        if len(matches) != 1:
            raise ValueError(f'Expected one matching accepted runtime for {path}: {len(matches)}')
        runtime, session, models = matches[0]
        if session in sessions:
            raise ValueError('Conversation reused across predictions')
        sessions.add(session)
        names = canonical_names(record['laureates'])
        groups[names].append(path.stem)
        aliases.update(record['laureates'])
        sources.append({'prediction_id': path.stem, 'path': str(path.relative_to(runner.ROOT)),
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'runtime_path': str(runtime.relative_to(runner.ROOT)),
                        'runtime_sha256': hashlib.sha256(runtime.read_bytes()).hexdigest(),
                        'observed_models': sorted(models), 'tool_calls_observed': [],
                        'session_id': session, 'raw_laureates': record['laureates']})
    summary = {'schema_version': 1, 'category': 'peace', 'model': runner.MODEL,
               'reasoning_effort': runner.EFFORT, 'completed_predictions': 50,
               'distinct_sessions': len(sessions),
               'user_question': runner.USER_PROMPT, 'system_format_instruction': runner.SYSTEM_PROMPT,
               'prompt_path': runner.PROMPT_FILE,
               'prompt_sha256': hashlib.sha256((runner.ROOT / runner.PROMPT_FILE).read_bytes()).hexdigest(),
               'question_sha256': hashlib.sha256((runner.ROOT / 'prompts/peace_oneshot_gpt_6_1_sol_v1.txt').read_bytes()).hexdigest(),
               'runner_sha256': hashlib.sha256((runner.ROOT / 'scripts/run_peace_oneshot_claude.py').read_bytes()).hexdigest(),
               'method': 'Existing structured primary forecasts validated against matching raw Opus runtime answers; exact recipient aliases grouped, with originals retained.',
               'recipient_aliases': ALIASES, 'raw_name_counts': dict(aliases),
               'configuration_counts': [{'laureates': list(names), 'count': len(ids), 'frequency': len(ids) / 50,
                                         'prediction_ids': ids} for names, ids in sorted(groups.items(), key=lambda x: (-len(x[1]), x[0]))],
               'source_records': sources}
    (runner.OUT / 'final_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print({'validated': 50, 'distinct_sessions': 50, 'configurations': summary['configuration_counts']})


if __name__ == '__main__':
    main()
