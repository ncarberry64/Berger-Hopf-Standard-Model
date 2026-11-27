"""No-fit replay of equal-charge shell controls with the same four rays and stars."""
import json
from pathlib import Path
import numpy as np
from scipy.integrate import quad, simpson
p=Path(__file__).resolve().parent
def source_prefix(name,stop):
    path=p/name
    scope={'__name__':'control_replay','__file__':str(path)}
    exec(compile(path.read_text().split(stop,1)[0],str(path),'exec'),scope)
    return scope
ns=source_prefix('he0435_core_exterior_check.py','# Conditional topographic exterior')
ap=source_prefix('he0435_seed_surface_flux.py','a,b=run(4097)')
cal=json.loads((p/'he0435_halo_calibration.json').read_text())
ref=cal['runs'][1]
rs,M0=ref['scale_kpc'],ref['M0']
bk=ns['r']*ns['d1']*1000
def enclosed(r):
    x=r/rs
    return M0*(np.log1p(x)-x/(1+x))
def projected(b,R):
    if b>=R:return 0.
    limit=np.pi/2 if np.isinf(R) else np.arccos(b/R)
    return quad(lambda t:enclosed(b/np.cos(t))*np.cos(t),0,limit,epsabs=1.,epsrel=1e-10)[0]
def rays(R):
    return ns['forward'](np.array([projected(b,R) for b in bk])/1e9,True)
r,W=ap['prepare'](8193)
v0=ap['v0']
def dispersion(R):
    # All options retain identical g(r) below R, but the aperture includes a LOS tail.
    return float(np.sqrt(v0**2+simpson(W*np.where(r<R,enclosed(r),0),x=r)))
unc=rays(np.inf)
def diff(v):
    d=v-unc
    return float(1000*np.linalg.norm(d[:,None]-d,axis=2).max())
assert abs(1000*ns['rms'](unc)-ref['simple_foreground_redistribution_RMS_mas'])<1e-5
assert abs(dispersion(np.inf)-ap['ap']['predictions_kms']['frozen_plus_halo'])<.02
out=[]
for R in [20.,50.,100.,np.inf]:
    u=rays(R)
    out.append(dict(compensation_radius_kpc=None if np.isinf(R) else R,common_source_RMS_mas=1000*ns['rms'](u),
                    max_pair_difference_vs_uncompensated_mas=diff(u), stellar_aperture_kms=dispersion(R)))
(p/'he0435_outer_geometry_ray_control.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
