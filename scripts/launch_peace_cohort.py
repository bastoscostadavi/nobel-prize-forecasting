"""Start one prepared Peace cohort in a detached dispatcher process."""
import argparse
import fcntl
import hashlib
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('provider', choices=('openai', 'claude'))
    args = parser.parse_args()
    arm = 'terra' if args.provider == 'openai' else 'claude'
    result = ROOT / 'results/peace'
    result.mkdir(parents=True, exist_ok=True)
    # An existing run must release its execution lock before relaunch.
    with (result / f'{arm}_committee.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(lock, fcntl.LOCK_UN)
    runner = 'run_peace_committee_codex.py' if arm == 'terra' else 'run_peace_committee_claude.py'
    source = ROOT / 'agent-data/peace/candidates/candidates.json'
    command = [sys.executable, str(ROOT / 'scripts' / runner), 'run', '--sims', '1-25',
               '--candidates', str(source), '--jobs', '3', '--max-attempts', '2']
    child_env = dict(os.environ)
    child_env.pop('NOBEL_PEACE_PROVIDER', None)
    with (result / f'{arm}_dispatcher.log').open('a') as log:
        process = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.DEVNULL,
            stdout=log, stderr=subprocess.STDOUT, start_new_session=True, env=child_env)
    metadata = {'pid': process.pid, 'command': command, 'started_at_utc': datetime.now(UTC).isoformat(),
        'candidate_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'simulations': 25,
        'profile_versions': 5, 'repeats_per_version': 5, 'committee_members': 5,
        'model': 'gpt-5.6-terra' if arm == 'terra' else 'claude-sonnet-5-5', 'effort': 'high'}
    (result / f'{arm}_deployment.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps(metadata, indent=2))


if __name__ == '__main__':
    main()
