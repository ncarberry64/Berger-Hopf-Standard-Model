"""Observed-input two-plane stellar-source calculation; no lens model fit or delays."""
import json, math
from functools import lru_cache
from pathlib import Path
import sys
import numpy as np
from scipy.integrate import quad
from scipy.special import gammainc, gammaincinv, gammaln
p=Path(__file__).resolve().parent
sys.path.insert(0,str(p/'pinned_extra'))
from r1_background_geometry import D,cfs,G,speed,L,xrad,bg

raw=json.loads((p/'he0435_courbin_astrometry.json').read_text())
positions={i['id']:np.array([i['delta_alpha'],i['delta_delta']]) for i in raw['astrometry']['data']}
theta_g=np.array([-2.585,-3.637])*xrad
names=('A','B','C','D')
z1,z2,zs=.4546,.7821,1.693
d1,d2,ds,d12,d1s,d2s = map(lambda q:D(*q),[(0,z1),(0,z2),(0,zs),(z1,z2),(z1,zs),(z2,zs)])
w1,w2=d1s/ds,d2s/ds
I=np.eye(2)

class Profile:
 def __init__(self,mass,scale,n,redshift):
  self.m=G*mass/speed**2
  self.a=scale/1000
  self.n=n
  self.bn=gammaincinv(2*n,.5) if n else None
  self.norm=gammaln(2*n+1) if n else None
  self.b,self.C,self.eps,_=cfs(redshift)
  self.rv=(16*self.b*self.m*L**2/(bg.LAMBDA*self.C**2))**(1/3)
 @lru_cache(maxsize=300000)
 def sphere(self,r):
  n=self.n
  if not n: return (r/math.hypot(r,1))**3,3/(1+r*r)
  y0=self.bn*r**(1/n)
  if y0>76:return 1.,0.
  def gam(y):return math.exp(2*n*math.log(y)-y-self.norm)
  def mp(t):
   y=y0+t*t; u=(y0/y)**n
   if u<1e-3:ker=4/(3*math.pi)*u**3*(1+.3*u*u+9/56*u**4)
   else:ker=2/math.pi*(math.asin(u)-u*math.sqrt(max(0,1-u*u)))
   return 2*t*gam(y)*ker
  def slope(t):
   y=y0+t*t;lu=-n*math.log1p(t*t/y0)
   if t==0:return 8/math.pi*gam(y0)*math.sqrt(y0/(2*n))
   return 8/math.pi*t*gam(y)*math.exp(3*lu)/math.sqrt(-math.expm1(2*lu))
  mu=gammainc(2*n+1,y0)+quad(mp,0,10,epsabs=1e-13)[0]
  return mu, quad(slope,0,10,epsabs=1e-13)[0]/mu
 @lru_cache(maxsize=8192)
 def cyl(self,R,r1):
  u=R/self.a
  if self.n:
   x=self.bn*u**(1/self.n)
   M=float(gammainc(2*self.n,x))
   Dlog=math.exp(2*self.n*math.log(x)-x-gammaln(2*self.n))/self.n
  else:
   M=u*u/(1+u*u)
   Dlog=2*M/(1+u*u)
  if r1:
   def f(t,i):
    x=u/math.cos(t)
    mu,n=self.sphere(x)
    S=math.sqrt(1+(self.rv/self.a)**3*mu/x**3)
    out=mu*(2*self.eps/(1+S))*math.cos(t)
    return out*(.5*((1+1/S)*n+3*(1-1/S)) if i else 1)
   q,t=[quad(lambda t:f(t,i),0,math.pi/2,epsabs=2e-13,epsrel=2e-9)[0] for i in [0,1]]
   M+=q;Dlog+=t
  return M,Dlog
 def apply(self,x,r1=False):
  R=float(np.linalg.norm(x))
  M,d=self.cyl(R,r1)
  rvec=x/R
  A=4*self.m*M/R
  H=(4*self.m/R**2)*(M*I+(d-2*M)*np.outer(rvec,rvec))
  return A*rvec,H

class Composite(Profile):
 def __init__(self,parts,redshift):
  self.parts=parts
  self.m=sum(part.m for part in parts)
  self.b,self.C,self.eps,_=cfs(redshift)
  self.rv=(16*self.b*self.m*L**2/(bg.LAMBDA*self.C**2))**(1/3)
 @lru_cache(maxsize=300000)
 def sphere_physical(self,r):
  pair=[(p.m/self.m,p.sphere(r/p.a)) for p in self.parts]
  return tuple(sum(w*m*(l if i else 1) for w,(m,l) in pair) for i in [0,1])
 @lru_cache(maxsize=8192)
 def cyl(self,R,r1):
  bare=tuple(sum(p.m/self.m*p.cyl(R,False)[i] for p in self.parts) for i in [0,1])
  if not r1:return bare
  def f(t,i):
   r=R/math.cos(t)
   mu,dmu=self.sphere_physical(r); n=dmu/mu
   S=math.sqrt(1+(self.rv/r)**3*mu)
   val=mu*(2*self.eps/(1+S))*math.cos(t)
   return val*(.5*((1+1/S)*n+3*(1-1/S)) if i else 1)
  return tuple(a+quad(lambda t:f(t,i),0,math.pi/2,epsabs=2e-13,epsrel=2e-9)[0] for i,a in enumerate(bare))


