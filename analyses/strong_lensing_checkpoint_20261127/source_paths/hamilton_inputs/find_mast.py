import json,urllib.parse,urllib.request
q={'service':'Mast.Caom.Cone','params':{'ra':337.5404,'dec':-8.1611,'radius':.025},'format':'json','pagesize':500}
u='https://mast.stsci.edu/api/v0/invoke?'+urllib.parse.urlencode({'request':json.dumps(q)})
with urllib.request.urlopen(u,timeout=20) as f:d=json.load(f)
open('mast.json','w').write(json.dumps(d,indent=2))
for r in d['data']:
 if r['obs_collection']=='HST' and r['calib_level']==3 and r['dataproduct_type']=='image':
  print(r['filters'],r['t_exptime'],r['proposal_id'],r['dataURL'])
