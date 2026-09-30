import json,urllib.request,urllib.parse,time
from topicmap import EXTRA
def get(params):
  params=dict(params); params['mailto']='davi.costa@usp.br'
  u='https://api.openalex.org/works?'+urllib.parse.urlencode(params,safe=':|,><')
  for i in range(8):
    try: return json.load(urllib.request.urlopen(u))
    except Exception as e: time.sleep(3)
Y='publication_year:2016-2025,type:article|review,is_retracted:false'
res={}
for tag,cf in [('all',''),('hc',',cited_by_count:>200')]:
  c={}
  for f in ['primary_topic.field.id:31','primary_topic.id:'+'|'.join(EXTRA)]:
    d=get({'filter':f'{f},{Y}{cf}','group_by':'authorships.institutions.continent'})
    for g in d['group_by']:
      if g['key']!='unknown': c[g['key_display_name']]=c.get(g['key_display_name'],0)+g['count']
  res[tag]=c
  time.sleep(1)
json.dump(res,open('oa_cont.json','w'),indent=1); print(res)
