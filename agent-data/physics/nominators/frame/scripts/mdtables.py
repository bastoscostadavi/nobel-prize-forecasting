import json
from regions import region,ORDER
s=json.load(open('shares_computed.json')); r=json.load(open('oa_shares.json')); cont=json.load(open('oa_cont.json'))
CATS=['condensed matter','particle/nuclear','astro/cosmology','AMO/quantum optics','quantum information','optics/photonics','statistical/complex systems','other']
L=[]
def p(x): L.append(x)
tot={t:sum(s[f'{t}_ext_cat'].values()) for t in ['all','hc']}
p('### Table 1. OpenAlex native subfields, strict field 31 only\n')
p('| OpenAlex subfield | works 2016-25 | share | works cited>200 | share |\n|---|---:|---:|---:|---:|')
hc=dict((k,(v,q)) for k,v,q in s['hc_native'])
for k,v,q in s['all_native']: p(f'| {k} | {v:,} | {100*q:.1f}% | {hc[k][0]:,} | {100*hc[k][1]:.1f}% |')
p(f"| **Total** | **{sum(v for _,v,_ in s['all_native']):,}** | | **{sum(v for _,v,_ in s['hc_native']):,}** | |\n")
p('### Table 2. Project categories (topic-level mapping)\n')
p('| Category | strict: all | strict: cited>200 | **extended: all** | extended: cited>200 |\n|---|---:|---:|---:|---:|')
for c in CATS:
  a=s['all_strict_cat'];b=s['hc_strict_cat'];e=s['all_ext_cat'];f=s['hc_ext_cat']
  p(f'| {c} | {100*a[c]/sum(a.values()):.1f}% | {100*b[c]/sum(b.values()):.1f}% | **{100*e[c]/sum(e.values()):.1f}%** | {100*f[c]/sum(f.values()):.1f}% |')
p(f"| N works | {sum(s['all_strict_cat'].values()):,} | {sum(s['hc_strict_cat'].values()):,} | {tot['all']:,} | {tot['hc']:,} |\n")
p('### Table 3. Countries: share of works with at least one author in the country (extended set; full counting, so columns sum to more than 100%)\n')
p('| Country | all works | cited>200 |\n|---|---:|---:|')
A=s['all_country_ext'];H=s['hc_country_ext']
for cc,v in sorted(((k,v) for k,v in A.items() if k!='unknown'),key=lambda x:-x[1])[:20]:
  p(f'| {cc} | {100*v/tot["all"]:.1f}% | {100*H.get(cc,0)/tot["hc"]:.1f}% |')
p(f'| (no country known) | {100*A.get("unknown",0)/tot["all"]:.1f}% | {100*H.get("unknown",0)/tot["hc"]:.1f}% |\n')
p('### Table 4. Continents: share of works with at least one author on the continent (extended set)\n')
p('| Continent | all works | cited>200 |\n|---|---:|---:|')
for k in ['Europe','Asia','North America','South America','Oceania','Africa']:
  p(f'| {k} | {100*cont["all"][k]/tot["all"]:.1f}% | {100*cont["hc"][k]/tot["hc"]:.1f}% |')
def reg(cc):
  g={}
  for k,v in cc.items():
    x=region(k)
    if x: g[x]=g.get(x,0)+v
  T=sum(g.values()); return {x:g.get(x,0)/T for x in ORDER}
p('\n### Table 5. Regions: share of author-country mentions (normalized to 100%; basis for pool stratification)\n')
p('| Region | all works | cited>200 |\n|---|---:|---:|')
ra=reg(A);rh=reg(H)
for x in ORDER: p(f'| {x} | {100*ra[x]:.1f}% | {100*rh[x]:.1f}% |')
p('\n### Table 6. Region mix within each category (all works 2016-2025, normalized author-country mentions)\n')
p('| Category | '+' | '.join(ORDER)+' |\n|---|'+'---:|'*len(ORDER))
for c in CATS:
  rr=reg(s[f'all_country_{c}']); p(f'| {c} | '+' | '.join(f'{100*rr[x]:.0f}' for x in ORDER)+' |')
p('\nSame, restricted to works cited>200:\n')
p('| Category | '+' | '.join(ORDER)+' |\n|---|'+'---:|'*len(ORDER))
for c in CATS:
  rr=reg(s[f'hc_country_{c}']); p(f'| {c} | '+' | '.join(f'{100*rr[x]:.0f}' for x in ORDER)+' |')
open('md_tables.md','w').write('\n'.join(L)); print('\n'.join(L))
