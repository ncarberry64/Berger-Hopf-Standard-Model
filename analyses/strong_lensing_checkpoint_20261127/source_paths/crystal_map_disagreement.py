"""Test whether local-vs-wide model spread warns of a withheld-image error."""
from pathlib import Path
from itertools import combinations
import json,numpy as np
from scipy.stats import spearmanr
P=Path(__file__).resolve().parent
ns={'__file__':__file__}
exec((P/'crystal_hybrid_v2.py').read_text().split('out={k:test')[0],ns)
s=ns['s']; rows=[]
for a,b in combinations(sorted(s),2):
 f=sorted(s[a].keys()&s[b].keys())
 if len(f)<8:continue
 for i,j in [(a,b),(b,a)]:
  X,Y=[np.array([s[k][t] for t in f]) for k in (i,j)]
  for k,x in enumerate(X):
   ids=np.argsort(np.sum((X-x)**2,axis=1),kind='stable')
   ids=ids[ids!=k]
   def fit(ids):return ns['predict'](X[ids],Y[ids],x)[1][1:] # affine, hybrid
   p=fit(ids[:6]); q=fit(ids)
   rows.append(dict(pair=[a,b],direction=[i,j],query=f[k],
       spread=np.linalg.norm(p-q,axis=1).tolist(),
       midpoint_error=np.linalg.norm((p+q)/2-Y[k],axis=1).tolist(),
       nearest_error=np.linalg.norm(p-Y[k],axis=1).tolist(),
       wide_error=np.linalg.norm(q-Y[k],axis=1).tolist()))
summary={}
for m,label in enumerate(('affine','hybrid')):
 x=np.array([r['spread'][m] for r in rows]);y=np.array([r['midpoint_error'][m] for r in rows])
 def stats(f):
  return dict(n=sum(f).item(),med=float(np.median(y[f])) if np.any(f) else None,err_over_half=sum(y[f]>=.5).item())
 summary[label]=dict(correlation=float(spearmanr(x,y).statistic),
  thresholds={str(t):{'flagged':stats(x>=t),'unflagged':stats(x<t)} for t in (.1,.25,.5)},
  leave_pair_out_correlations={},
  biggest_unflagged=max((r for r in rows if r['spread'][m]<.25),key=lambda r:r['midpoint_error'][m]),
  error_outside_midpoint_radius_half_spread=int(np.count_nonzero(y>x/2)))
 for p in sorted({tuple(r['pair']) for r in rows}):
  keep=np.array([tuple(r['pair'])!=p for r in rows])
  summary[label]['leave_pair_out_correlations'][str(p)]=float(spearmanr(x[keep],y[keep]).statistic)
assert len(rows)==94
(P/'crystal_map_disagreement.json').write_text(json.dumps(dict(summary=summary,rows=rows),indent=2)+'\n')
print(json.dumps(summary,indent=2))
