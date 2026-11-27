"""Reproject fixed physical masses; retain measured angular stellar light scales."""
import json,sys
from functools import lru_cache
from pathlib import Path
import numpy as np
from scipy.ndimage import spline_filter
import jackpot_current_geometry_holdout as prior
ep=prior.ep;u=ep.u;cw=u.cw;P=Path(__file__).resolve().parent
origdk=cw.dk;origcenters=cw.centers.copy();origscale=cw.scale.copy()
origdist=ep.Ds.copy()
names=list(prior.Ws)
def angular_d(z,geom):
 if geom=='closed_R1':return prior.D(0,z)*1000.
 if geom=='same_expansion_flat':
  from r1_background_geometry import L
  return L*prior.sameE(0,z)*1000/(1+z)
 return cw.chi(z)*1000/(1+z)
def set_up(geom,recompute):
 D0=angular_d(u.z0,geom)
 newdk=D0*u.asc
 sc=newdk/origdk
 ep.Ds={z:angular_d(z,geom) for z in ep.Ds}
 ep.W=prior.Ws[geom]
 def basic(t):
    r=np.linalg.norm(t,axis=-1)
    q=nTheta(t)
    a=u.scale[:,0];b=u.scale[:,1]
    proj=np.sum(u.stars*(np.hypot(r[:,None],a)-a-np.hypot(r[:,None],b)+b)/(b-a),axis=1)
    A=4*cw.G/(cw.c**2*newdk*u.asc)
    v=A*(proj+1.6e9)[:,None]*t/q
    for center,m in zip(u.centers,cw.star_near):
      dr=t-center;v+=A*m*dr/(nTheta(dr)+(3/newdk)**2)
    return v
 def nTheta(t):
    return np.sum(t*t,axis=1)[:,None]
 u.basic=basic
 if recompute:
  cw.dk=newdk
  cw.centers=origcenters*sc
  cw.scale=origscale*sc
  # Keep same underlying phenomenological g-scale across backgrounds, vary geometry only.
  f=P/f'jackpot_physical_close_field_{geom}.npz'
  if not f.exists():cw.integrate(650,896,3500,108,[0,0,0],field_file=f)
  zz=np.load(f);assert abs(float(zz['dk'])-newdk)<1e-10
  u.grid=[spline_filter(x,order=3) for x in zz['field']]
  u.gridbox=float(zz['box']);u.gridstep=float(zz['step']);u.dk=newdk
  u.exact_origin=u.get_exact(np.zeros((1,2)))
 return dict(lens_distance_kpc=D0,eROSITA_distance_kpc=ep.Ds[ep.zc],scale=sc)
def main():
 data={}
 for g in names:
  data[g]=dict(scale=set_up(g,True))
  for arm in ['none','separate']:
   f=ep.fn(arm)
   fit=ep.fit(f,u.starts)
   data[g][arm]=dict(inner_rms_mas=float(np.linalg.norm(fit.fun)*1000/np.sqrt(14)),fit=fit.x.tolist(),outer={str(s):(f(fit.x,s,True)*1e3).tolist() for s in [0,75,150]})
  print(g,data[g],flush=True)
  (P/'jackpot_physical_geometry.json').write_text(json.dumps(data,indent=2)+'\n')
if __name__=='__main__':main()
