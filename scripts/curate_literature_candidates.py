"""Apply the reviewed 50-writer selection to the archived 190-writer draft.

Preserves original IDs and full source accounting. Forecasting judgments and
public contender evidence are retained for audit, never added to blinded packets.
"""
import copy
import csv
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'agent-data/literature/candidates/codex'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    archive_path=DIRECTORY/'coverage-190.json';selection_path=DIRECTORY/'selection_50.json'
    archive=json.loads(archive_path.read_text());review=json.loads(selection_path.read_text())
    source=archive['candidates'];by_id={c['candidate_id']:c for c in source}
    selected=review['selected'];excluded=review['exclusions']
    if len(source)!=190 or len(by_id)!=190 or archive['candidate_count']!=190:raise ValueError('Expected the complete 190-writer archive')
    if len(selected)!=50 or review['selected_count']!=50:raise ValueError('Expected exactly 50 selections')
    if not set(selected)<=set(by_id) or not set(excluded)<=set(by_id) or set(selected)&set(excluded):raise ValueError('Unknown or conflicting selection IDs')
    kept=[];trimmed=[];crosswalk=[]
    for original in source:
        cid=original['candidate_id'];name=original['name']
        if cid in selected:
            decision=selected[cid]
            if decision['name']!=name or not decision['reason'].strip():raise ValueError(f'Selection/name mismatch: {cid}')
            if any(s not in review['sources'] for s in decision['source_ids']):raise ValueError(f'Unknown source: {cid}')
            entry=copy.deepcopy(original)
            entry.update(forecast_inclusion_reason=decision['reason'],selection_source_ids=decision['source_ids'],
                assessment_type='author_forecast_judgment_not_calibrated_probability',
                living_status='Retained under a working living-status assumption; no known death identified in the selection review. Targeted status checks, not an exhaustive current registry audit.')
            kept.append(entry);action='kept';reason=decision['reason']
        else:
            entry=copy.deepcopy(original)
            if cid in excluded:
                decision=excluded[cid]
                if decision['name']!=name:raise ValueError(f'Exclusion/name mismatch: {cid}')
                action='excluded_ineligible';reason=decision['reason']
                entry['living_status']='Deceased 26 August 2026, confirmed by publisher and institutional memorial.'
                entry['exclusion_source_ids']=decision['source_ids']
            else:
                action='trimmed_relative_likelihood'
                reason=('Lower relative 2026 forecasting priority than the retained 50, weighing whole-oeuvre distinction, maturity, international recognition and current contender visibility. '
                        'This is a comparative author judgment, not ineligibility. Draft-specific reservation: '+original['main_reservation'])
            entry.update(disposition=action,trim_reason=reason);trimmed.append(entry)
        crosswalk.append({'candidate_id':cid,'writer_key':original['writer_key'],'name':name,'disposition':action,'reason':reason})
    if len(kept)!=50 or len(trimmed)!=140 or len(crosswalk)!=190:raise ValueError('Incomplete source accounting')
    result=copy.deepcopy(archive)
    result.update(list_id='literature-2026-codex-50',version=2,source_type='curated_independent_author_forecast_list',
        research_cutoff=review['research_cutoff'],cutoff_timezone=review['cutoff_timezone'],candidate_count=50,
        scope=review['scope'],selection_method=review['method'],
        archive={'path':'coverage-190.json','sha256':sha(archive_path),'candidate_count':190},
        selection_review={'path':'selection_50.json','sha256':sha(selection_path),'selected':50,'removed':140},
        limitations=review['limitations']+['Countries_or_contexts retain biographical/literary contexts, not verified citizenship. Literary summaries and representative works are inherited from the original draft; selection sources document contender visibility or recognition only.'],
        candidates=kept,sources=review['sources'])
    (DIRECTORY/'candidates.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    with (DIRECTORY/'candidates.csv').open('w',newline='') as f:
        writer=csv.writer(f,lineterminator="\n");writer.writerow(['candidate_id','name','writing_languages','genres','representative_works','rationale','main_reservation','forecast_inclusion_reason'])
        for c in kept:writer.writerow([c['candidate_id'],c['name'],'; '.join(c['writing_languages']),'; '.join(c['genres']),'; '.join(c['representative_works']),c['rationale'],c['main_reservation'],c['forecast_inclusion_reason']])
    audit={'schema_version':1,'category':'literature','research_cutoff':review['research_cutoff'],
        'input_candidate_count':190,'retained_count':50,'removed_count':140,'ineligibility_exclusions':len(excluded),
        'archive_sha256':sha(archive_path),'selection_review_sha256':sha(selection_path),
        'source_crosswalk':crosswalk,'trimmed_entries':trimmed,'sources':review['sources']}
    (DIRECTORY/'trimmed_entries.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
    lines=['# 50 Literature candidates for 2026','',
        'The active Codex list, reduced from the recovered 190-writer draft on 6 October 2026. '
        'These are the 50 most plausible winners within that original pool by author judgment, combining whole-oeuvre achievement with current public contender evidence. '
        'The list is alphabetical; the row order and original candidate IDs are not a ranking.','',
        '| ID | Writer | Writing languages | Representative works |',
        '|---|---|---|---|']
    for c in kept:lines.append(f'| {c["candidate_id"]} | {c["name"]} | {"; ".join(c["writing_languages"])} | {"; ".join(c["representative_works"])} |')
    lines+=['','Selection reasons are in `selection_50.json` and `candidates.json`. '
            'The original 190 writers are preserved in `coverage-190.json`; `trimmed_entries.json` accounts for all 140 removals. '
            'One removal is an eligibility exclusion: Péter Nádas died before the announcement, as confirmed by [his publisher](https://www.rowohlt.de/magazin/aus-dem-verlag/wir-trauern-um-peter-nadas). '
            'The other 139 are comparative forecasting cuts, not judgments that those writers cannot win.','',
            'Current public contender sources include the [6 October Betsson release](https://www.prnewswire.com/news-releases/betsson-group-odds-favourites-for-the-2026-nobel-prize-in-literature-302899576.html) '
            'and [29 September Literary Hub coverage](https://lithub.com/here-are-the-bookies-odds-for-the-2026-nobel-prize-in-literature/). '
            'Selection does not copy market order or interpret odds as calibrated probabilities. Sources support public visibility, recognition and targeted eligibility checks; '
            'the inherited literary summaries are author assessments. Actual nominations and committee preferences are unknown.','']
    (DIRECTORY/'candidates.md').write_text('\n'.join(lines))
    print('Active list: 50; archive: 190; removals: 140 (139 comparative cuts, one confirmed eligibility exclusion).')

if __name__=='__main__':main()
