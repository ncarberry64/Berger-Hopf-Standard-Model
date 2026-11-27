"""Replay frozen ordinary geometry plus archived R1 joint-minus-isolated residual."""
from pathlib import Path
from contextlib import redirect_stdout
import sys,io,json,inspect
import numpy as np
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'bhsm_environment_audit'))
with redirect_stdout(io.StringIO()):
 import he0435_joint_projected as h
 import he0435_joint_field_control as ctl
# Instrument only the existing replay: export deflection samples without
# changing its PDE, source, integration window, or mesh.
s=inspect.getsource(h.run).replace("  out['LOS_half_length_Mpc']=wins","  out['LOS_half_length_Mpc']=wins\n  out['joint_minus_iso_physical_alpha_rad']={w:[(g['joint']-g['isolated']).tolist() for g in [deflections(t,float(w)) for t in th]] for w in ['0.30','0.8','1.25']}")
exec(compile(s,h.__file__,'exec'),h.__dict__)
p=json.loads((P/'environment_fixed_stretch.json').read_text())
X=np.array([ctl.positions[k]-ctl.positions['G'] for k in ctl.names])
B=ctl.theta_g/ctl.xrad-ctl.positions['G']
R=float(np.median(np.linalg.norm(X[:3],axis=1)))
def trial(row):
 T=np.array(row['unreduced_tide'])
 b,s=row['params_radial_only']
 def front(x):
  r=np.linalg.norm(x,axis=1)
  return (b*((r/R)**s)/r)[:,None]*x+x@T.T
 alpha_ref=front(np.vstack([X,B]))*ctl.xrad
 def score(extra):
  aa=alpha_ref+extra; a=aa[:4]
  v=ctl.d2*ctl.xrad*(X-B)-ctl.d12*(a-aa[-1])
  y=X-ctl.w1*a/ctl.xrad-ctl.w2*np.stack([ctl.g_photo.apply(t,False)[0]/ctl.xrad for t in v])
  return y[3]-y[0], y
 ref,y=score(np.zeros((5,2)))
 assert abs(np.linalg.norm(ref)-row['held_anchor_source_RMS']['AD'])<1e-11
 return ref,score
def analytic_budget(a,b):
 # If a is a held residual vector and b the *change*, scale b only as
 # a diagnostic; no candidate is taken from a fit to the held-out data.
 u=np.linalg.norm(a);v=np.linalg.norm(b)
 k=-a@b/(v*v); cos=-a@b/(u*v)
 return dict(required_at_least_amplitude_ratio=u/v,cosine_toward_closure=cos,
             diagnostic_signed_multiplier=k,unavoidable_perpendicular_arcsec=np.linalg.norm(a+k*b),
             diagnostic_positive_only_min_arcsec=np.linalg.norm(a+max(0,k)*b))
h.Astar=h.Obj('sersic')
out=[]
for name,grids in [('nominal_group_470',[(90,1.5),(100,2.25)]),('near_group_470',[(90,1.5),(100,2.25)])]:
 if name.startswith('near'):
  center=np.array([69.559414,-12.276026])
  origin=np.array([h.cfg['main_RA_Deg'],h.cfg['main_Dec_Deg']])
  q=(center-origin)*3600*np.array([np.cos(np.deg2rad(origin[1])),1.])
  h.axis=q/np.linalg.norm(q);h.sep=41.9*h.d1*h.xrad
 row=next(r for r in p['rows'] if r['lens']=='HE0435' and r['scenario']==name)
 baseline,score=trial(row)
 for n, L in grids:
  with redirect_stdout(io.StringIO()):
   ff=h.run(n,L)
  for los,ds in ff['joint_minus_iso_physical_alpha_rad'].items():
   a,_=score(np.array(ds));b=a-baseline
   q=dict(scenario=name,N=n,domain_Mpc=L,los_Mpc=float(los),pde_converged=ff['converged'],
          max_scaled_PDE_residual=ff['last_max_scaled_residual'],minimum_elliptic_eigenvalue=ff['minimum_principal_eigenvalue'],
          ordinary_D_minus_A_mas=(1000*baseline).tolist(),
          extra_after_separate_G1_D_minus_A_microarcsec=(1e6*b).tolist(),
          remaining_gap_mas=float(1000*np.linalg.norm(a)),**analytic_budget(baseline,b))
   out.append(q)
   print(q,flush=True)
r=dict(scope='Conditional hybrid diagnostic: ordinary calibrated round-plus-fixed-environment map and its exact unchanged G1 receive the archived cored-star-plus-group R1 joint-minus-isolated deflection on the same observed rays and G1 centroid, with no amplitude or orientation fit. Does not derive any new W_s term or physical light delays. Signed multiplier and perpendicular bound are after-the-fact vector diagnostics only.',
  runs=out)
(P/'boundary_frozen_ray_test.json').write_text(json.dumps(r,indent=2)+'\n')
