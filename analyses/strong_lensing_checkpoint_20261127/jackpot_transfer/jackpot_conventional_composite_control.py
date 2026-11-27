"""Replay conventional composite knot-only comparator; no BHSM close field."""
import json,sys
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent
root=P.parent/'visible_mass_envelope_20261126/external_weak/jackpot_neighbor'
sys.path.insert(0,str(root))
import jackpot_current_geometry_holdout as p
ep,u=p.ep,p.u
u.get_exact=lambda t:np.zeros_like(t)
u.exact_origin=np.zeros((1,2))
rings=[x.copy() for x in u.observed]; pair=u.pair.copy()
out={}
for label in ('flat_LCDM_distance_control','closed_R1'):
 ep.W=p.Ws[label]
 f=ep.fn('none')
 o=ep.fit(f,u.starts)
 nom={str(s):(1000*f(o.x,s,True)).tolist() for s in (0,75,150)}
 rng=np.random.default_rng(161348);err=[]
 for _ in range(128):
    u.observed=[x+rng.normal(0,.03,x.shape) for x in rings]
    u.pair=pair+rng.normal(0,[[.02,.02],[.05,.04]])
    trial=ep.fn('none')
    t=ep.fit(trial,[o.x])
    err.append([1000*np.linalg.norm(trial(t.x,s,True)) for s in (0,75,150)])
 u.observed=rings;u.pair=pair
 out[label]=dict(ring_rms_mas=float(np.linalg.norm(o.fun)*1e3/np.sqrt(14)),x=o.x.tolist(),
   s1_reduced_angle_to_s2_arcsec=o.x[-1]*ep.W[u.z1,u.z2],
   third_pair_vectors_mas=nom,third_pair_mas={s:float(np.linalg.norm(a)) for s,a in nom.items()},
   jitter_q16_q50_q84_mas=np.quantile(err,[.16,.5,.84],axis=0).tolist())
(P/'jackpot_conventional_composite_control.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
