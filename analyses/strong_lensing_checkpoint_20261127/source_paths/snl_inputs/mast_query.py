import json, urllib.parse, urllib.request
params={'columns':'*','filters':[{'paramName':'proposal_id','values':['14210','10429','10710']},{'paramName':'obs_collection','values':['HST']}]}
q={'service':'Mast.Caom.Filtered','params':params,'format':'json','pagesize':300}
u='https://mast.stsci.edu/api/v0/invoke?'+urllib.parse.urlencode({'request':json.dumps(q)})
with urllib.request.urlopen(u,timeout=30) as f:d=json.load(f)
print(d.get('status'))
open('mast.json','w').write(json.dumps(d,indent=2))
for row in d.get('data',[]):print(*(row.get(k) for k in ('proposal_id','target_name','obs_id','filters','calib_level','obsid','dataURL')))
