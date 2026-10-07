"""Merge independently authored Literature lists with complete source accounting.

A reviewed disposition is required for every unique writer: keep, trim, or
exclude. This program never substitutes one draft for a missing second draft.
Source wording and metadata are retained in input_entries for audit. Blinded
simulation packets are created separately by literature_committee.py.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
import unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
DIRECTORY=ROOT/'agent-data/literature/candidates'
ALIASES={
    'lyudmila-ulitskaya':'ludmila-ulitskaya','lyudmila-petrushevskaya':'ludmila-petrushevskaya',
    'ludmilla-petrushevskaya':'ludmila-petrushevskaya','nurrudin-farah':'nuruddin-farah',
    'nurudin-farah':'nuruddin-farah','can-xue-deng-xiaohua':'can-xue',
    'adonis-ali-ahmad-said-esber':'adonis','ko-un-go-eun':'ko-un',
    'yurii-andrukhovych':'yuri-andrukhovych','yury-andrukhovych':'yuri-andrukhovych',
}

def writer_key(name):
    raw=re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',name).encode('ascii','ignore').decode().lower()).strip('-')
    return ALIASES.get(raw,raw)

def text_list(value):
    if value is None:return []
    if isinstance(value,str):return [v.strip() for v in value.split(';') if v.strip()]
    if isinstance(value,list) and all(isinstance(v,str) and v.strip() for v in value):return list(dict.fromkeys(v.strip() for v in value))
    raise ValueError(f'Expected text or text array, got {value!r}')

def load(path,label):
    if not path.is_file():raise ValueError(f'Missing {label} draft: {path}')
    data=json.loads(path.read_text())
    if not isinstance(data,dict) or data.get('category')!='literature':raise ValueError(f'Not a Literature draft: {path}')
    rows=data.get('candidates')
    if not isinstance(rows,list) or not rows:raise ValueError(f'Empty {label} draft')
    normalized=[]; ids=set(); keys=set()
    for index,row in enumerate(rows,1):
        if not isinstance(row,dict):raise ValueError(f'{label}: candidate is not an object')
        name=next((row[k] for k in ('name','writer','author','candidate_name') if isinstance(row.get(k),str) and row[k].strip()),None)
        if name is None:
            names=text_list(row.get('credited_names',row.get('nominees')))
            if len(names)!=1:raise ValueError(f'{label}: writer entry must identify exactly one author: {index}')
            name=names[0]
        name=name.strip(); key=writer_key(name); cid=row.get('candidate_id',f'{label}-{index:03d}')
        if not isinstance(cid,str) or not cid or cid in ids or key in keys:raise ValueError(f'{label}: duplicate/invalid writer or ID: {name} / {cid}')
        ids.add(cid);keys.add(key)
        achievement=next((row[k].strip() for k in ('achievement','literary_contribution','literary_basis','rationale','discovery') if isinstance(row.get(k),str) and row[k].strip()),None)
        languages=text_list(row.get('writing_languages',row.get('languages',row.get('language'))))
        genres=text_list(row.get('genres',row.get('genre')))
        works=text_list(row.get('representative_works',row.get('major_works',row.get('key_works'))))
        field=next((row[k].strip() for k in ('field','subfield') if isinstance(row.get(k),str) and row[k].strip()),None)
        field=field or '; '.join(genres+(['writing languages: '+ '; '.join(languages)] if languages else []))
        if not achievement or not field:raise ValueError(f'{label}: {name} lacks a literary contribution or field')
        normalized.append({'writer_key':key,'name':name,'achievement':achievement,'field':field,
            'writing_languages':languages,'genres':genres,'representative_works':works,
            'source_list':label,'source_candidate_id':cid,'source_entry':row})
    return data,normalized

def merge(codex_path,claude_path,review_path):
    inputs={}; groups={}
    for label,path in (('codex',codex_path),('claude',claude_path)):
        data,rows=load(path,label)
        inputs[label]={'path':str(path.resolve().relative_to(ROOT.resolve())),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'candidate_count':len(rows),'list_id':data.get('list_id'),'research_cutoff':data.get('research_cutoff'),
            'sources':data.get('sources',{})}
        for row in rows:groups.setdefault(row['writer_key'],[]).append(row)
    if not review_path.is_file():raise ValueError(f'Review required for {len(groups)} unique writers: {review_path}')
    review=json.loads(review_path.read_text())
    decisions=review.get('writers')
    if not isinstance(decisions,dict) or set(decisions)!=set(groups):
        missing=sorted(set(groups)-set(decisions or {})); extra=sorted(set(decisions or {})-set(groups))
        raise ValueError(f'Incomplete source accounting: missing={missing}; unknown={extra}')
    kept=[];removed=[];crosswalk=[]
    for key,entries in sorted(groups.items()):
        verdict=decisions[key]
        if not isinstance(verdict,dict) or verdict.get('action') not in ('keep','trim','exclude') or not isinstance(verdict.get('reason'),str) or not verdict['reason'].strip():
            raise ValueError(f'Invalid reviewed disposition: {key}')
        references=[{'source_list':e['source_list'],'candidate_id':e['source_candidate_id']} for e in entries]
        if verdict['action']!='keep':
            removed.append({'writer_key':key,'names':[e['name'] for e in entries],**verdict,'input_entries':references})
            crosswalk.extend({**r,'writer_key':key,'disposition':verdict['action'],'candidate_id':None} for r in references)
            continue
        name=verdict.get('canonical_name',entries[0]['name'])
        languages=list(dict.fromkeys(v for e in entries for v in e['writing_languages']))
        genres=list(dict.fromkeys(v for e in entries for v in e['genres']))
        works=list(dict.fromkeys(v for e in entries for v in e['representative_works']))
        contribution=verdict.get('achievement')
        if contribution is None:
            if len(entries)>1:raise ValueError(f'Overlapping writer needs reviewed neutral achievement: {key}')
            contribution=entries[0]['achievement']
        field=verdict.get('field','; '.join(genres+(['writing languages: '+ '; '.join(languages)] if languages else [])) or entries[0]['field'])
        for label,value in (('canonical_name',name),('achievement',contribution),('field',field)):
            if not isinstance(value,str) or not value.strip():raise ValueError(f'{key}: invalid {label}')
        row={'candidate_id':f'L{len(kept)+1:03d}','writer_key':key,'name':name,'credited_names':[name],
            'achievement':contribution,'field':field,'writing_languages':languages,'genres':genres,'representative_works':works,
            'main_reservation':verdict.get('main_reservation','; '.join(e['source_entry'].get('main_reservation','') for e in entries if e['source_entry'].get('main_reservation'))),
            'review_reason':verdict['reason'],'eligibility_review':verdict.get('eligibility_review','Not independently verified; requires review before dispatch.'),
            'flags':verdict.get('flags',[]),'input_entries':entries}
        kept.append(row); crosswalk.extend({**r,'writer_key':key,'disposition':'kept','candidate_id':row['candidate_id']} for r in references)
    if len(kept)<8:raise ValueError('Fewer than eight retained writers')
    if len(crosswalk)!=sum(d['candidate_count'] for d in inputs.values()):raise ValueError('Source accounting mismatch')
    return {'schema_version':1,'category':'literature','prize_year':2026,'list_id':'literature-2026','version':1,
        'prepared_by':'Codex consolidation of independent Codex and Claude drafts','research_cutoff':review.get('research_cutoff'),
        'prepared_on':review.get('prepared_on'),'candidate_count':len(kept),'candidate_order':'alphabetical_by_canonical_writer_key_not_rank',
        'nominator_stage':{'simulated_nominations':False,'actual_nominations_known':False},
        'scope':'Writer-centered reviewed union. One writer per entry; simulation packets omit draft provenance, reservations and review labels.',
        'inputs':inputs,'review_sha256':hashlib.sha256(review_path.read_bytes()).hexdigest(),
        'merge_summary':{'unique_writers':len(groups),'shared_writers':sum(len(v)>1 for v in groups.values()),
            'retained_writers':len(kept),'removed_writers':len(removed),'accounted_source_entries':len(crosswalk)},
        'candidates':kept,'removed_entries':removed,'source_crosswalk':crosswalk,
        'limitations':review.get('limitations',[])}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex',type=Path,default=DIRECTORY/'codex/candidates.json')
    parser.add_argument('--claude',type=Path,required=True)
    parser.add_argument('--review',type=Path,default=DIRECTORY/'merge/review_decisions.json')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    try:value=merge(args.codex,args.claude,args.review)
    except (OSError,ValueError,KeyError) as exc:parser.error(str(exc))
    content=json.dumps(value,ensure_ascii=False,indent=2)+'\n';target=DIRECTORY/'candidates.json'
    if args.check:
        if not target.is_file() or target.read_text()!=content:raise SystemExit('Canonical list differs from reviewed drafts')
    else:
        if target.exists() and target.read_text()!=content:raise SystemExit('Refusing to replace a different frozen candidate list')
        target.write_text(content)
        with (DIRECTORY/'candidates.csv').open('w',newline='') as f:
            writer=csv.writer(f,lineterminator="\n");writer.writerow(['candidate_id','name','achievement','field','credited_names'])
            for c in value['candidates']:writer.writerow([c['candidate_id'],c['name'],c['achievement'],c['field'],'; '.join(c['credited_names'])])
    print(f'Verified complete source accounting: {len(value["candidates"])} retained writers.')
if __name__=='__main__':main()
