"""Conditional retained close system + cluster, one interaction proxy.
NFW X-ray-calibrated gravity treated as an effective external field, not baryons.
Compute joint minus separate, subtract close-scale nonadditivity already present.
Local projected longitudinal solve checked for boundary dependence.
"""
import numpy as np
import json
import coupled_well_screen as s
from scipy.fft import rfft2,irfft2,fftfreq,rfftfreq
from scipy.ndimage import map_coordinates
from numpy.polynomial.legendre import leggauss
from pathlib import Path
P=Path(__file__).resolve().parent
p=(np.array([146.33333610581,10.08535044288])-s.radec[0])*3600*s.dk*[np.cos(np.deg2rad(s.radec[0,1])),1]
M,R,c=8.56e13,623.,3.
def evaluate(box,n,los,q,offset=0,sample=None):
 step=2*box/n
 g=np.arange(n)*step-box
 X,Y=np.meshgrid(g,g,indexing='ij',sparse=True)
 xy=[(X-v[0],Y-v[1]) for v in s.centers]
 xy4=(X-p[0],Y-p[1]);rr4=xy4[0]**2+xy4[1]**2
 r2=[x*x+y*y for x,y in xy]
 rs=R/c
 j=lambda x:np.log1p(x)-x/(1+x)
 u,w=leggauss(q)
 lim=np.arcsinh(los/5.)
 F=np.zeros((2,n,n))
 for uu,ww in zip(u,w):
  h=5*np.sinh(lim*uu); weight=ww*5*lim*np.cosh(lim*uu)
  v=[]
  for i,((x,y),t) in enumerate(zip(xy,r2)):
   r=np.maximum(np.sqrt(h*h+t),1e-10)
   m=s.G*s.mt(r,i)/r**3
   v.append([m*x,m*y,m*h])
  v=[sum(z[k] for z in v) for k in range(3)]
  dc=h-offset; r=np.sqrt(dc*dc+rr4)
  t=s.G*M*j(r/rs)/j(c)/r**3
  W=[t*xy4[0],t*xy4[1],t*dc]
  F+=weight*(s.response(*(a+b for a,b in zip(v,W)),s.aH)-s.response(*v,s.aH)-s.response(*W,s.aH))
 kx,ky=fftfreq(n)[:,None],rfftfreq(n)[None,:]
 den=kx*kx+ky*ky;den[0,0]=1
 pot=(kx*rfft2(F[0])+ky*rfft2(F[1]))/den
 fields=[irfft2(k*pot,s=(n,n))*2/(s.c*s.c*s.arad) for k in [kx,ky]]
 w0=1-s.chi(s.z)/s.chi(5.975)
 def alpha(a):
  return np.array([map_coordinates(f,((a*s.dk+box)/step).T,order=3) for f in fields]).T
 e=np.eye(2)*.2;J=(alpha(e)-alpha(-e)).T/.4
 a=alpha(s.A);v=a[0]-a[1]
 row=dict(box=box,n=n,los=los,q=q,assumed_depth_kpc=offset,raw_pair_mas=float(np.linalg.norm(v)*1000*w0),
          beyond_affine_mas=float(np.linalg.norm(v-J@(s.A[0]-s.A[1]))*1000*w0),matrix=J.tolist(),
          vector_mas=(v*1000*w0).tolist(),kappa=float(np.trace(J)*w0/2))
 if sample is not None: row["samples"]=[(alpha(t)-alpha(np.zeros((1,2)))).tolist() for t in sample]
 return row
if __name__=='__main__':
 out=[]
 for args in [(450,560,3600,100),(750,768,7200,124),(1100,928,12000,136),(750,768,7200,124,2500)]:
  r=evaluate(*args);out.append(r);print(r,flush=True)
  (P/'erosita_shared_well.json').write_text(json.dumps(out,indent=2)+'\n')
