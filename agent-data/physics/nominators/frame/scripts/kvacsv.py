import json,csv,re
out=json.load(open('kva_parsed.json'))
C='condensed matter';P='particle/nuclear';A='astro/cosmology';O='AMO/quantum optics';Q='quantum information';OP='optics/photonics';S='statistical/complex systems';X='other'
inf={'Igor Abrikosov':C,'Lars Bergström':P,'Annica Black-Schaffer':C,'Klaus Blaum':P,'Olga Botner':P,'Mohamed Bourennane':Q,'Richard Brenner':P,'Gert Brodin':X,'Eleanor Campbell':O,
'Per Carlson':P,'Tord Claeson':C,'Ulf Danielsson':P,'Per Delsing':Q,'Paula Anna-Maria Eerola':P,'Torleif Ericson':P,'Olle Eriksson':C,'Claes Fahlander':P,'Tünde Fülöp':X,
'Steven M Girvin':C,'Thors Hans Hansson':C,'Lene Vestergaard Hau':O,'David Haviland':C,'Björgvin Hjörvarsson':C,'Sven-Olof Holmgren':P,'Olle Inganäs':C,'Gunnar Ingelman':P,
'Anders Irbäck':S,'Cecilia Jarlskog':P,'Börje Johansson':C,'Göran Johansson':Q,'Björn Jonson':P,'Mats Jonson':C,'Anders Karlhede':P,'Erik Karlsson':C,'Stefan Kröll':O,
'Anne L’Huillier':O,'Mats Larsson':O,'Jon Magne Leinaas':C,'Ingolf Lindau':C,'Ingvar Lindgren':O,'Eva Lindroth':O,'Heiner Linke':C,'Ingemar Lundström':C,'Bernhard Mehlig':S,
'Petter Minnhagen':S,'Ellen Moons':C,'Nils Mårtensson':C,'Thomas Nilsson':P,'Joseph Nordgren':C,'Eva Olsson':C,'Mark Pearce':A,'Hiranya Peiris':A,'Carsten Peterson':S,
'Elisabeth Rachlew':O,'Stephanie Reimann':C,'Dan-Olof Riska':P,'Dirk Rudolph':P,'Hans Ryde':P,'Lars Samuelson':C,'Reinhold Schuch':O,'Alexander N. Skrinskiy':P,
'Lennart Stenflo':X,'Sara Strandberg':P,'Bo Sundqvist':P,'Sune Svanberg':OP,'Julia Tjus':A,'Yoshinori Tokura':C,'Claes-Göran Wahlström':OP,'John Wettlaufer':X,
'Frank Wilczek':P,'Torsten Åkesson':P,'Barbro Åsman':P}
phys_comm={'Mark Pearce','Olle Eriksson','Göran Johansson','Stefan Kröll','Eva Lindroth','Ulf Danielsson','Bernhard Mehlig','Eva Olsson'}
chem_comm={'Heiner Linke','Andrei Chabes','Peter Somfai','Emma Sparr','Xiaodong Zou','Daniel Aili','Peter Brzezinski','Johan Åqvist'}
kw=[('particle','particle/nuclear'),('subatomic','particle/nuclear'),('nuclear','particle/nuclear'),('astro','astro/cosmology'),('cosmolog','astro/cosmology'),('astronom','astro/cosmology'),('atomic','AMO/quantum optics'),('molecular physics','AMO/quantum optics'),('quantum','quantum/other quantum'),('magnetism','condensed matter'),('condensed','condensed matter'),('nano','condensed matter'),('plasma','other (plasma)'),('complex systems','statistical/complex systems'),('space physics','astro/cosmology (space physics)'),('x-ray','condensed matter (spectroscopy)'),('synchrotron','condensed matter (spectroscopy)'),('ion physics','particle/nuclear (ion physics)'),('microscopy','condensed matter'),('electronics','condensed matter'),('theoretical physics','(theoretical, unspecified)'),('mathematical physics','(mathematical physics)'),('radio astronomy','astro/cosmology')]
rows=[]
for o in out:
  pos=o['position'].lower()
  st=next((v for k,v in kw if k in pos),'')
  if o['kva_class']!='physics': sub='astro/cosmology'
  else: sub=inf[o['name']]
  flag=''
  if o['name'] in phys_comm: flag='2026 PHYSICS COMMITTEE - exclude from nominator pool (category 2 nominator in own right)'
  if o['name'] in chem_comm: flag='2026 CHEMISTRY COMMITTEE member (Chair) - flag'
  rows.append(dict(name=o['name'],swedish_or_foreign=o['swedish_or_foreign'],kva_class=o['kva_class'],position=o['position'],affiliation=o['affiliation'] if o['affiliation']!='International affairs' else '',
    subfield_stated=st,subfield_inferred=sub,other_kva_roles=o['other_roles'],committee_flag=flag,kva_url=o['link']))
rows.sort(key=lambda r:(r['kva_class']!='physics',r['name']))
w=csv.DictWriter(open('/Users/davicosta/Desktop/projects/nobel-prize-forecasting/agent-data/physics/nominators/frame/kva_physics.csv','w',newline=''),fieldnames=list(rows[0]))
w.writeheader();w.writerows(rows)
from collections import Counter
print(Counter((r['kva_class'],r['swedish_or_foreign']) for r in rows))
print(Counter(r['subfield_inferred'] for r in rows if r['kva_class']=='physics'))
