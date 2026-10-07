"""Verify completed committee runtime records and package the full audit archive."""
import gzip
import hashlib
import json
import tarfile
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'results/literature'

def main():
    records=[];sources=[];statuses=Counter();sessions=set()
    for arm in ('terra','claude'):
        progress=json.loads((DIRECTORY/f'{arm}_committee_progress.json').read_text())
        if progress['status']!='complete' or progress['totals']!={'complete':25}:raise ValueError(f'{arm} cohort incomplete')
        runtime=DIRECTORY/f'{arm}_committee_runtime'
        accepted=0
        for path in sorted(runtime.glob('**/execution.json')):
            record=json.loads(path.read_text());statuses[(arm,record['status'])]+=1
            if record['status']=='accepted':
                accepted+=1
                if not record['tools_disabled'] or record.get('disallowed_event_items') or record.get('error'):raise ValueError(f'Invalid accepted runtime: {path}')
                session=record.get('thread_id',record.get('session_id'))
                if not session or session in sessions:raise ValueError(f'Missing/reused session: {path}')
                sessions.add(session)
            for item in sorted(path.parent.iterdir()):
                if item.is_file() and item.suffix in ('.json','.jsonl','.txt'):
                    records.append(item)
                    sources.append({'path':str(item.relative_to(ROOT)),'sha256':hashlib.sha256(item.read_bytes()).hexdigest()})
        if accepted!=625:raise ValueError(f'Expected 625 accepted requests for {arm}, got {accepted}')
    target=DIRECTORY/'runtime_audit.tar.gz'
    with target.open('wb') as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as compressed,tarfile.open(fileobj=compressed,mode='w') as archive:
        for path in sorted(records):
            info=archive.gettarinfo(str(path),arcname=str(path.relative_to(ROOT)))
            info.mtime=0;info.uid=info.gid=0;info.uname=info.gname='';info.mode=0o644
            with path.open('rb') as f:archive.addfile(info,f)
    manifest={'schema_version':1,'category':'literature','archive':'results/literature/runtime_audit.tar.gz',
        'archive_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'archive_bytes':target.stat().st_size,
        'accepted_requests':1250,'distinct_accepted_sessions':len(sessions),'files':len(sources),
        'attempt_counts':[{'cohort':a,'status':s,'count':n} for (a,s),n in sorted(statuses.items())],
        'source_records':sources,'reproduction':'python3 scripts/package_literature_audit.py',
        'extraction':'tar -xzf results/literature/runtime_audit.tar.gz -C .'}
    (DIRECTORY/'runtime_audit_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print({k:manifest[k] for k in ('archive_bytes','accepted_requests','distinct_accepted_sessions','files','attempt_counts')})
if __name__=='__main__':main()
