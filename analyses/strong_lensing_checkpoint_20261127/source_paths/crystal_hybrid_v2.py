"""Training-only hybrid of scaled orientation (mirror allowed) and affine light maps."""
from pathlib import Path
from itertools import combinations
import json,numpy as np
P=Path(__file__).resolve().parent
src=(P/'sunburst_crystal_transfer.py').read_text().split('res=[]')[0]
ns={'__file__':__file__}
exec(src,ns)
s=ns['sets']
hamdata=json.loads((P/'hamilton_landmark_holdout.json').read_text())['marker_pixels']
h={i:{j+1:v*np.array([1/67,-2.2/67]) for j,v in enumerate(np.array(t))} for i,t in hamdata.items()}
def pred(X,Y,x):
 a=X-X.mean(0); b=Y-Y.mean(0)
 J=np.linalg.lstsq(a,b,rcond=None)[0]
 u,d,v=np.linalg.svd(a.T@b)
 R=np.diag([1,np.sign(np.linalg.det(J))*np.linalg.det(u@v)])
 T=u@R@v*(d@R.diagonal())/np.sum(a*a)
 return np.stack([(x-X.mean(0))@M+Y.mean(0) for M in (T,J)])
def predict(X,Y,x):
 # For this outer target, select weight ONLY within the six training matches.
 # Inner CV predicts each of the six using the other five.
 Z=np.array([pred(np.delete(X,j,0),np.delete(Y,j,0),xj) for j,xj in enumerate(X)])
 d=Z[:,1]-Z[:,0]
 weight=float(np.clip(np.sum(d*(Y-Z[:,0]))/max(np.sum(d*d),1e-30),0,1))
 p,q=pred(X,Y,x)
 return weight,np.stack([p,q,p+weight*(q-p)])
def test(s):
 q=[]
 keys=['similarity','affine','hybrid']
 for a,b in combinations(s,2):
  f=sorted(s[a].keys()&s[b].keys())
  if len(f)<7:continue
  for l,r in ((a,b),(b,a)):
   X,Y=(np.array([s[k][i] for i in f]) for k in (l,r))
   for j,x in enumerate(X):
    ids=np.argsort(np.sum((X-x)**2,axis=1),kind='stable')
    ids=ids[ids!=j][:6]
    assert len(ids)==6 and j not in ids
    w,p=predict(X[ids],Y[ids],x)
    q.append(dict(copy=[l,r],query=f[j],training=[f[i] for i in ids],affine_weight=w,errors=dict(zip(keys,np.linalg.norm(p-Y[j],axis=1).tolist()))))
 arr=np.array([[r['errors'][n] for n in keys] for r in q])
 return dict(n=len(q),weights=np.percentile([r['affine_weight'] for r in q],[0,25,50,75,100]).tolist(),rms=dict(zip(keys,np.sqrt(np.mean(arr**2,axis=0)).tolist())),median=dict(zip(keys,np.median(arr,axis=0).tolist())),queries=q)
out={k:test(v) for k,v in (('Sunburst',s),('Hamilton',h))}
(P/'crystal_hybrid_v2.json').write_text(json.dumps(out,indent=2)+'\n')
for k,v in out.items():print(k,{k:a for k,a in v.items() if k!='queries'})
