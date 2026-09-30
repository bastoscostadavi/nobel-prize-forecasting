import json,re,html,csv
arr=json.load(open('kva_contacts.json'))
out=[]
for a in arr:
  names=[x['name'] for x in a['titles']]
  if 'Class for physics' not in names and 'Class for astronomy and space science' not in names: continue
  slug=a['link'].rstrip('/').split('/')[-1]
  t=open(f'kvapages/{slug}.html').read()
  t=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S)
  t=html.unescape(re.sub(r'<[^>]+>','\n',t))
  lines=[l.strip() for l in t.split('\n') if l.strip()]
  org=''
  if 'Organisation' in lines:
    i=len(lines)-1-lines[::-1].index('Organisation'); org=lines[i+1] if lines[i+1]!='Member of' else ''
  cls='physics' if 'Class for physics' in names else 'astronomy and space science'
  nat={'1':'Swedish','svensk':'Swedish','2':'foreign'}.get(a['nationality'],'unknown')
  roles=[n for n in names if not n.startswith('Class')]
  out.append(dict(name=html.unescape(a['title']),swedish_or_foreign=nat,kva_class=cls,position=html.unescape(a['position']).strip(),affiliation=org,other_roles='; '.join(roles),link=a['link']))
json.dump(out,open('kva_parsed.json','w'),ensure_ascii=False,indent=0)
for o in out: print(o['swedish_or_foreign'],'|',o['name'],'|',o['position'],'|',o['affiliation'],'|',o['other_roles'])
