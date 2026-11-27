"""Inputs-to-equivalent-output audit for light-only positional geometry."""
from pathlib import Path
from itertools import combinations
import json,numpy as np
P=Path(__file__).resolve().parent
ns={'__file__':__file__}
exec((P/'sunburst_crystal_transfer.py').read_text().split('res=[]')[0],ns)
sun=ns['sets']
hh=json.loads((P/'hamilton_landmark_holdout.json').read_text())['marker_pixels']
ham={i:{j+1:v*np.array([1/67,-2.2/67]) for j,v in enumerate(np.array(t))} for i,t in hh.items()}
def aff(X,Y,x):
 u=X.mean(0); v=Y.mean(0)
 return (x-u)@np.linalg.lstsq(X-u,Y-v,rcond=None)[0]+v
def bary(X,Y,x):
 # Source triangle coordinates from light alone; transport the same
 # weights to target triangle; no fitted target profile or anisotropy prior.
 basis=X[1:]-X[0]
 w=np.linalg.solve(basis.T,x-X[0]);w=np.r_[1-w.sum(),w]
 return w@Y,w
def area(t):
 a,b=t[1:]-t[0]
 return abs(a[0]*b[1]-a[1]*b[0])
def run(s):
 rows=[]
 for a,b in combinations(s,2):
  f=sorted(s[a].keys()&s[b].keys())
  if len(f)<7:continue
  for l,r in ((a,b),(b,a)):
   X,Y=(np.array([s[k][i] for i in f]) for k in [l,r])
   for j,x in enumerate(X):
    ids=np.argsort(np.sum((X-x)**2,axis=1),kind='stable')
    ids=ids[ids!=j][:6]
    assert j not in ids
    near=ids[:3]
    # Compare best-spread vs nearest. The rule never reads target positions.
    tri=np.array(max(combinations(ids,3),key=lambda c:area(X[list(c)])))
    p,w=bary(X[tri],Y[tri],x)
    q,_=bary(X[near],Y[near],x)
    equiv=float(np.linalg.norm(p-aff(X[tri],Y[tri],x)))
    assert equiv<1e-7
    fits={'tri_spread3':p,'tri_nearest3':q,'affine4':aff(X[ids[:4]],Y[ids[:4]],x),'affine5':aff(X[ids[:5]],Y[ids[:5]],x),'affine6':aff(X[ids],Y[ids],x)}
    rows.append(dict(pair=[l,r],withheld=f[j],inputs=[f[i] for i in ids],triangle=[f[i] for i in tri],
        inside=bool(np.all(w>=-1e-8)),equivalence=equiv,errors={k:float(np.linalg.norm(v-Y[j])) for k,v in fits.items()}))
 def metrics(r):
  return {k:[float(np.sqrt(np.mean([v['errors'][k]**2 for v in r]))),float(np.median([v['errors'][k] for v in r]))] for k in r[0]['errors']}
 return dict(n=len(rows),inside=sum(v['inside'] for v in rows),maximum_same_triangle_difference=max(r['equivalence'] for r in rows),
  rms_median=metrics(rows),inside_rms_median=metrics([v for v in rows if v['inside']]),outside_rms_median=metrics([v for v in rows if not v['inside']]),rows=rows)
out={k:run(z) for k,z in [('Sunburst',sun),('Hamilton',ham)]}
(P/'crystal_landmark_budget.json').write_text(json.dumps(out,indent=2)+'\n')
for k,r in out.items(): print(k,{k:v for k,v in r.items() if k!='rows'})
