"""Table 1: https://arxiv.org/html/2411.07289#S3. No foreground inputs."""
import numpy as np, json
from scipy.integrate import quad
from scipy.linalg import helmert
from scipy.optimize import root, linear_sum_assignment
from scipy.spatial.distance import cdist
x=dict(A=[[49.71,25.50],[49.36,33.05],[48.78,32.06],[49.03,23.85]],
 B=[[49.69,24.74],[49.33,32.89],[48.76,31.40],[48.99,23.75]],
 C=[[49.84,24.98],[49.04,27.38]],E=[[49.87,25.27],[49.63,33.69],[48.50,34.15],[49.03,21.41]],
 F=[[49.85,22.15],[49.46,34.43],[48.50,32.52],[48.88,21.55]])
Z=dict(A=1.88,B=1.88,C=1.698,E=4.95,F=4.95)
xy={k:(np.array(v)-[49.0,28.])*[15*np.cos(np.deg2rad(18+18/60+30/3600)),1.] for k,v in x.items()}
X=np.concatenate([xy[k] for k in 'ABC'])
def chis(z): return quad(lambda u:1/np.sqrt(.3*(1+u)**3+.7),0,z)[0]
def w(k,z):
 return 1. if not z else (1-chis(z)/chis(Z[k]))/(1-chis(z)/chis(Z['A']))
def run(width,z):
 ws={k:w(k,z) for k in Z}
 def basis(q):
  d=np.atleast_2d(q)[:,None,:]-X
  return np.moveaxis(d/width*np.exp(-.5*np.sum(d*d,axis=2)/width**2)[:,:,None],1,2)
 m=np.concatenate([(ws[k]*np.einsum('ij,jab->iab',helmert(len(xy[k])),basis(xy[k]))).reshape(-1,len(X)) for k in 'ABC'])
 t=np.concatenate([(helmert(len(xy[k]))@xy[k]).ravel() for k in 'ABC'])
 reg=.02
 c=np.linalg.solve(m.T@m+reg**2*np.eye(len(X)),m.T@t)
 ans={}
 for k in 'EF':
  def mp(q): return np.atleast_2d(q)-ws[k]*(basis(q)@c)
  anchor=mp(xy[k][0])[0]
  def g(q): return mp(q)[0]-anchor
  roots=[]
  for ii in np.linspace(-19,19,35):
   for jj in np.linspace(-17,17,31):
    p=root(g,[ii,jj]); v=p.x
    if p.success and np.linalg.norm(g(v))<1e-7 and max(abs(v))<25 and all(np.linalg.norm(v-u)>1e-4 for u in roots):
     roots.append(v)
  rr=[v for v in roots if np.linalg.norm(v-xy[k][0])>1e-4]
  matches={}
  if rr:
   d=cdist(xy[k][1:],rr); i,j=linear_sum_assignment(d)
   matches={str(int(a+2)):float(d[a,b]) for a,b in zip(i,j)}
  ans[k]=dict(roots=len(roots),matches=matches,source_plane_closure=np.linalg.norm(mp(xy[k][1:])-anchor,axis=1).tolist())
 return {'width':width,'screen_redshift':z,'dev_RMS':float(np.sqrt(np.mean((m@c-t)**2))),**ans}
if __name__=='__main__':
 out=[run(s,z) for z in [0.,.3,.6,.9] for s in [3.,6.,12.]]
 print(json.dumps(out,indent=2))
