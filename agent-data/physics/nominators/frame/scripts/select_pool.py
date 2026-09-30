# Stratified selection of the international pool (see frame/README.md)
import json,glob,csv,random,unicodedata,sys
sys.path.insert(0,'.')
from topicmap import M,EXTRA
from regions import region
SEED=2026; N=300
TOPIC2CAT={**M,**EXTRA}
CATS=['condensed matter','particle/nuclear','astro/cosmology','AMO/quantum optics','quantum information','optics/photonics','statistical/complex systems','other']
S=json.load(open('shares_computed.json'))
def norm(s): return ''.join(ch for ch in unicodedata.normalize('NFKD',s.lower()) if not unicodedata.combining(ch)).replace('.','').replace('-',' ').strip()
PHYS={norm(x) for x in ['Mark Pearce','Olle Eriksson','Göran Johansson','Stefan Kröll','Eva Lindroth','Ulf Danielsson','Bernhard Mehlig','Eva Olsson']}
CHEM={norm(x) for x in ['Heiner Linke','Andrei Chabes','Peter Somfai','Emma Sparr','Xiaodong Zou','Daniel Aili','Peter Brzezinski','Johan Åqvist']}
LAUR={norm(r['name']) for r in csv.DictReader(open('/Users/davicosta/Desktop/projects/nobel-prize-forecasting/agent-data/physics/nominators/frame/laureates.csv'))}
# 1. candidates: primary (top) topic must map to the category
cand={c:[] for c in CATS}; seen=set(); stats={}
for f in sorted(glob.glob('pool/cand_*.jsonl')):
  raw=[json.loads(l) for l in open(f)]
  for a in raw:
    if not a.get('topics') or not a.get('last_known_institutions'): continue
    top=a['topics'][0]['id'].split('/')[-1]
    c=TOPIC2CAT.get(top)
    if c is None or a['id'] in seen: continue
    inst=a['last_known_institutions'][0]; cc=inst.get('country_code') or ''
    nm=norm(a['display_name'])
    if nm in PHYS and cc=='SE': continue   # 2026 physics committee: excluded
    seen.add(a['id'])
    cand[c].append(dict(name=a['display_name'],openalex_id=a['id'].split('/')[-1],institution=inst.get('display_name',''),country=cc,
      region=region(cc) or 'unknown',subfield=c,primary_topic=a['topics'][0]['display_name'],h_index=a['summary_stats']['h_index'],
      works_count=a['works_count'],cited_by_count=a['cited_by_count'],orcid=(a.get('orcid') or '').replace('https://orcid.org/',''),
      flag=('2026 CHEMISTRY COMMITTEE' if nm in CHEM and cc=='SE' else '')+('Nobel laureate (name match)' if nm in LAUR else '')))
  stats[f]=len(raw)
# 2. targets: N x category share (extended, all works) x country share within category (normalized mentions)
def lr(weights,total):
  T=sum(weights.values()); ex={k:total*v/T for k,v in weights.items()}
  base={k:int(v) for k,v in ex.items()}; rem=total-sum(base.values())
  for k in sorted(ex,key=lambda k:-(ex[k]-base[k]))[:rem]: base[k]+=1
  return base
catT=lr(S['all_ext_cat'],N)
rng=random.Random(SEED)
chosen=[]; alloc=[]
for c in CATS:
  cw={k:v for k,v in S[f'all_country_{c}'].items() if k!='unknown'}
  tgt={k:v for k,v in lr(cw,catT[c]).items() if v>0}
  pool=sorted(cand[c],key=lambda r:r['openalex_id']); rng.shuffle(pool)
  used=set(); deficit=[]
  for cc,k in sorted(tgt.items(),key=lambda x:-x[1]):
    got=[r for r in pool if r['country']==cc and r['openalex_id'] not in used][:k]
    for r in got: used.add(r['openalex_id']); r['stratum']=f'{c}|{cc}'; chosen.append(r)
    if len(got)<k: deficit.append((cc,k-len(got)))
    alloc.append(dict(subfield=c,country=cc,target=k,filled_exact=len(got)))
  for cc,k in deficit:  # fill from same region, then anywhere in category
    reg=region(cc)
    got=[r for r in pool if r['region']==reg and r['openalex_id'] not in used][:k]
    if len(got)<k: got+= [r for r in pool if r['openalex_id'] not in used and r not in got][:k-len(got)]
    for r in got: used.add(r['openalex_id']); r['stratum']=f'{c}|{cc}->substitute'; chosen.append(r)
json.dump(alloc,open('pool/alloc.json','w'),indent=0)
fields=['name','openalex_id','institution','country','region','subfield','primary_topic','h_index','works_count','cited_by_count','orcid','stratum','flag']
w=csv.DictWriter(open('/Users/davicosta/Desktop/projects/nobel-prize-forecasting/agent-data/physics/nominators/frame/international_pool.csv','w',newline=''),fieldnames=fields)
w.writeheader(); w.writerows(chosen)
from collections import Counter
print('raw per file',stats); print('candidates',{c:len(v) for c,v in cand.items()})
print('cat targets',catT); print('chosen',len(chosen),Counter(r['subfield'] for r in chosen))
print('regions',Counter(r['region'] for r in chosen)); print('subst',sum('substitute' in r['stratum'] for r in chosen))
print('flags',[ (r['name'],r['flag']) for r in chosen if r['flag']])
