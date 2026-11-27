"""Conditional minimum-energy common-field pin solver; no S3 calibration."""
import sys,json
from pathlib import Path
import numpy as np
from scipy.special import k0,k1
from scipy.optimize import brentq,least_squares,root
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'visible_mass_envelope_20261126/external_weak/jackpot_neighbor'))
import jackpot_current_geometry_holdout as geo
ep,u=geo.ep,geo.u
ep.W=geo.Ws['closed_R1']
u.get_exact=lambda t:np.zeros_like(t)
u.exact_origin=np.zeros((1,2))
basic=u.basic; pair=u.pair.copy()
ap=json.loads((P/'jackpot_equilibrium_calibration.json').read_text())
r0,r1=ap['apertures_arcsec']; dk=ap['apertures_kpc'][0]/r0
M0,M1=ap['total_projected_Msun']; Mh=1.6e9
a,b=u.scale.T
mstar=u.stars/(b-a)
def stars(r):
 r=np.asarray(r)[...,None]
 return (mstar*(np.hypot(r,a)-a-np.hypot(r,b)+b)).sum(axis=-1)
def F(x):
 with np.errstate(invalid='ignore'):return np.where(x==0,0.,1-x*k1(x))
B=np.array([M0,M1])-stars([r0,r1])-Mh
base=ep.fit(ep.fn('none'),u.starts).x
w=ep.W[u.z0,u.z1]
phi=np.arange(256)*2*np.pi/256
unit=np.stack([np.cos(phi),np.sin(phi)],axis=1)
def values(positions,ell,mode):
 d=np.linalg.norm(positions[:,None]-positions[None,:],axis=2)
 K=np.divide(-np.expm1(-d/ell),d,out=np.full_like(d,1/ell),where=d>0)
 assert np.linalg.eigvalsh(K).min()>0
 target=np.ones(len(positions))
 q=np.linalg.solve(K,target) if mode=='joint' else ell*target
 assert np.all(q>0)
 return K,q
def field(t,positions,ell,q):
 r=t[:,None,:]-positions[None,:,:2]
 norm=np.linalg.norm(r,axis=2)
 return ((F(norm/ell)*q/np.maximum(norm,1e-12)**2)[:,:,None]*r).sum(axis=1)
def project(positions,ell,q,rlist):
 return np.array([r*np.mean(np.sum(unit*field(r*unit,positions,ell,q),axis=1)) for r in rlist])
def replay(positions,ell,q):
 def build():
  u.basic=lambda t:basic(t)+u.A0*field(t,positions,ell,q)
  try:return ep.fn('none')
  finally:u.basic=basic
 f=build()
 xx=min((least_squares(lambda x:f(np.r_[0,0,x]),seed,bounds=(u.lo[2:],u.hi[2:]),ftol=1e-11,xtol=1e-11,gtol=1e-11) for seed in [base[2:],[.08,.08,.30],[0,0,.05]]),key=lambda o:o.cost)
 x=np.r_[0,0,xx.x]
 def resid(p):
  u.pair=np.vstack([pair[0],p])
  try:return build()(x,0,True)
  finally:u.pair=pair
 roots=[]
 for k in np.arange(-4,4.1,1.):
  for m in np.arange(-4,4.1,1.):
   if not np.hypot(k,m):continue
   rr=root(resid,[k,m]); p=rr.x
   if rr.success and np.linalg.norm(resid(p))<1e-8 and np.linalg.norm(p)<6 and all(np.linalg.norm(z-p)>1e-4 for z in [pair[0],*roots]):roots.append(p)
 h=.002
 dx1,dx2=project(positions,ell,q,r0*np.exp(np.array([-h,h])))
 dd=project(positions,ell,q,[r0])[0]
 st1,st2=stars(r0*np.exp(np.array([-h,h])))
 mx=(dx2-dx1+st2-st1)/(2*h)
 mxx=(dx2+dx1-2*dd+st2+st1-2*stars(r0))/h**2
 eta=1+.5*(mxx-3*mx+2*M0)/(M0-.5*mx)
 return dict(ring_rms_mas=1e3*np.linalg.norm(xx.fun)/np.sqrt(14),eta_azimuthal=eta,
   S3_gap_mas=1e3*np.linalg.norm(f(x,0,True)),S3_signed_vector_mas=(1e3*f(x,0,True)).tolist(),
   counterimages_from_A=[dict(xy_arcsec=p.tolist(),err_mas=1e3*np.linalg.norm(p-pair[1])) for p in roots])
positions=np.c_[np.vstack([[0.,0.],u.centers]),np.zeros(3)]
out={}
for tag,group in [('center_only',positions[:1]),('companions_same_plane',positions),('companions_depth_equal_projected',positions+np.c_[np.zeros((3,2)),np.linalg.norm(positions,axis=1)])]:
 out[tag]={}
 for mode in ['joint','isolated']:
  def pr(ell):
   K,q=values(group,ell,mode)
   return project(group,ell,q,[r0,r1])
  def eq(ell):
   m=pr(ell);return m[1]/m[0]-B[1]/B[0]
  ell=brentq(eq,.03,100.)
  K,q=values(group,ell,mode)
  A=B[0]/pr(ell)[0]; q*=A
  assert np.allclose(project(group,ell,q,[r0,r1]),B)
  if mode=='joint':assert np.allclose(K@q,A)
  out[tag][mode]=dict(ell_kpc=ell*dk,response_Msun=q.tolist(),common_pin_trace_mass_per_arcsec=A,matrix=K.tolist(),**replay(group,ell,q))
out['conventional_S3_gap_mas']=1e3*np.linalg.norm(ep.fn('none')(base,0,True))
out['summary']='Same flat local static scalar operator as v0.5; equal-potential optical map and equal trace values assumed. Same-plane catalogs are sensitivity hypotheses, not confirmed pins. Calibration uses the two main-ring excess masses, exact once counting of ordinary compact term and no third source.'
(P/'jackpot_coupled_pins.json').write_text(json.dumps(out,indent=2)+'\n')
for tag,r in out.items():
 if isinstance(r,dict):
  for mode,a in r.items():print(tag,mode,a['ell_kpc'],a['eta_azimuthal'],a['ring_rms_mas'],a['S3_gap_mas'],a['counterimages_from_A'],a['response_Msun'])
 else: print(tag,r)
