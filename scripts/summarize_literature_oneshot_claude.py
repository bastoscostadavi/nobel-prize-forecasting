"""Audit and summarize the 25 existing Opus Literature one-shot forecasts."""
import hashlib
import json
import unicodedata
from collections import Counter,defaultdict
from pathlib import Path
import run_oneshot_claude as runner
ROOT=runner.ROOT
OUT=ROOT/'results/literature/oneshot/claude-opus-5-5'
SPEC=runner.CATEGORIES['literature']
ALIASES={'Mircea Cartarescu':'Mircea Cărtărescu','Mircea Cărtărescu':'Mircea Cărtărescu'}
def canonical(name):return ALIASES.get(unicodedata.normalize('NFC',name),unicodedata.normalize('NFC',name))
def main():
    expected={f'pred-{n:02d}.json' for n in range(1,26)}
    paths=sorted(OUT.glob('pred-*.json'))
    if {p.name for p in paths}!=expected:raise ValueError('Expected exactly 25 Opus Literature forecasts')
    groups=defaultdict(list);sources=[];sessions=set();raw_names=Counter()
    for path in paths:
        record=json.loads(path.read_text())
        keys={'schema_version','prediction_id','model','reasoning_effort','prompt',*SPEC['keys']}
        if set(record)!=keys or record['schema_version']!=1 or record['prediction_id']!=path.stem:raise ValueError(f'Identity/schema differs: {path}')
        if record['model']!=runner.MODEL or record['reasoning_effort']!=runner.EFFORT or record['prompt']!=SPEC['prompt_file']:raise ValueError(f'Model/prompt differs: {path}')
        value={k:record[k] for k in SPEC['keys']};runner.validate(value,SPEC)
        matches=[]
        for runtime in sorted((OUT/'runtime').glob(path.stem+'-attempt-*.jsonl')):
            try:
                if runner.parse(runtime.read_text())!=value:continue
            except (ValueError,RuntimeError):continue
            events=[json.loads(line) for line in runtime.read_text().splitlines() if line.strip()]
            init=[e for e in events if e.get('type')=='system' and e.get('subtype')=='init']
            if len(init)!=1 or not init[0].get('session_id'):continue
            models=set()
            def check(node):
                if isinstance(node,dict):
                    if node.get('type') in ('tool_use','tool_result','server_tool_use','mcp_tool_use'):raise ValueError(f'Tool activity: {runtime}')
                    for child in node.values():check(child)
                elif isinstance(node,list):
                    for child in node:check(child)
            check(events)
            for event in events:
                if event.get('type')=='system' and event.get('subtype')=='init':models.add(event.get('model'))
                if event.get('type')=='assistant':models.add(event.get('message',{}).get('model'))
                if event.get('type')=='result':models.update(event.get('modelUsage',{}))
            models.discard(None)
            if models!={runner.MODEL}:raise ValueError(f'Model drift: {runtime}')
            matches.append((runtime,init[0]['session_id']))
        if len(matches)!=1:raise ValueError(f'Expected one accepted runtime for {path}')
        runtime,session=matches[0]
        if session in sessions:raise ValueError('Conversation reused')
        sessions.add(session);name=canonical(record['laureate']);groups[name].append(path.stem);raw_names[record['laureate']]+=1
        sources.append({'prediction_id':path.stem,'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'runtime_path':str(runtime.relative_to(ROOT)),'runtime_sha256':hashlib.sha256(runtime.read_bytes()).hexdigest(),
            'session_id':session,'observed_models':[runner.MODEL],'tool_calls_observed':[],'raw_laureate':record['laureate']})
    summary={'schema_version':1,'category':'literature','model':runner.MODEL,'reasoning_effort':runner.EFFORT,
        'completed_predictions':25,'distinct_sessions':len(sessions),'user_question':SPEC['user_prompt'],'system_format_instruction':SPEC['system_prompt'],
        'prompt_path':SPEC['prompt_file'],'prompt_sha256':hashlib.sha256((ROOT/SPEC['prompt_file']).read_bytes()).hexdigest(),
        'question_sha256':hashlib.sha256((SPEC['user_prompt']+'\n').encode()).hexdigest(),
        'runner_path':'scripts/run_oneshot_claude.py','runner_sha256':hashlib.sha256((ROOT/'scripts/run_oneshot_claude.py').read_bytes()).hexdigest(),
        'method':'Structured primary picks matched exactly to separate, tools-disabled Opus runtime sessions. Only explicit spelling/Unicode aliases are merged.',
        'recipient_aliases':ALIASES,'raw_name_counts':dict(raw_names),
        'configuration_counts':[{'laureate':name,'count':len(ids),'frequency':len(ids)/25,'prediction_ids':ids} for name,ids in sorted(groups.items(),key=lambda v:(-len(v[1]),v[0]))],
        'source_records':sources}
    (OUT/'final_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'validated':25,'counts':dict((n,len(ids)) for n,ids in groups.items())},ensure_ascii=False))
if __name__=='__main__':main()
