"""Outer-only nullspace witness; geometry/normalization are the durable Jackpot replay's."""
from pathlib import Path
import sys,json
import numpy as np
from scipy.optimize import linprog
from numpy.polynomial.legendre import leggauss
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'visible_mass_envelope_20261126/external_weak/jackpot_neighbor'))
import jackpot_current_geometry_holdout as geo
ep,u=geo.ep,geo.u
ep.W=geo.Ws['closed_R1']
u.get_exact=lambda t:np.zeros_like(t)
u.exact_origin=np.zeros((1,2))
basis=json.loads((P/'jackpot_equilibrium_calibration.json').read_text())
R,S=basis['apertures_kpc']
dk=R/basis['apertures_arcsec'][0]
ray=np.linalg.norm(u.pair,axis=1)*dk
n,w=leggauss(48)
def shell(b,r):
 b=np.asarray(b)[...,None]
 mid=np.mean(r,axis=1)
 h=(r[:,-1]-r[:,0])/(2*n[-1])
 def primitive(p):
    q=np.maximum(p,b)
    return np.sqrt((q-b)*(q+b))-b*np.arccos(np.clip(b/q,0,1))
 return 1-(primitive(mid+h)-primitive(mid-h))/(2*h)
def mat(rs,half):
 r=rs[:,None]+half*n
 q=(R/r)**2
 assert (S<r).all()
 return r,np.array([np.ones(len(rs)),shell(R,r),(q/np.sqrt(1-q))@w/2,(q/(1-q)**1.5)@w/2,shell(S,r)])
r,M=mat(np.array([8.,9.5,11,14,19,28]),.1)
_,s,v=np.linalg.svd(M)
a=v[-1];a*=np.sign(a[-1])
a/=np.maximum(a,0).sum()
assert np.max(abs(M@a))<1e-12
MASS=1e11
base=u.basic
params=np.array(json.loads((P/'jackpot_conventional_composite_control.json').read_text())['closed_R1']['x'])
f=ep.fn('none')
def replay(r,m):
 def field(t):
    R=np.linalg.norm(t,axis=1)
    return base(t)+((shell(R*dk,r)@m)*MASS*u.A0/R**2)[:,None]*t
 u.basic=field
 try:ff=ep.fn('none')
 finally:u.basic=base
 ref=1e3*f(params,0,True); new=1e3*ff(params,0,True)
 return dict(base_signed_S3_mas=ref.tolist(),new_signed_S3_mas=new.tolist(),
             delta_norm_mas=np.linalg.norm(new-ref),new_gap_mas=np.linalg.norm(new),
             ring_residual_change_norm_mas=1e3*np.linalg.norm(ff(params)-f(params)))
witness=dict(weights=a.tolist(),s3_delta_cyl_mass_Msun=(MASS*shell(ray,r)@a).tolist(),
  null_residual=(M@a).tolist(),rings_kpc=[R,S],S3_kpc=ray.tolist(),**replay(r,a))
checks={}
for width in (.05,.1,.2):
 for nn in (100,300):
    r,M=mat(np.geomspace(8,60,nn),width)
    C=shell(ray,r)[0]
    # Max absolute far-ray mass per moved 1e11. An arbitrary finite library,
    # not a continuous bound; positive weights are source/destination budgets.
    opt=linprog(np.r_[-C,C],A_eq=np.block([[M,-M],[np.ones(nn),np.zeros(nn)]]),
      b_eq=[0]*5+[1],bounds=(0,None),method='highs',options={'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
    assert opt.success
    m=opt.x[:nn]-opt.x[nn:]
    assert np.max(abs(M@m))<5e-9
    checks[f'{width}_{nn}']=dict(max_far_delta_cyl_mass_Msun=MASS*(C@m),**replay(r,m))
out=dict(scope='Synthetic fixed angular R1 replay. Sparse ring summaries, not joint likelihood or proof on the physical model. No retuning. LP is only a grid leverage bound for chosen domain and fixed far-ray radius; no S3 measured misclosure targeted.',witness=witness,grids=checks)
(P/'jackpot_outer_null_control.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
