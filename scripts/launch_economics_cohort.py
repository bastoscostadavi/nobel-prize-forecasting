"""Launch or resume 25 frozen Economics simulations: Terra/high by default,
Sonnet/high with NOBEL_ECONOMICS_PROVIDER=claude."""
import fcntl
import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import economics_committee as protocol

ROOT = protocol.ROOT
RESULT = ROOT / 'results/economics'
ARM = protocol.PROMPT_ARM
RUNNER = 'run_economics_committee_codex.py' if protocol.PROVIDER == 'openai' else 'run_economics_committee_claude.py'

def main():
    source = protocol.default_candidates()
    paths = [source, ROOT/'agent-data/economics/committee/terra_profile_variants.json']
    paths.extend((ROOT/'agent-data/economics/committee').glob('*/profile_terra_v*.md'))
    paths.extend(ROOT/p for p in protocol.PROMPTS.values())
    if len(paths) != 62:
        raise ValueError('Expected candidate source, manifest, 55 factual profiles and five prompts')
    snapshot = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    for number in range(1, 26):
        sim = protocol.RESULTS/protocol.COHORT/f'sim-{number:02d}'
        protocol.prepare(sim)
        protocol.check_packet(sim)
    RESULT.mkdir(parents=True, exist_ok=True)
    with (RESULT/f'{ARM}_committee.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(lock, fcntl.LOCK_UN)
    command = [sys.executable, str(ROOT/'scripts'/RUNNER), 'run',
               '--sims', '1-25', '--candidates', str(source), '--jobs', '3', '--max-attempts', '2']
    with (RESULT/f'{ARM}_dispatcher.log').open('a') as log:
        process = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.DEVNULL, stdout=log,
                                   stderr=subprocess.STDOUT, start_new_session=True)
    record = {'pid': process.pid, 'command': command, 'started_at_utc': datetime.now(UTC).isoformat(),
              'model': protocol.MODEL, 'reasoning_effort': protocol.EFFORT, 'simulations': 25,
              'profile_versions': 5, 'repeats_per_version': 5, 'committee_participants': 11,
              'base_model_request_count': 1125, 'jobs': 3, 'frozen_inputs': snapshot}
    (RESULT/f'{ARM}_deployment.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps({k: v for k, v in record.items() if k != 'frozen_inputs'}, indent=2))

if __name__ == '__main__': main()
