"""Inner knots only. Conditional projected mass sensitivity, not detection.
Co-plane assumption; free ambient shear, stellar/BH profile fixed. Fit each mass
at fixed spread, stopping short of any claim of a confidence bound.
"""
import numpy as np
import json
import inner_rings_shared_well as u
from pathlib import Path
P=Path(__file__).resolve().parent
sky=np.array([146.733004235044,10.1036436603437])
lens=u.cw.radec[0]
cen=(sky-lens)*3600*[np.cos(np.deg2rad(lens[1])),1]
basic=u.basic
parts=[np.vstack(u.observed[:4]),u.observed[4]]
def mk(mass,rad):
    def v(t):
        d=t-cen
        pp=u.A0*mass*d/(np.sum(d*d,axis=1)[:,None]+(rad/u.dk)**2)
        return basic(t)+pp
    u.basic=v
    f=u.mk(u.observed)
    u.basic=basic
    return f
mat=None if u.exact_on else np.zeros((2,2)) # retain prior two-neighbor correction in all branches, no new nonlinear response here
B=mk(0,0)
p0=u.fit(B,mat,u.starts).x
r0=B(p0,mat)
rows={}
for rad in [3,30,100]:
   case=[]
   for m in [0,1e11,3e11,1e12,3e12,1e13,3e13,1e14]:
       f=mk(m,rad)
       fit=u.fit(f,mat,[p0]+u.starts[:2])
       r=fit.fun
       if m:
          fwr=f(p0,mat)-r0
          cr=r-r0
       else:fwr=cr=np.zeros_like(r)
       case.append(dict(mass=m,rms_mas=1e3*np.linalg.norm(r)/np.sqrt(14),
            unrefit_signal_rms_mas=1e3*np.linalg.norm(fwr)/np.sqrt(14),
            refit_signal_rms_mas=1e3*np.linalg.norm(cr)/np.sqrt(14),p=fit.x.tolist()))
   rows[str(rad)]=case
   print(rad,[(v['mass'],round(v['rms_mas'],3),round(v['refit_signal_rms_mas'],3)) for v in case],flush=True)
(P/'weigh_sw_plume.json').write_text(json.dumps(dict(center_arcsec=cen.tolist(),joint_existing=u.exact_on,profiles=rows),indent=2)+'\n')