def build(main,comp,on1=False,on2=False):
 # Observed companion light centroid is lensed by first plane, too.
 alpha_g,_=main.apply(d1*theta_g,on1)
 c2=d2*theta_g-d12*alpha_g
 def ray(theta):
  a1,H1=main.apply(d1*theta,on1)
  x2=d2*theta-d12*a1-c2
  if comp is None: a2,H2=np.zeros(2),np.zeros((2,2))
  else:a2,H2=comp.apply(x2,on2)
  beta=theta-w1*a1-w2*a2
  J=I-w1*d1*H1-w2*H2@(d2*I-d12*d1*H1)
  return beta,J,np.linalg.norm(x2),(w1*a1,w2*a2)
 return ray

def run(main,comp,on1,on2,base=None):
 ray=build(main,comp,on1,on2)
 b=[]
 arr=[]
 for name in names:
  t=(positions[name]-positions['G'])*xrad
  y,J,imp,a=ray(t)
  h=.0001*xrad
  Jfd=np.stack([(ray(t+h*e)[0]-ray(t-h*e)[0])/(2*h) for e in I],axis=1)
  assert np.max(abs(J-Jfd))<3.e-7
  b.append(y/xrad)
  arr.append(dict(image=name,source_arcsec=(y/xrad).tolist(), total_convergence=float(1-np.trace(J)/2),rotation=float((J[0,1]-J[1,0])/2),signed_jacobian_det=float(np.linalg.det(J)), G1_impact_kpc=1000*imp, main_reduced_deflection_arcsec=float(np.linalg.norm(a[0])/xrad), G1_reduced_deflection_arcsec=float(np.linalg.norm(a[1])/xrad), jacobian_fd_error=float(np.max(abs(J-Jfd)))))
 b=np.array(b)
 sep=float(np.max(np.linalg.norm(b[:,None]-b,axis=2)))
 result=dict(rays=arr, common_source_RMS_arcsec=float(np.sqrt(np.mean(np.sum((b-b.mean(axis=0))**2,axis=1)))), max_source_disagreement_arcsec=sep)
 if base:
  b0=np.array([q['source_arcsec'] for q in base['rays']])
  delta=b-b0
  result.update(max_source_shift_arcsec=float(np.max(np.linalg.norm(delta,axis=1))),max_pairwise_differential_source_shift_arcsec=float(np.max(np.linalg.norm(delta[:,None]-delta,axis=2))))
 return result

# Main: independent Zahedy+ photometric shape and stellar mass (spherical proxy at declared catalog effective scale).
q_main=.82
Re_major=4.4
Re_circular=Re_major*math.sqrt(q_main)
m=Profile(10**11.1,Re_circular,3.51,z1)
noG=run(m,None,False,False)
runs={}
for a in [.2,2.,5.]:
 # Companion mass from Wong et al. independently estimated as stellar mass.
 # No admitted size measured; predeclared shape/scale variants, not training.
 g=Profile(10**10.9,a,None,z2)
 bare=run(m,g,False,False,noG)
 r1=run(m,g,True,True,bare)
 runs[str(a)]=dict(stars_only_GR=bare,stars_plus_baryon_sourced_R1=r1)
wbulge=1/(1+10**(-.4*(18.8-18.7)))
rear_bulge_Re=.37*xrad*d2*1000
rear_disk_Re=(1.67834699*.67)*xrad*d2*1000
g_photo=Composite([Profile(wbulge*10**10.9,rear_bulge_Re,4.,z2),
                  Profile((1-wbulge)*10**10.9,rear_disk_Re,1.,z2)],z2)
bare_photo=run(m,g_photo,False,False,noG)
r1_photo=run(m,g_photo,True,True,bare_photo)

out=dict(scope='Conditional stars-only actual-target control; no masses, source position, delays, shear or halo fitted. Main circular. Independent G1 bulge+disk photometry circled as primary, with common H-band M/L, plus Plummer sensitivity variants; independent R1 quasi-static response on each well-separated redshift plane, with coupled ordered ray tracing; not joint cosmological nonlinear matter evolution or a BHSM environment-law prediction.',redshifts=[z1,z2,zs],distances_Mpc=[d1,d2,ds,d12,d1s,d2s],source_comparison='Back-project observed positions only; common-source RMS is diagnostic equivalent to best constant centering, not a forward fitted quasar source.',main_Msun=10**11.1,main_n=3.51,main_Re_major_kpc=Re_major,main_q=q_main,main_Re_circularized_kpc=Re_circular,G1_stellar_Msun=10**10.9,G1_offsets_arcsec=(theta_g/xrad).tolist(),main_eps=m.eps,G1_eps=g.eps,main_no_G1=noG,G1_photometric_bulge_disk=dict(bulge_fraction=wbulge,bulge_Re_kpc=rear_bulge_Re,disk_Re_kpc=rear_disk_Re,stars_only_GR=bare_photo,stars_plus_baryon_sourced_R1=r1_photo),G1_plummer_kpc=runs)
(p/'he0435_joint_field_control.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(dist=[d1,d2,ds,d12,d1s,d2s],none=noG['common_source_RMS_arcsec'],checks={k:(v['stars_only_GR']['common_source_RMS_arcsec'],v['stars_only_GR']['max_pairwise_differential_source_shift_arcsec'],v['stars_plus_baryon_sourced_R1']['common_source_RMS_arcsec'],v['stars_plus_baryon_sourced_R1']['max_pairwise_differential_source_shift_arcsec']) for k,v in runs.items()}),indent=2))
