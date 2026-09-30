import json,csv,html
d=json.load(open('laur.json'))
C='condensed matter';P='particle/nuclear';A='astro/cosmology';O='AMO/quantum optics';Q='quantum information';OP='optics/photonics';S='statistical/complex systems';X='other'
sub={'97':C,'99':C,'106':P,'112':A,'113':P,'124':P,'126':C,'128':C,'130':C,'138':P,'143':A,'144':A,'149':C,'150':C,'152':O,'153':O,'154':O,'155':C,'156':C,'157':C,'158':P,
'738':O,'739':O,'740':O,'776':P,'777':P,'778':P,'792':O,'793':O,'804':A,'814':C,'827':P,'849':C,'850':C,'864':A,'865':A,'866':A,'876':O,'877':O,'907':OP,'908':OP,'919':P,'920':P,
'929':C,'930':C,'942':A,'943':A,'961':OP,'962':OP,'973':A,'974':A,'975':A,'988':A,'989':A,'990':A,'1000':X,'1001':S,'999':X,'1012':Q,'1013':Q,'1014':Q,'1026':O,'1027':O,'1028':O,'1037':S,'1038':X,'1050':Q,'1051':Q,'1052':Q}
note={'1000':'climate physics','999':'climate physics','1038':'machine learning / computer science','1037':'biophysics / neural networks','974':'exoplanets','975':'exoplanets','1050':'superconducting circuits (also condensed matter)','1051':'superconducting circuits (also condensed matter)','1052':'superconducting circuits (also condensed matter)','988':'mathematical physics / general relativity','1026':'attosecond physics','1027':'attosecond physics','1028':'attosecond physics'}
rows=[]
for l in d['laureates']:
  if 'death' in l or 'fullName' not in l: continue
  for p in l['nobelPrizes']:
    if p['category']['en']!='Physics': continue
    affs=[a for a in p.get('affiliations',[]) if 'name' in a]
    rows.append(dict(name=l['fullName']['en'],year=p['awardYear'],motivation=p['motivation']['en'],
      affiliation_at_award='; '.join(html.unescape(a['name']['en']) for a in affs),
      country='; '.join(x for x in dict.fromkeys(a.get('countryNow',a.get('country',{})).get('en','') for a in affs) if x),
      birth_country=l['birth']['place']['countryNow']['en'] if 'place' in l['birth'] else '',
      subfield=sub[l['id']],subfield_note=note.get(l['id'],''),birth_year=l['birth']['date'][:4],nobel_id=l['id'],wikidata=l['wikidata']['id']))
rows.sort(key=lambda r:(r['year'],r['name']))
w=csv.DictWriter(open('/Users/davicosta/Desktop/projects/nobel-prize-forecasting/agent-data/physics/nominators/frame/laureates.csv','w',newline=''),fieldnames=list(rows[0]))
w.writeheader();w.writerows(rows)
from collections import Counter
print(len(rows),Counter(r['subfield'] for r in rows))
print(Counter(r['country'].split(';')[0] for r in rows))
