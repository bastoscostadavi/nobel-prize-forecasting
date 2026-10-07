"""Launch the authorized 25-answer Sol Literature batch with a process lock."""
import fcntl
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import literature_oneshot as protocol


def run():
    root = protocol.ARM_ROOT
    with (root / 'dispatcher.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit('The Literature one-shot dispatcher is already running')
        protocol.shared.prepare(check=True)
        completed = subprocess.run([sys.executable, str(protocol.ROOT / 'scripts/run_literature_oneshot_codex.py'), '--jobs', '3'], cwd=protocol.ROOT)
        protocol.shared.progress(write=True)
        raise SystemExit(completed.returncode)


def main():
    if '--worker' in sys.argv:
        run()
        return
    root = protocol.ARM_ROOT
    protocol.shared.prepare(check=True)
    with (root / 'dispatcher.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(lock, fcntl.LOCK_UN)
    command = [sys.executable, str(Path(__file__).resolve()), '--worker']
    with (root / 'dispatcher.log').open('a') as log:
        child = subprocess.Popen(command, cwd=protocol.ROOT, stdin=subprocess.DEVNULL,
                                 stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    deployment = {'pid': child.pid, 'command': command, 'started_at_utc': datetime.now(UTC).isoformat(),
                  'model': protocol.MODEL, 'reasoning_effort': 'high', 'prediction_count': 25,
                  'prompt_sha256': protocol.shared.sha256_bytes(protocol.shared.prompt_bytes())}
    (root / 'deployment.json').write_text(json.dumps(deployment, indent=2) + '\n')
    print(json.dumps(deployment, indent=2))


if __name__ == '__main__':
    main()
