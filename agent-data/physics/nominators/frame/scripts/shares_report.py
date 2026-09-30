import json
from topicmap import M,EXTRA
from regions import region,ORDER
r=json.load(open('oa_shares.json'))
CATS=['condensed matter','particle/nuclear','astro/cosmology','AMO/quantum optics','quantum information','optics/photonics','statistical/complex systems','other']
def pct(x,t): return f'{100*x/t:.1f}%'
out={}
for tag in ['all','hc']:
  nat=r[f'{tag}_native']; T=sum(nat.values())
  out[f'{tag}_native']=[(k,v,v/T) for k,v in sorted(nat.items(),key=lambda x:-x[1])]
  cat={c:0 for c in CATS}
  for t,v in r[f'{tag}_topics31'].items(): cat[M[t]]+=v
  strict=dict(cat)
  for t,v in r[f'{tag}_extra'].items(): cat[EXTRA[t]]+=v
  out[f'{tag}_strict_cat']=strict; out[f'{tag}_ext_cat']=cat
  # region shares extended overall = sum across categories
  tot={}
  for c in CATS:
    for cc,v in r[f'{tag}_country_{c}'].items(): tot[cc]=tot.get(cc,0)+v
  out[f'{tag}_country_ext']=tot
  for c in CATS: out[f'{tag}_country_{c}']=r[f'{tag}_country_{c}']
json.dump(out,open('shares_computed.json','w'),indent=1)
def regshares(cc):
  reg={}
  for k,v in cc.items():
    g=region(k)
    if g: reg[g]=reg.get(g,0)+v
  T=sum(reg.values()); return {g:reg.get(g,0)/T for g in ORDER}
for tag in ['all','hc']:
  print(tag,'native',[(k,v,f'{p:.3f}') for k,v,p in out[f'{tag}_native']])
  s=out[f'{tag}_strict_cat'];e=out[f'{tag}_ext_cat']
  print(tag,'strict',{k:f'{v/sum(s.values()):.3f}' for k,v in s.items()}, sum(s.values()))
  print(tag,'ext',{k:f'{v/sum(e.values()):.3f}' for k,v in e.items()}, sum(e.values()))
  print(tag,'regions',{k:f'{v:.3f}' for k,v in regshares(out[f'{tag}_country_ext']).items()})
