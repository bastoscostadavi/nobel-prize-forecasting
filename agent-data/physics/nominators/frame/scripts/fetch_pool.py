# Seeded OpenAlex author samples per physics category (see frame/README.md)
import json,urllib.request,urllib.parse,time,os,sys
sys.path.insert(0,'..'); sys.path.insert(0,'.')
from topicmap import M,EXTRA
SEED=2026; SAMPLE=2000
cats={}
for k,v in {**M,**EXTRA}.items(): cats.setdefault(v,[]).append(k)
def get(u):
  for i in range(15):
    try: return json.load(urllib.request.urlopen(u))
    except urllib.error.HTTPError as e: time.sleep(60 if e.code==429 else 3)
    except Exception: time.sleep(3)
  raise SystemExit('fail '+u)
for c,ts in cats.items():
  fn='pool/cand_'+c.replace('/','_').replace(' ','_')+'.jsonl'
  if os.path.exists(fn+'.done'): continue
  out=open(fn,'w'); n=0
  for page in range(1,SAMPLE//200+1):
    u='https://api.openalex.org/authors?'+urllib.parse.urlencode({'filter':'summary_stats.h_index:>39,works_count:<5001,topics.id:'+'|'.join(ts),
      'sample':SAMPLE,'seed':SEED,'per-page':200,'page':page,
      'select':'id,display_name,works_count,cited_by_count,summary_stats,last_known_institutions,topics,orcid','mailto':'davi.costa@usp.br'},safe=':|,><')
    d=get(u)
    if page==1: print(c,'population',d['meta']['count'],flush=True)
    for a in d['results']: out.write(json.dumps(a)+'\n')
    n+=len(d['results']); out.flush()
    if len(d['results'])<200: break
    time.sleep(0.5)
  out.close(); open(fn+'.done','w').write(str(n)); print(c,n,flush=True)
print('ALLDONE')
