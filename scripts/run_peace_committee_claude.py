#!/usr/bin/env python3
"""Run 25 isolated, tools-disabled Sonnet/high Peace committees (5 x 5).

Shares the Peace packet and stage evidence protocol with the Codex cohort,
but dispatches Claude CLI sessions and keeps a separate complete audit trail.
No workflow plugin, persistent Claude session, or external tool is required.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CLAUDE = Path.home() / '.local/bin/claude'


def load_claude_protocol_and_cohort():
    # Private module instances prevent importing this runner in a test/process
    # from changing a previously imported OpenAI protocol or dispatcher.
    prior_env = os.environ.get('NOBEL_PEACE_PROVIDER')
    prior_module = sys.modules.get('peace_committee')
    os.environ['NOBEL_PEACE_PROVIDER'] = 'claude'
    try:
        spec = importlib.util.spec_from_file_location('_claude_peace_protocol', ROOT/'scripts/peace_committee.py')
        assert spec and spec.loader
        protocol = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(protocol)
        sys.modules['peace_committee'] = protocol
        spec = importlib.util.spec_from_file_location('_claude_peace_cohort', ROOT/'scripts/run_peace_committee_codex.py')
        assert spec and spec.loader
        cohort = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cohort)
        return protocol, cohort
    finally:
        if prior_env is None:
            os.environ.pop('NOBEL_PEACE_PROVIDER', None)
        else:
            os.environ['NOBEL_PEACE_PROVIDER'] = prior_env
        if prior_module is None:
            sys.modules.pop('peace_committee', None)
        else:
            sys.modules['peace_committee'] = prior_module


protocol, cohort = load_claude_protocol_and_cohort()
dispatch = cohort.dispatch
RUNTIME = ROOT/'results/peace/claude_committee_runtime'
PROGRESS = ROOT/'results/peace/claude_committee_progress.json'
SUMMARY = ROOT/'results/peace/claude_committee_summary.json'
SYSTEM_PROMPT = ('Execute the supplied isolated Nobel Peace committee stage. '
                 'Use only the permitted evidence. Return exactly the required JSON object.')


def build_claude_command(claude: Path) -> list[str]:
    return [str(claude), '--print', '--model', protocol.MODEL, '--effort', protocol.EFFORT,
            '--tools', '', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
            '--disable-slash-commands', '--safe-mode', '--no-session-persistence',
            '--output-format', 'stream-json', '--verbose', '--permission-mode', 'dontAsk',
            '--setting-sources', '', '--no-chrome', '--system-prompt', SYSTEM_PROMPT]


def parse_events(raw: str) -> dict:
    """Extract final response and audit identity; reject any tools/model drift."""
    events = []
    for line in raw.splitlines():
        if line.strip():
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError('Claude runtime contains a non-JSON event') from exc
            if not isinstance(event, dict):
                raise ValueError('Claude runtime event must be an object')
            events.append(event)
    models, errors, disallowed = set(), [], set()
    session_id = None
    final = None
    initialized = False
    def inspect(value):
        if isinstance(value, dict):
            if value.get('type') in {'tool_use', 'tool_result', 'server_tool_use', 'mcp_tool_use'}:
                disallowed.add(value['type'])
            for child in value.values():
                inspect(child)
        elif isinstance(value, list):
            for child in value:
                inspect(child)
    for event in events:
        inspect(event)
        session_id = event.get('session_id', session_id)
        if event.get('type') == 'system' and event.get('subtype') == 'init':
            initialized = True
            if event.get('model'):
                models.add(event['model'])
            else:
                errors.append('initialization did not identify the model')
            if event.get('tools'):
                disallowed.add('available_tools')
            if event.get('mcp_servers'):
                disallowed.add('mcp_servers')
        if event.get('type') == 'assistant':
            message = event.get('message', {})
            if message.get('model'):
                models.add(message['model'])
            if message.get('error'):
                errors.append(str(message['error']))
        # api_retry events are the CLI's own transient retries; a failed final call still fails below.
        is_retry = event.get('type') == 'system' and event.get('subtype') == 'api_retry'
        if not is_retry and (event.get('type') == 'error' or event.get('error')):
            errors.append(str(event.get('message') or event.get('error') or event))
        if event.get('type') == 'result':
            if final is not None:
                errors.append('multiple result events')
            final = event
            models.update(event.get('modelUsage', {}).keys())
            if event.get('is_error') or event.get('subtype') != 'success':
                errors.append(str(event.get('errors') or event.get('result') or event.get('subtype')))
    if not initialized:
        errors.append('missing initialization event')
    if not models or models != {protocol.MODEL}:
        errors.append(f'actual model(s) {sorted(models)!r} differ from locked model {protocol.MODEL!r}')
    if disallowed:
        errors.append('unexpected tool activity/configuration: ' + ', '.join(sorted(disallowed)))
    if final is None:
        errors.append('missing final result event')
    result = final or {}
    raw_usage = result.get('usage', {})
    def count(key):
        value = raw_usage.get(key)
        return value if type(value) is int and value >= 0 else None
    input_tokens = count('input_tokens')
    cached_tokens = count('cache_read_input_tokens')
    cache_creation_tokens = count('cache_creation_input_tokens')
    output_tokens = count('output_tokens')
    total = sum(v or 0 for v in (input_tokens, cached_tokens, cache_creation_tokens, output_tokens)) if input_tokens is not None and output_tokens is not None else None
    return {'session_id': session_id, 'actual_models': sorted(models), 'errors': errors,
            'disallowed_event_items': sorted(disallowed), 'raw_response': result.get('result'),
            'usage': {'input_tokens': input_tokens, 'cached_input_tokens': cached_tokens,
                      'cache_creation_input_tokens': cache_creation_tokens,
                      'output_tokens': output_tokens, 'reasoning_tokens': None, 'total_tokens': total},
            'provider_usage': raw_usage, 'model_usage': result.get('modelUsage', {}),
            'total_cost_usd': result.get('total_cost_usd')}


def record_attempt(attempt: Path, *, prompt, manifest, command, completed,
                   raw_response, status, error, audit) -> None:
    (attempt/'prompt.txt').write_text(prompt, encoding='utf-8')
    (attempt/'permitted_evidence.json').write_text(dispatch.encode(manifest), encoding='utf-8')
    (attempt/'runtime.jsonl').write_text(completed.stdout, encoding='utf-8')
    (attempt/'stderr.txt').write_text(completed.stderr, encoding='utf-8')
    if raw_response is not None:
        (attempt/'response.txt').write_text(raw_response, encoding='utf-8')
    value = {'schema_version': 1, 'provider': protocol.PROVIDER, 'interface': 'claude-cli',
             'requested_model': protocol.MODEL, 'reasoning_effort': protocol.EFFORT,
             'profile_version': dispatch.PROFILE_VERSION, 'profile_file': dispatch.PROFILE_FILENAME,
             'ephemeral': True, 'working_directory': 'fresh empty temporary directory',
             'tools_disabled': True, 'command': command, 'returncode': completed.returncode,
             'prompt_sha256': hashlib.sha256(prompt.encode('utf-8')).hexdigest(),
             'permitted_evidence': manifest, 'status': status, 'error': error,
             'completed_at_utc': datetime.now(UTC).isoformat().replace('+00:00', 'Z'),
             **{k: v for k, v in audit.items() if k != 'raw_response'}}
    (attempt/'execution.json').write_text(dispatch.encode(value), encoding='utf-8')


def run_request(sim, stage, member, claude, max_attempts, runner=subprocess.run):
    destination = dispatch.output_path(sim, stage, member)
    if destination.exists():
        dispatch.validate_member_output(sim, stage, member)
        return f'SKIP {dispatch.relative_label(destination)}: valid artifact exists'
    prompt, manifest = cohort.build_prompt(sim, stage, member)
    errors = []
    for _ in range(max_attempts):
        attempt = dispatch.next_attempt(dispatch.runtime_directory(sim, stage, member))
        command = build_claude_command(claude)
        audit, raw_response = {}, None
        with tempfile.TemporaryDirectory(prefix=f'peace-claude-{stage}-{member}-') as tmp:
            try:
                completed = runner(command, input=prompt, capture_output=True, text=True,
                                   check=False, cwd=tmp, timeout=1800)
            except (OSError, subprocess.TimeoutExpired) as exc:
                stdout = getattr(exc, 'stdout', '') or ''
                stderr = getattr(exc, 'stderr', '') or str(exc)
                if isinstance(stdout, bytes):
                    stdout = stdout.decode('utf-8', errors='replace')
                if isinstance(stderr, bytes):
                    stderr = stderr.decode('utf-8', errors='replace')
                completed = subprocess.CompletedProcess(command, 124, stdout, stderr)
            try:
                audit = parse_events(completed.stdout)
                raw_response = audit.get('raw_response')
                if completed.returncode != 0:
                    raise RuntimeError(f'Claude exited {completed.returncode}: {completed.stderr.strip()}')
                if audit['errors']:
                    raise RuntimeError(' | '.join(audit['errors']))
                if not isinstance(raw_response, str) or not raw_response.strip():
                    raise RuntimeError('Claude produced no final response')
                value = dispatch.parse_json_response(raw_response)
                dispatch.publish_json(destination, value)
                try:
                    dispatch.validate_member_output(sim, stage, member)
                except (Exception, SystemExit):
                    (attempt/'rejected-output.json').write_text(dispatch.encode(value))
                    destination.unlink(missing_ok=True)
                    raise
            except (Exception, SystemExit) as exc:
                error = str(exc)
                errors.append(error)
                record_attempt(attempt, prompt=prompt, manifest=manifest, command=command,
                               completed=completed, raw_response=raw_response,
                               status='failed', error=error, audit=audit)
                continue
            record_attempt(attempt, prompt=prompt, manifest=manifest, command=command,
                           completed=completed, raw_response=raw_response,
                           status='accepted', error=None, audit=audit)
            return f'OK {dispatch.relative_label(destination)}'
    raise RuntimeError(f'{dispatch.relative_label(destination)} failed after {max_attempts} attempt(s): ' + ' | '.join(errors))


def configure():
    if protocol.PROVIDER != 'anthropic' or protocol.MODEL != 'claude-sonnet-5-5':
        raise ValueError('Claude Peace runner must lock Anthropic claude-sonnet-5-5')
    cohort.configure()
    cohort.RUNTIME, cohort.PROGRESS, cohort.SUMMARY = RUNTIME, PROGRESS, SUMMARY
    dispatch.RUNTIME_ROOT = RUNTIME
    dispatch.RUNTIME_SLUG = 'peace-claude'
    dispatch.COORDINATOR_SCRIPT = 'claude_peace_committee.py'
    dispatch.run_request = run_request


def main():
    configure()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('plan', 'run', 'validate', 'summarize'))
    parser.add_argument('--sims', default='1-25')
    parser.add_argument('--candidates', type=Path)
    parser.add_argument('--exclude', action='append', default=[])
    parser.add_argument('--jobs', type=int, default=3)
    parser.add_argument('--max-attempts', type=int, default=2)
    parser.add_argument('--claude', type=Path, default=DEFAULT_CLAUDE)
    args = parser.parse_args()
    ids = dispatch.parse_number_selector(args.sims, tuple(range(1, 26)), 'simulations')
    sims = [ROOT/'results/peace/committee'/protocol.COHORT/f'sim-{n:02d}' for n in ids]
    if args.command == 'plan':
        for sim in sims:
            print(sim.relative_to(ROOT), 'COMPLETE' if (sim/'decision.json').exists() else 'PENDING')
        return
    if args.command == 'validate':
        for sim in sims:
            protocol.validate_sim(sim)
            print('OK', sim.relative_to(ROOT))
        return
    if args.command == 'summarize':
        value = cohort.summarize(sims)
        print(f"Summarized {value['completed_simulations']}/{value['requested_simulations']} simulations: {SUMMARY.relative_to(ROOT)}")
        return
    if not args.candidates or not args.candidates.is_file():
        parser.error('run requires --candidates pointing to the common canonical JSON')
    if not 1 <= args.jobs <= 3 or not 1 <= args.max_attempts <= 5:
        parser.error('jobs must be 1-3; max-attempts must be 1-5')
    if not args.claude.is_file():
        parser.error(f'Claude executable missing: {args.claude}')
    PROGRESS.parent.mkdir(parents=True, exist_ok=True)
    with (PROGRESS.parent/'claude_committee.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            parser.error('a Peace Claude dispatcher already holds the run lock')
        current = None
        try:
            for sim in sims:
                current = sim
                version = f'neutral-terra-v{(int(sim.name[4:])-1)//5+1}'
                if (sim/'metadata.json').exists():
                    protocol.check_packet(sim)
                    metadata = protocol.shared.load_json(sim/'metadata.json')
                    if (ROOT/metadata['candidate_input']).resolve() != args.candidates.resolve():
                        raise ValueError('existing simulation uses a different candidate input')
                    if set(metadata['excluded_candidates']) != set(args.exclude):
                        raise ValueError('existing simulation uses different candidate exclusions')
                    if protocol.simulation_profile_version(sim) != version:
                        raise ValueError('existing simulation uses a different profile version')
                else:
                    protocol.prepare(sim, candidates_path=args.candidates.resolve(), excluded=args.exclude, profile_version=version)
            cohort.progress(sims, 'running')
            for sim in sims:
                current = sim
                cohort.configure_simulation(sim)
                cohort.progress(sims, 'running', sim)
                protocol.check_packet(sim)
                if (sim/'decision.json').exists():
                    protocol.validate_sim(sim)
                    print('SKIP complete', sim.relative_to(ROOT), flush=True)
                    continue
                for stage in cohort.STAGES:
                    dispatch.run_stage(sim, stage, args.claude, args.jobs, args.max_attempts)
                    if stage == 'opening':
                        dispatch.ensure_derived(sim, 'shortlist', sim/'shortlist.json')
                    if stage == 'round2':
                        dispatch.ensure_derived(sim, 'slate', sim/'proposal_slate.json')
                    if stage == 'final':
                        dispatch.ensure_derived(sim, 'tally', sim/'decision.json')
                    cohort.progress(sims, 'running', sim)
                protocol.validate_sim(sim)
                cohort.summarize(sims)
                print('COMPLETE', sim.relative_to(ROOT), flush=True)
        except (Exception, SystemExit) as exc:
            cohort.progress(sims, 'failed', current, str(exc))
            raise
        cohort.progress(sims, 'complete')
        cohort.summarize(sims)


if __name__ == '__main__':
    main()
