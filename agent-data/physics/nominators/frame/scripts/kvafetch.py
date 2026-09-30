import json,subprocess,re,html,os
arr=json.load(open('kva_contacts.json'))
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
for a in arr:
  ids=[x['term_id'] for x in a['titles']]
  if 1332 in ids or 1326 in ids:
    slug=a['link'].rstrip('/').split('/')[-1]
    f=f'kvapages/{slug}.html'
    if not os.path.exists(f): subprocess.run(['curl','-sL','-A',UA,a['link'],'-o',f])
