import json,urllib.request,urllib.parse,time
from topicmap import M,EXTRA
BASE='https://api.openalex.org/works'
def get(params):
  params=dict(params); params['mailto']='davi.costa@usp.br'
  u=BASE+'?'+urllib.parse.urlencode(params,safe=':|,><')
  for i in range(5):
    try: return json.load(urllib.request.urlopen(u))
    except Exception as e: print('retry',e); time.sleep(2)
Y='publication_year:2016-2025,type:article|review,is_retracted:false'
res={}
for tag,cf in [('all',''),('hc',',cited_by_count:>200')]:
  # native subfields, strict field 31
  d=get({'filter':f'primary_topic.field.id:31,{Y}{cf}','group_by':'primary_topic.subfield.id'})
  res[f'{tag}_native']={g['key_display_name']:g['count'] for g in d['group_by']}
  res[f'{tag}_native_total']=d['meta']['count']
  # topic counts strict
  d=get({'filter':f'primary_topic.field.id:31,{Y}{cf}','group_by':'primary_topic.id','per-page':'200'})
  res[f'{tag}_topics31']={g['key'].split('/')[-1]:g['count'] for g in d['group_by']}
  # extras
  ex='|'.join(EXTRA)
  d=get({'filter':f'primary_topic.id:{ex},{Y}{cf}','group_by':'primary_topic.id','per-page':'200'})
  res[f'{tag}_extra']={g['key'].split('/')[-1]:g['count'] for g in d['group_by']}
  # countries strict field 31
  d=get({'filter':f'primary_topic.field.id:31,{Y}{cf}','group_by':'authorships.institutions.country_code','per-page':'200'})
  res[f'{tag}_country31']={g['key'].split('/')[-1]:g['count'] for g in d['group_by']}
  # countries extras
  d=get({'filter':f'primary_topic.id:{ex},{Y}{cf}','group_by':'authorships.institutions.country_code','per-page':'200'})
  res[f'{tag}_countryextra']={g['key'].split('/')[-1]:g['count'] for g in d['group_by']}
  # countries per category (extended)
  cats={}
  for k,v in {**M,**EXTRA}.items(): cats.setdefault(v,[]).append(k)
  for c,ts in cats.items():
    cc={}
    for i in range(0,len(ts),50):
      d=get({'filter':f'primary_topic.id:{"|".join(ts[i:i+50])},{Y}{cf}','group_by':'authorships.institutions.country_code','per-page':'200'})
      for g in d['group_by']: cc[g['key'].split('/')[-1]]=cc.get(g['key'].split('/')[-1],0)+g['count']
    res[f'{tag}_country_{c}']=cc
json.dump(res,open('oa_shares.json','w'),indent=1)
print({k:(sum(v.values()) if isinstance(v,dict) else v) for k,v in res.items()})
