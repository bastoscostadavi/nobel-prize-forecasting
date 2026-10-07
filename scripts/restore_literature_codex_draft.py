"""Normalize the recovered 190-writer Literature coverage archive (no new research).

Writes coverage-190.json/csv; never replaces the curated active candidate list."""
import csv
import hashlib
import json
import re
import unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'agent-data/literature/candidates/codex'

def key(name):
    return re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',name).encode('ascii','ignore').decode().lower()).strip('-')

def main():
    source=DIRECTORY/'recovered_seed.json'
    seed=json.loads(source.read_text())
    rows=sorted(seed['candidates'],key=lambda c:key(c['name']))
    candidates=[]
    for i,c in enumerate(rows,1):
        works=c['works'].split('; ')
        if c['name']=='Raúl Zurita':works=['Purgatory','Anteparadise']
        candidates.append({'candidate_id':f'C{i:03d}','writer_key':key(c['name']),'name':c['name'],
            'credited_names':[c['name']],'countries_or_contexts':c['countries'].split('; '),
            'writing_languages':c['languages'].split('; '),'genres':c['genres'].split('; '),
            'representative_works':works,'achievement':c['rationale']+' Representative works: '+ '; '.join(works)+'.',
            'field':c['genres']+'; writing languages: '+c['languages'],
            'rationale':c['rationale'],'main_reservation':c['reservation'],
            'living_status':'No death identified in original draft; not individually reverified.',
            'assessment_type':'author_judgment_not_probability','source_ids':[],
            'flags':(['former_swedish_academy_member'] if c['name'] in ('Kerstin Ekman','Tua Forsström') else [])})
    value={'schema_version':1,'category':'literature','prize_year':2026,'list_id':'literature-2026-codex-draft',
        'prepared_by':'Codex','research_cutoff':'2026-10-03','restored_on':'2026-10-06',
        'source_type':'recovered_independent_author_longlist','candidate_count':len(candidates),
        'candidate_order':'alphabetical_by_writer_not_rank','nominator_stage':{'simulated_nominations':False,'actual_nominations_known':False},
        'recovery':{'source':'recovered_seed.json','sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                    'note':seed['recovery_note'],'editorial_correction':'Zurita representative title normalized to Anteparadise.'},
        'limitations':['Broad coverage draft, not a forecast ranking or evidence of actual nomination.',
            'Original work stopped before per-author source verification; empty source_ids explicitly record that limitation.',
            'Countries_or_contexts denote literary and biographical context, not verified citizenship.',
            'Living status and oeuvre details require review before final simulation input is frozen.'],
        'candidates':candidates,'sources':{}}
    (DIRECTORY/'coverage-190.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    with (DIRECTORY/'coverage-190.csv').open('w',newline='') as f:
        writer=csv.writer(f,lineterminator="\n");writer.writerow(['candidate_id','name','writing_languages','genres','representative_works','rationale','main_reservation'])
        for c in candidates:writer.writerow([c['candidate_id'],c['name'],'; '.join(c['writing_languages']),'; '.join(c['genres']),'; '.join(c['representative_works']),c['rationale'],c['main_reservation']])
    print(f'Restored archive of {len(candidates)} draft writers with explicit research limitations.')
if __name__=='__main__':main()
