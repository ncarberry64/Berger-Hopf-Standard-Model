"""Does a smooth foreground sheet absorb the diagnostic outer-shape changes?"""
from pathlib import Path
import json
import numpy as np
from scipy.optimize import minimize_scalar
p=Path(__file__).resolve().parent
src=p/'he0435_outer_geometry_ray_control.py'
s={'__name__':'replay','__file__':str(src)}
exec(compile(src.read_text().split("assert abs(1000*ns['rms']",1)[0],str(src),'exec'),s)
bk,ns,projected=s['bk'],s['ns'],s['projected']
ref=np.array([projected(b,np.inf) for b in bk])/1e9
b2=(bk/s['cal']['RE_kpc'])**2
base=ns['forward'](ref,True)
def centered(v):return v-v.mean(axis=0)
def maxpair(v):return 1000*float(np.linalg.norm(v[:,None]-v[None,:],axis=2).max())
out=[]
for R in (20.,50.,100.):
    exact=s['rays'](R)
    def fake(a):
        return ns['forward'](ref+a*b2,True)
    def fit(sel):
        return minimize_scalar(lambda a:np.sum(centered((fake(a)-exact)[sel])**2),
            bracket=(-75.,0.),method='brent',options={'xtol':1e-12}).x
    ids=np.arange(4)
    amp=fit(ids)
    rem=fake(amp)-exact
    hold=[]
    for i in ids:
        sel=ids[ids!=i]
        u=fake(fit(sel))-exact
        hold.append(float(1000*np.linalg.norm(u[i]-u[sel].mean(axis=0))))
    pred=dict(kpc=R,raw_pair_mas=maxpair(exact-base),equivalent_sheet_at_RE_Msun=amp*1e9,
              residual_pair_mas=maxpair(rem),residual_centered_rms_mas=1000*ns['rms'](rem),
              held_one_ray_mas=hold)
    assert pred['residual_pair_mas']<pred['raw_pair_mas']
    out.append(pred)
(p/'he0435_outer_shape_vs_sheet.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
