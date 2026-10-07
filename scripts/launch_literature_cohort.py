"""Launch 25 Literature committees, optionally queued after both Peace cohorts.

Uses the consolidated list by default or an explicitly supplied independent
list. Freezes source/profile/prompt hashes. Concurrent execution is permitted
with separate locks; --after-peace optionally waits for both Peace cohorts.
"""
import argparse
import fcntl
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import UTC,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/'results/literature'
SOURCE=ROOT/'agent-data/literature/candidates/candidates.json'

def now():return datetime.now(UTC).isoformat()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(value,indent=2)+'\n');temp.replace(path)
def frozen_inputs(provider,candidates=None):
    candidates=(candidates or SOURCE).resolve()
    arm='terra' if provider=='openai' else 'claude'
    paths=[candidates,ROOT/'agent-data/literature/committee/terra_profile_variants.json']
    paths.extend((ROOT/'agent-data/literature/committee').glob('*/profile_terra_v*.md'))
    paths.extend((ROOT/'prompts').glob(f'literature_committee_{arm}_*.md'))
    if not candidates.is_file():raise ValueError('Literature list is missing; supply the active Codex draft explicitly or finish the Claude merge.')
    if not candidates.is_relative_to(ROOT.resolve()):raise ValueError('Candidate source must be inside the repository')
    data=json.loads(candidates.read_text())
    if candidates == SOURCE.resolve():
        if data.get('list_id')!='literature-2026' or set(data.get('inputs',{}))!={'codex','claude'}:
            raise ValueError('Default source must be the reviewed Codex–Claude common list.')
    elif data.get('category')!='literature' or not data.get('list_id'):
        raise ValueError('Explicit candidate source must identify a Literature list')
    if len(paths)!=37:raise ValueError('Expected candidate list, manifest, 30 profiles and five prompts')
    return {str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)}
def peace_ready():
    waiting=[]
    for arm in ('terra','claude'):
        path=ROOT/f'results/peace/{arm}_committee_progress.json'
        if not path.is_file():waiting.append(f'{arm}: no Peace progress record');continue
        data=json.loads(path.read_text())
        if data.get('status')=='failed':raise ValueError(f'{arm} Peace dispatcher failed; resolve Peace before launching queued Literature')
        if data.get('status')!='complete' or data.get('totals')!={'complete':25}:
            waiting.append(f'{arm}: {data.get("status")}, {data.get("totals")}');continue
        lockpath=path.parent/f'{arm}_committee.lock'
        with lockpath.open('a') as lock:
            try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:waiting.append(f'{arm}: Peace dispatcher still holds run lock')
    return waiting

def launch(provider,snapshot,candidates=None,jobs=1):
    candidates=(candidates or SOURCE).resolve()
    arm='terra' if provider=='openai' else 'claude'
    if frozen_inputs(provider,candidates)!=snapshot:raise ValueError('Literature inputs changed after queue creation; refusing dispatch')
    with (RESULT/f'{arm}_committee.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(lock,fcntl.LOCK_UN)
    runner='run_literature_committee_codex.py' if provider=='openai' else 'run_literature_committee_claude.py'
    command=[sys.executable,str(ROOT/'scripts'/runner),'run','--sims','1-25','--candidates',str(candidates),'--jobs',str(jobs),'--max-attempts','2']
    env=dict(os.environ);env.pop('NOBEL_LITERATURE_PROVIDER',None)
    with (RESULT/f'{arm}_dispatcher.log').open('a') as log:
        process=subprocess.Popen(command,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env=env)
    value={'pid':process.pid,'command':command,'started_at_utc':now(),'candidate_sha256':sha(candidates),'candidate_source':str(candidates.relative_to(ROOT.resolve())),
        'candidate_source_type':json.loads(candidates.read_text()).get('source_type'),'jobs':jobs,
        'simulations':25,'profile_versions':5,'repeats_per_version':5,'committee_members':6,
        'model':'gpt-5.6-terra' if arm=='terra' else 'claude-sonnet-5-5','effort':'high','frozen_inputs':snapshot}
    write(RESULT/f'{arm}_deployment.json',value);return value

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('provider',choices=('openai','claude'))
    parser.add_argument('--after-peace',action='store_true')
    parser.add_argument('--candidates',type=Path,help='Explicit Literature input; independent drafts remain labeled as such.')
    parser.add_argument('--jobs',type=int,choices=(1,2,3),default=1)
    parser.add_argument('--worker',action='store_true',help=argparse.SUPPRESS)
    args=parser.parse_args();arm='terra' if args.provider=='openai' else 'claude'
    candidates=(args.candidates or SOURCE).resolve()
    try:snapshot=frozen_inputs(args.provider,candidates)
    except (OSError,ValueError) as exc:parser.error(str(exc))
    RESULT.mkdir(parents=True,exist_ok=True)
    queuepath=RESULT/f'{arm}_queue.json'
    if args.worker:
        with (RESULT/f'{arm}_queue.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            queued=json.loads(queuepath.read_text());snapshot=queued['frozen_inputs']
            candidates=ROOT/queued['candidate_source'];jobs=queued['jobs']
            try:
                while True:
                    if frozen_inputs(args.provider,candidates)!=snapshot:raise ValueError('Queued Literature inputs changed')
                    waiting=peace_ready()
                    if not waiting:break
                    write(queuepath,{**queued,'status':'waiting_for_peace','updated_at_utc':now(),'dependencies':waiting})
                    time.sleep(30)
                deployment=launch(args.provider,snapshot,candidates,jobs)
                write(queuepath,{**queued,'status':'launched','updated_at_utc':now(),'dispatcher_pid':deployment['pid']})
            except Exception as exc:
                write(queuepath,{**queued,'status':'failed','updated_at_utc':now(),'error':str(exc)});raise
        return
    if args.after_peace and peace_ready():
        with (RESULT/f'{arm}_queue.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            if queuepath.exists() and json.loads(queuepath.read_text()).get('status') in ('queued','waiting_for_peace'):
                raise SystemExit('A Literature queue already exists')
            value={'provider':args.provider,'status':'queued','queued_at_utc':now(),'frozen_inputs':snapshot,
                   'candidate_source':str(candidates.relative_to(ROOT.resolve())),'jobs':args.jobs}
            write(queuepath,value)
            command=[sys.executable,str(Path(__file__).resolve()),args.provider,'--worker','--candidates',str(candidates),'--jobs',str(args.jobs)]
            with (RESULT/f'{arm}_queue.log').open('a') as log:
                p=subprocess.Popen(command,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            value['queue_pid']=p.pid;write(queuepath,value)
        print(json.dumps(value,indent=2));return
    print(json.dumps(launch(args.provider,snapshot,candidates,args.jobs),indent=2))
if __name__=='__main__':main()
