"""Whole-patch coordinate holdout. Use unchanged affine fits and local-six support rule.
Patch = unique set of seed + two nearest cataloged reference knots; one fixed fit
for all three, six nearest to patch centroid vs all available. A patch gets a
precision prediction only when ALL three are inside that fit's input hull.
Require at least ten common landmarks so wide actually uses more than six.
"""
from pathlib import Path
import json
from itertools import combinations
import numpy as np
from scipy.spatial import ConvexHull
P=Path(__file__).resolve().parent
s={'__file__':str(P/'crystal_blocked_rule.py')}
exec((P/'crystal_blocked_rule.py').read_text().split('out={}\nfor name')[0],s)
def test(S):
 rows=[]
 for a,b in combinations(sorted(S),2):
  names=sorted(S[a].keys()&S[b].keys())
  if len(names)<10:continue
  for i,j in ((a,b),(b,a)):
   X,Y=[np.array([S[z][k] for k in names]) for z in (i,j)]
   dx=np.sum((X[:,None,:]-X[None,:,:])**2,axis=-1)
   np.fill_diagonal(dx,np.inf)
   patches={tuple(sorted([k,*seq[:2]])) for k,seq in enumerate(np.argsort(dx,axis=1,kind='stable'))}
   for p in sorted(patches):
    Q=X[list(p)]
    pool=np.array([k for k in range(len(X)) if k not in p])
    ids=pool[np.argsort(np.sum((X[pool]-Q.mean(0))**2,axis=1),kind='stable')]
    row=dict(direction=[i,j],patch=[names[k] for k in p],wide_n=int(len(ids)))
    assert len(ids)>6
    for label,t in [('local',ids[:6]),('wide',ids)]:
     q=ConvexHull(X[t]).equations
     mask=np.max(Q@q[:,:2].T+q[:,2],axis=1)<=1e-9
     pred=s['fit'](X[t],Y[t],Q)
     y=Y.copy();y[list(p)]+=1.e8
     np.testing.assert_array_equal(pred,s['fit'](X[t],y[t],Q))
     err=np.linalg.norm(pred-Y[list(p)],axis=1)
     row[label]=dict(inside=mask.tolist(),support=bool(mask.all()),error=err.tolist(),rms=float(np.sqrt(np.mean(err**2))),worst=float(err.max()),training=[names[k] for k in t])
    assert not row['local']['support'] or row['wide']['support']
    rows.append(row)
 def stat(label,cond):
  hit=[r[label] for r in rows if cond(r)]
  if not hit:return {'n':0}
  err=np.array([v['error'] for v in hit])
  return dict(n=len(hit),rms=float(np.sqrt(np.mean(err**2))),median=float(np.median(err)),worst=float(err.max()),all3_within_025=int(sum(err.max(1)<=.25)),all3_within_05=int(sum(err.max(1)<=.5)))
 stats={m:{'all':stat(m,lambda r:True),'both_supported':stat(m,lambda r:r['local']['support']),'own_supported':stat(m,lambda r:r[m]['support']),'wide_only':stat(m,lambda r:r['wide']['support'] and not r['local']['support'])} for m in ('local','wide')}
 use=np.array([(r["local"] if r["local"]["support"] else r["wide"])["error"] for r in rows if r["wide"]["support"]])
 stats["exploratory_router"]=dict(n=len(use),rms=float(np.sqrt(np.mean(use**2))),all3_within_05=int(sum(use.max(1)<=.5)),worst=float(use.max())) if len(use) else dict(n=0)
 return dict(stats=stats,wide_budget=sorted({r['wide_n'] for r in rows}),rows=rows)
out={k:test(v) for k,v in [('Sunburst',s['ns']['sets']),('Refsdal',s['ref'])]}
(P/'crystal_full_patch.json').write_text(json.dumps(out,indent=2)+'\n')
for k,v in out.items():
 print(k,v['wide_budget']);print(json.dumps(v['stats'],indent=2))
