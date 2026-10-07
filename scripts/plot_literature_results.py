"""Render Literature committee and one-shot figures from validated source hashes."""
import hashlib
import json
import unicodedata
from collections import Counter
import literature_oneshot as sol
import plot_physics_prediction_distributions as style
ROOT=style.ROOT
DESCRIPTIONS={
    'Mircea Cărtărescu':'Visionary fiction exploring memory, consciousness and the body',
    'Anne Carson':'Poetry and hybrid forms joining classical and contemporary experience',
    'Thomas Pynchon':'Encyclopedic fiction connecting systems, history and power',
    'Hélène Cixous':'Experimental writing across fiction, essay and theatre',
    'Gerald Murnane':'Distinctive fiction of landscape, memory and mental images',
    'Adonis':'Renewal of Arabic poetic language through myth and modernist forms',
    'Can Xue':'Surreal, formally inventive fiction of consciousness and estrangement',
}
COLORS=['#167D8D','#7162AA','#C17B35','#4FA3AE','#9A8CC8','#83986A','#AC7680']
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical(name):
    name=unicodedata.normalize('NFC',name)
    return {'Mircea Cartarescu':'Mircea Cărtărescu'}.get(name,name)
def label(parts):
    if not parts:return 'No award'
    if len(parts)!=1 or len(parts[0]['laureates'])!=1:raise ValueError('Expected a single writer')
    return canonical(parts[0]['laureates'][0])
def oneshots():
    summary=json.loads((sol.ARM_ROOT/'posthoc_transcription_summary.json').read_text())
    if summary['source_record_count']!=25 or len(summary['source_records'])!=25:raise ValueError('Expected 25 Sol records')
    counts=Counter()
    for source in summary['source_records']:
        directory=sol.ARM_ROOT/source['prediction_id']
        for filename,key in [('response.txt','response_sha256'),('result.json','result_sha256'),('request.json','request_sha256'),('runtime.jsonl','runtime_sha256')]:
            if digest(directory/filename)!=source[key]:raise ValueError(f'Sol source changed: {directory/filename}')
        sol.shared.validate_result(directory)
        result=json.loads((directory/'result.json').read_text());parts=result['prize_configuration']['prize_parts']
        if len(parts)!=1 or len(parts[0]['credited_names'])!=1:raise ValueError('Expected one Sol primary writer')
        counts[canonical(parts[0]['credited_names'][0])]+=1
    opus=json.loads((ROOT/'results/literature/oneshot/claude-opus-5-5/final_summary.json').read_text())
    if opus['completed_predictions']!=25 or len(opus['source_records'])!=25:raise ValueError('Expected 25 Opus records')
    for source in opus['source_records']:
        if digest(ROOT/source['path'])!=source['sha256'] or digest(ROOT/source['runtime_path'])!=source['runtime_sha256']:raise ValueError('Opus source changed')
    other=Counter({canonical(row['laureate']):row['count'] for row in opus['configuration_counts']})
    if sum(counts.values())!=25 or sum(other.values())!=25:raise ValueError('One-shot counts differ')
    style.SLATE_COLORS.update({n:COLORS[i%len(COLORS)] for i,n in enumerate(sorted(counts|other))})
    rows=max(len(counts),len(other))
    style.plot('literature-openai-oneshot-distribution.png','OpenAI one-shot','GPT-6.1 Sol',counts,rows)
    style.plot('literature-claude-oneshot-distribution.png','Claude one-shot','Claude Opus 5.5',other,rows)
    print('One-shot counts:',{'sol':dict(counts),'opus':dict(other)})
def committees():
    summary=json.loads((ROOT/'results/literature/final_summary.json').read_text())
    if summary['completed_simulations']!=50 or len(summary['source_decisions'])!=50:raise ValueError('Expected 50 validated decisions')
    for source in summary['source_decisions']:
        if digest(ROOT/source['path'])!=source['sha256']:raise ValueError(f'Decision changed: {source["path"]}')
    def counts(rows):
        result=Counter()
        for row in rows:result[label(row['prize_parts'])]+=row['count']
        return result
    aggregate=counts(summary['recipient_configurations']);terra=counts(summary['models']['gpt-5.6-terra']['configurations']);claude=counts(summary['models']['claude-sonnet-5-5']['configurations'])
    if aggregate!=terra+claude or sum(aggregate.values())!=50 or sum(terra.values())!=25 or sum(claude.values())!=25:raise ValueError('Committee counts differ')
    style.SLATE_COLORS.update({n:COLORS[i%len(COLORS)] for i,n in enumerate(sorted(aggregate))})
    style.ranked_plot('literature-committee-top5.png','2026 Nobel Prize in Literature',aggregate,DESCRIPTIONS,limit=5)
    style.ranked_plot('literature-committee-full-distribution.png','2026 Nobel Prize in Literature',aggregate,DESCRIPTIONS)
    rows=max(len(terra),len(claude))
    style.plot('literature-terra-committee-distribution.png','Terra committee','GPT-5.6 Terra',terra,rows)
    style.plot('literature-claude-committee-distribution.png','Claude committee','Claude Sonnet 5.5',claude,rows)
    print('Committee counts:',{'aggregate':dict(aggregate),'terra':dict(terra),'claude':dict(claude)})
def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--oneshot-only',action='store_true');args=parser.parse_args()
    style.FIGURES.mkdir(parents=True,exist_ok=True);oneshots()
    if not args.oneshot_only:committees()
if __name__=='__main__':main()
