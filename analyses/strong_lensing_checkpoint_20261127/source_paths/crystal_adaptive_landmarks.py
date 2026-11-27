"""Nested landmark budget choice. No target location in either model selection or training."""
from pathlib import Path
from itertools import combinations
import json,numpy as np
P=Path(__file__).resolve().parent
ns={'__file__':__file__}
exec((P/'crystal_hybrid_v2.py').read_text().split('out={k:test')[0],ns)
s=ns['s']
def nearest(X,x,n):
 return np.argsort(np.sum((X-x)**2,axis=1),kind='stable')[:n]
def both(X,Y,x,n):
 k=nearest(X,x,n)
 return ns['predict'](X[k],Y[k],x)[1][1:] # affine and hybrid
def select(X,Y,x):
 # Score both budgets on identical inner targets. Remove one K from both
 # candidate counts to retain the gap: five nearest vs all remaining.
 N=len(X); loss=np.zeros((2,2))
 for i,j in enumerate(X):
  z=np.arange(N)!=i
  for k,b in enumerate([5,N-1]):
   p=both(X[z],Y[z],j,b)
   loss[k]+=np.sum((p-Y[i])**2,axis=1)
 # Ties go to fewer matches.
 choice=(loss[1]<loss[0]).astype(int)
 a=np.array([both(X,Y,x,k) for k in [6,N]])
 return a,choice,loss
rows=[]
for a,b in combinations(sorted(s),2):
 f=sorted(s[a].keys()&s[b].keys())
 if len(f)<8:continue
 for i,j in [(a,b),(b,a)]:
  X,Y=[np.array([s[k][t] for t in f]) for k in (i,j)]
  for k,x in enumerate(X):
   ids=np.arange(len(X))!=k
   p,c,l=select(X[ids],Y[ids],x)
   # Counterfactual: change the target position after selecting; predictions
   # are identical because the held target isn't used to build scores.
   Yf=Y.copy();Yf[k]+=100
   pp,cc,ll=select(X[ids],Yf[ids],x)
   assert np.array_equal(p,pp) and np.array_equal(c,cc) and np.array_equal(l,ll)
   e=np.linalg.norm(p-Y[k],axis=-1)
   rows.append(dict(pair=[i,j],query=f[k],train=[f[ix] for ix in np.where(ids)[0]],error=e.tolist(),wider=c.tolist(),choice_loss=l.tolist()))
def score(rows):
 e=np.array([r['error'] for r in rows]); k=np.array([r['wider'] for r in rows])
 z=e[np.arange(len(e))[:,None],k,np.arange(2)]
 metrics=lambda z:[np.sqrt(np.mean(z*z,axis=0)).tolist(),np.median(z,axis=0).tolist(),np.max(z,axis=0).tolist()]
 return dict(count=len(e),larger=k.sum(axis=0).tolist(),six=metrics(e[:,0]),all=metrics(e[:,1]),adaptive=metrics(z))
report=score(rows)
baseline=json.loads((P/'crystal_more_landmarks.json').read_text())
for j,name in enumerate(['affine','hybrid']):
 for m in ('six','all'):
  assert abs(report[m][0][j]-baseline[m][name][0])<1e-12
by={f'{a}-{b}':score([r for r in rows if set(r['pair'])=={a,b}]) for a,b in sorted({tuple(sorted(r['pair'])) for r in rows})}
(P/'crystal_adaptive_landmarks.json').write_text(json.dumps(dict(report=report,pairs=by,rows=rows),indent=2)+'\n')
print(report)
for k,v in by.items():print(k,'wide',v['larger'],'rms six/all/adaptive',[v[key][0] for key in ['six','all','adaptive']])
