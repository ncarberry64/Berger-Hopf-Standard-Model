"""On/off stationary loaded surface with a compliant core interface.
No pin depression prescribed; no third-source calibration."""
import sys,json
from pathlib import Path
import numpy as np
from scipy.special import k1
from scipy.integrate import quad
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
a,b=u.scale.T; z=u.stars/(b-a)
def stars(r):return (z*(np.hypot(r,a)-a-np.hypot(r,b)+b)).sum()
B=np.array([M0,M1])-np.array([stars(r) for r in [r0,r1]])-Mh
base=ep.fit(ep.fn('none'),u.starts).x
def pointG(r,L):
 return -np.expm1(-r/L)/r if r else 1/L
def G(r,s,L):
 if r==0 or s==0:return pointG(max(r,s),L)
 return 1/max(r,s)-L*np.exp(-abs(r-s)/L)*(-np.expm1(-2*min(r,s)/L))/(2*r*s)
def S(x):return np.sinh(x)/x if x else 1.
def perq(r,s,L):
 assert np.min(r)>s or np.isclose(np.min(r),s,rtol=0,atol=1e-12)
 x=r/L
 return 1-S(s/L)*x*k1(x)
# Independent LOS checks for projected optical force sourced by the spherical interface.
# Exterior depth = (1-S(s/L)exp(-r/L))/r per unit reaction.
for rr,ss,L in [(5.,1.,3.),(5.,4.,10.),(2.,0.,1.)]:
 q=quad(lambda z:rr*rr*(1-S(ss/L)*(1+(r:=np.hypot(rr,z))/L)*np.exp(-r/L))/r**3,0,np.inf)[0]
 assert abs(q-perq(rr,ss,L))<1e-9

def ordinary_trace(s,L):
 def dr(r):
  A,T=a*dk,b*dk
  return np.sum(u.stars*2/np.pi/(T-A)*(T*T/(T*T+r*r)-A*A/(A*A+r*r)))
 cuts=[(0,s),(s,np.inf)] if s>0 else [(0,np.inf)]
 load=Mh*pointG(s,L)+sum(quad(lambda r:dr(r)*G(r,s,L),lo,hi,epsrel=2e-10)[0] for lo,hi in cuts)
 return load

def outputs(s,L,q):
 def build():
  def bplus(t):
   r=np.linalg.norm(t,axis=1)
   return basic(t)+(u.A0*q*perq(r*dk,s,L)/r**2)[:,None]*t
  u.basic=bplus
  try:return ep.fn('none')
  finally:u.basic=basic
 f=build()
 opt=min((least_squares(lambda p:f(np.r_[0,0,p]),seed,bounds=(u.lo[2:],u.hi[2:]),ftol=1e-11,xtol=1e-11,gtol=1e-11) for seed in [base[2:],[.08,.08,.3],[0,0,.05]]),key=lambda o:o.cost)
 x=np.r_[0,0,opt.x]
 h=.0005
 def proj(t):
  r=r0*np.exp(t)
  return stars(r)+Mh+q*perq(r*dk,s,L)
 mx=(proj(h)-proj(-h))/(2*h); mxx=(proj(h)+proj(-h)-2*proj(0))/h**2
 def resid(t):
  u.pair=np.vstack([pair[0],t])
  try:return build()(x,0,True)
  finally:u.pair=pair
 rr=root(resid,[1.,.75]) # fixed seed in expected other half; no B coordinates used
 return dict(eta=1+.5*(mxx-3*mx+2*M0)/(M0-.5*mx),
             ring_rms_mas=1e3*np.linalg.norm(opt.fun)/np.sqrt(14),
             third_gap_mas=1e3*np.linalg.norm(f(x,0,True)),
             B_forecast=rr.x.tolist() if rr.success and np.linalg.norm(resid(rr.x))<1e-7 else None,
             B_error_mas=1e3*np.linalg.norm(rr.x-pair[1]) if rr.success else None)
rows={}
for label,s in [('point',0.),('compact_ordinary_horizon_scale_proxy',2*u.cw.G*Mh/u.cw.c**2),('stellar_core_0p066arcsec',.066*dk),('stellar_cut_0p50arcsec',.50*dk),('galaxy_interface_0p90arcsec_stress',.90*dk)]:
 def er(L):
  vals=perq(np.array([r0,r1])*dk,s,L)
  return vals[1]/vals[0]-B[1]/B[0]
 L=brentq(er,.1,60)
 q=B[0]/perq(r0*dk,s,L)
 assert np.allclose(perq(np.array([r0,r1])*dk,s,L)*q,B)
 # E=1/2<u,A u>-<j,u>+κ/2(d-u_s)^2.
 # q=κ(d-u_s), u_s=u0_s+q K_ss. Fit q via calibration, then
 # solve for d for each fixed stiffness. Recompute the equilibrium forward.
 K=G(s,s,L); off=ordinary_trace(s,L)
 trace=[]
 for rel in (.25,1.,4.):
  kappa=rel/K
  D=off+q*K+q/kappa
  qcheck=kappa*(D-off)/(1+kappa*K)
  assert np.isclose(qcheck,q)
  on=off+K*qcheck
  assert on<D and on>off
  deltaE_free=0.5*qcheck*qcheck*K+0.5*kappa*(on-D)**2-0.5*kappa*(off-D)**2
  assert np.isclose(deltaE_free,-.5*qcheck*qcheck*K*(1+kappa*K))
  trace.append(dict(relative_stiffness=rel,core_preferred_value=D,uncoupled_trace=off,coupled_trace=on,
       reaction=qcheck,energy_relaxation_within_coupled_functional=deltaE_free))
 rows[label]=dict(source_interface_kpc=s,ell_kpc=L,q_Msun_equivalent=q,actual_coupled_trace_outputs=trace,**outputs(s,L,q))
(P/'jackpot_compliant_pin.json').write_text(json.dumps(rows,indent=2)+'\n')
for r,x in rows.items():print(r,{k:v for k,v in x.items() if k!='actual_coupled_trace_outputs'})
