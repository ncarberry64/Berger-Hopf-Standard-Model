"""Geometric identifiability of three evaluated deflection vectors."""
from pathlib import Path
import sys,json,numpy as np
from scipy.integrate import quad
p=Path(__file__).resolve().parent
sys.path.insert(0,str(p.parent/'bhsm_environment_audit'/'pinned_extra'))
from r1_background_geometry import D
pl=[.6828,1.36,1.4869]
ss=[1.4869,1.4874,2.763,3.428,4.205]
def flat(a,b):
 return quad(lambda z:(.3*(1+z)**3+.7)**-.5,a,b,epsabs=1e-12)[0]/(1+b)
def check(metric,dist):
 def matrix(s):return np.array([[dist(x,z)/dist(0,z) if z>x else 0. for x in pl] for z in s])
 W=matrix(ss)
 _,sig,V=np.linalg.svd(W,full_matrices=False)
 n=V[-1]/V[-1,-1]
 assert sig[-1]<1e-12
 assert max(abs(W@n))<1e-12
 options={}
 for z in [.90,1.15,1.30,1.36,1.40,1.45,1.4869,2.6,5.0]:
  row=matrix([z]).ravel()
  options[str(z)]=dict(new_row_residual_per_unit_third_plane=float(row@n),
                       augmented_singular_vals=np.linalg.svd(np.vstack([W,row]),compute_uv=False).tolist())
 return dict(metric=metric,W=W.tolist(),singular_values=sig.tolist(),null_per_unit_third=n.tolist(),augmented=options)
out={'scope':'At one observed angle for three evaluated bend vectors, not arbitrary joint physical mass maps or changing intercepts. Source weights are FLRW distance factors. Putative nearer source is a geometry design, not a detection.',
 'plane_z':pl,'catalogued_source_z':ss,'check':[check('flat 0.3 matter',flat),check('frozen curved R1',D)]}
(p/'cswa31_distance_rank.json').write_text(json.dumps(out,indent=2)+'\n')
for x in out['check']:print(x['metric'],x['null_per_unit_third'],x['singular_values'],x['augmented']['1.36'])
