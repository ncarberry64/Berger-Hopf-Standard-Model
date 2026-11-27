"""Paired ablation: enlarge training set with one target always held out."""
from pathlib import Path
from itertools import combinations
import json,numpy as np
P=Path(__file__).resolve().parent
ns={'__file__':__file__}
exec((P/'crystal_hybrid_v2.py').read_text().split('out={k:test')[0],ns)
rows=[]
for a,b in combinations(sorted(ns['s']),2):
 s=ns['s']; f=sorted(s[a].keys()&s[b].keys())
 if len(f)<8:continue # require a genuine increase in every scored query
 for i,j in [(a,b),(b,a)]:
  X,Y=[np.array([s[k][t] for t in f]) for k in (i,j)]
  for k,x in enumerate(X):
   inds=np.argsort(np.sum((X-x)**2,axis=1),kind='stable')
   inds=inds[inds!=k]; assert k not in inds
   vals={}
   for n in range(6,len(inds)+1):
    ix=inds[:n]; _,p=ns['predict'](X[ix],Y[ix],x)
    vals[n]=dict(zip(['uniform','affine','hybrid'],np.linalg.norm(p-Y[k],axis=1).tolist()))
   rows.append(dict(pair=[i,j],knot=f[k],n=len(inds),errors=vals))
def summary(rr,nn,m):
 v=np.array([r['errors'][nn(r)][m] for r in rr]);return [float(np.sqrt(np.mean(v*v))),float(np.median(v)),float(v.max())]
modes=['uniform','affine','hybrid']
scores={str(n):dict(count=len(rr), rms_median_max={m:summary(rr,lambda r:n,m) for m in modes},
                 baseline6={m:summary(rr,lambda r:6,m) for m in modes}) for n in range(7,max(r['n'] for r in rows)+1) if (rr:=[r for r in rows if r['n']>=n])}
allres={m:summary(rows,lambda r:r['n'],m) for m in modes}
six={m:summary(rows,lambda r:6,m) for m in modes}
by={}
for a,b in sorted({tuple(sorted(r['pair'])) for r in rows}):
 rr=[r for r in rows if set(r['pair'])=={a,b}]
 by[f'{a}-{b}']={m:[summary(rr,lambda r:6,m)[0],summary(rr,lambda r:r['n'],m)[0]] for m in modes}
out=dict(n=len(rows),six=six,all=allres,by_pair=by,by_budget=scores,rows=rows)
(P/'crystal_more_landmarks.json').write_text(json.dumps(out,indent=2)+'\n')
print({k:v for k,v in out.items() if k not in ('rows','by_budget')})
print('same subset max budget',scores[str(max(r['n'] for r in rows))])
