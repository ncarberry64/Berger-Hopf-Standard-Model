"""Matched held-out A/B comparison, fixed X-ray cluster mass. Affine joint proxy."""
import json
import numpy as np
from scipy.optimize import least_squares
import inner_rings_shared_well as u
from pathlib import Path
import erosita_shared_well as ec
p=Path(__file__).resolve().parent
zc=.2183
def w(a,b):return 1-u.cw.chi(a)/u.cw.chi(b)
W={(a,b):w(a,b) for a in [zc,u.z0,u.z1,u.z2] for b in [u.z0,u.z1,u.z2,u.z3] if a<b}
Ds={a:u.cw.chi(a)*1000/(1+a) for a in [zc,u.z0]}
pc=ec.p/u.dk
def Ext(t,z):
 v=t-pc
 r=np.linalg.norm(v,axis=-1)
 x=r*Ds[z]*u.asc/(ec.R/ec.c)
 j=np.log(x/2)+np.arccos(1/x)/np.sqrt(x*x-1)
 return (4*u.cw.G*ec.M/(u.cw.c**2*Ds[z]*u.asc**2)/(np.log1p(ec.c)-ec.c/(1+ec.c))*j/r**2)[:,None]*v
split=[3,5,8]
def fn(arm,J=np.zeros((2,2))):
 T=[np.vstack(u.observed[:4]),u.observed[4],u.pair]
 C=[Ext(t,zc)-Ext(np.zeros((1,2)),zc) if arm=='separate' else 0*t for t in T]
 tmain=[t-W[zc,u.z0]*q for t,q in zip(T,C)]
 B=[u.basic(t)+u.get_exact(t)-u.exact_origin for t in tmain]
 if arm in ('coplanar','coupled','sampled'):
  B=[v+Ext(t,u.z0)-Ext(np.zeros((1,2)),u.z0)+(J[i] if arm=='sampled' else t@J.T) for i,(t,v) in enumerate(zip(tmain,B))]
 n=[np.linalg.norm(t,axis=1)[:,None] for t in tmain]
 def model(params,s2=0,report=False):
  a,s,g1,g2,b=params
  S=np.array([[g1,g2],[g2,-g1]])
  U=[v+a*(r/1.43)**s*t/r+t@S.T for v,t,r in zip(B,tmain,n)]
  def at(i,z):return T[i]-W[zc,z]*C[i]-W[u.z0,z]*U[i]
  t1=np.split(at(0,u.z1),split)
  q1=np.mean([t.mean(axis=0) for t in t1],axis=0)
  def sis(t,q):d=t-q;return d/np.maximum(1e-12,np.linalg.norm(d,axis=1)[:,None])
  def trace(i,z):return at(i,z)-W[u.z1,z]*b*sis(at(i,u.z1),q1)
  t2=trace(1,u.z2)
  train=np.concatenate([(t-t.mean(axis=0)).ravel() for t in t1+[t2]])
  if not report:return train
  p3=trace(2,u.z3)
  if report=="rays":return p3,trace(2,u.z2)-t2.mean(axis=0)
  if s2:p3-=W[u.z2,u.z3]*4*np.pi*(s2/u.cw.c)**2/u.asc*sis(trace(2,u.z2),t2.mean(axis=0))
  return p3[0]-p3[1]
 return model
def fit(f,seeds):
 return min((least_squares(f,x,bounds=(u.lo,u.hi),ftol=1e-11,xtol=1e-11,gtol=1e-11,max_nfev=250) for x in seeds),key=lambda f:f.cost)
if __name__=='__main__':
 base=fit(fn('none'),u.starts); rows={}
 arms=[('none',np.zeros((2,2))),('separate',np.zeros((2,2))),('coplanar',np.zeros((2,2)))]
 jpath=p/'erosita_shared_well.json'
 if jpath.exists():
  for i,r in enumerate(json.loads(jpath.read_text())):
   arms.append((f'coupled_{i}',np.array(r['matrix'])))
 nodes=p/'erosita_shared_nodes.json'
 if nodes.exists():arms.append(('sampled',[np.array(v) for v in json.loads(nodes.read_text())['samples']]))
 for tag,H in arms:
  f=fn(tag.split('_')[0],H);a=fit(f,[base.x]+u.starts[:2])
  row=dict(inner_rms_mas=float(np.linalg.norm(a.fun)*1000/np.sqrt(14)),outer={},p=a.x.tolist())
  for v in [0,150]:
   diff=f(a.x,v,True)*1000
   row['outer'][str(v)]=dict(norm_mas=float(np.linalg.norm(diff)),vector_mas=diff.tolist(),
    from_base_vec_mas=float(np.linalg.norm(diff-fn('none')(base.x,v,True)*1000)))
  rows[tag]=row;print(tag,row)
 (p/'erosita_matched_planes.json').write_text(json.dumps(rows,indent=2)+'\n')
