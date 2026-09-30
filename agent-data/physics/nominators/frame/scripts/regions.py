EU=set('AT BE BG HR CY CZ DK EE FI FR DE GR HU IE IT LV LT LU MT NL PL PT RO SK SI ES SE GB CH NO IS UA RS BA ME MK AL BY MD LI'.split())
def region(cc):
  if cc in ('US',):return 'USA'
  if cc=='CA':return 'Canada'
  if cc=='CN':return 'China'
  if cc=='JP':return 'Japan'
  if cc in ('KR','TW','SG','HK','MO'):return 'Other East Asia (KR,TW,SG,HK)'
  if cc=='IN':return 'India'
  if cc=='RU':return 'Russia'
  if cc in ('SE','DK','FI','NO','IS'):return 'Nordic'
  if cc in EU:return 'Europe (non-Nordic)'
  if cc in ('AU','NZ'):return 'Oceania'
  if cc in ('BR','MX','AR','CL','CO','PE','VE','UY','CU','EC','BO','CR','PR','PY'):return 'Latin America'
  if cc in ('IL','TR','IR','SA','AE','QA','EG','JO','LB','IQ','PK','KW','OM','BH'):return 'Middle East/Turkey/Iran/Pakistan'
  if cc in ('unknown',None,''):return None
  return 'Rest of world'
ORDER=['USA','Canada','Europe (non-Nordic)','Nordic','China','Japan','Other East Asia (KR,TW,SG,HK)','India','Russia','Middle East/Turkey/Iran/Pakistan','Latin America','Oceania','Rest of world']
