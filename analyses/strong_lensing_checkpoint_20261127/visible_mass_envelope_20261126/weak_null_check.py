"""Gavazzi published bins, mask and compensated control; no covariance supplied."""
import json,numpy as np
from pathlib import Path
src=json.load(open('joint_reach.json'))
r,y,s=np.array(src['table2']).T
cross=np.array([-1015,-526,141,-180,-36,36,-45,52,34],float)
C=np.diag(s*s); anchor=4
out={}
for L in [.88,2,3,5,10,20,50,1e9]:
 out[str(L)]=[]
 p=src['results'][str(L)]['weak']
 for k in (0,1,2):
  a=np.array(p[k]['y'])
  h={}
  for key,i in [('full',[4,5,6,7]),('minus235',[4,5,6]),('with_farthest',[4,5,6,7,8]),('lose_94',[4,5,7]),('lose_54',[4,6,7]),('lose_31',[5,6,7])]:
   q=np.array(i)
   stat=lambda v: v@np.linalg.solve(C[np.ix_(q,q)],v)
   h[key]=[float(stat(v[q])) for v in [y-a,cross]]
  for key,i in [('full_ups',[5,6,7]),('minus235_ups',[5,6]),('with_farthest_ups',[5,6,7,8])]:
   B=np.eye(len(r))[i]; B[:,anchor]-=(r[anchor]/r[i])**2
   cov=B@C@B.T
   stat=lambda v:float((B@v)@np.linalg.solve(cov,B@v))
   h[key]=[stat(v) for v in [y-a,cross]]
  out[str(L)].append(h)
 print(L,{k:np.round(v,3).tolist() for k,v in out[str(L)][0].items()})
Path('weak_null_check.json').write_text(json.dumps(out,indent=2)+'\n')
