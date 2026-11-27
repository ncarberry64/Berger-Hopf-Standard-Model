"""External X-ray-derived mass scale, conditional circular profile and plane."""
import json
import numpy as np
import coupled_well_screen as cw
from pathlib import Path
z=.2183;R500=623.; M500=8.56e13; s1=.609; s3=5.975
sky=np.array([146.33333610581,10.08535044288]); c0=cw.radec[0]
p=(sky-c0)*3600*[np.cos(np.deg2rad(c0[1])),1]
A=cw.A
D=cw.chi(z)/(1+z)*1000
a=cw.arad
def model(ratio,factor,zsource):
 def coef(t):
    v=t-p
    r=np.linalg.norm(v,axis=-1);R=r*D*a
    f=np.ones_like(r)
    if ratio:
        x=R/(R500/ratio)
        assert min(x)>1 if np.ndim(x) else x>1
        f=(np.log(x/2)+np.arccos(1/x)/np.sqrt(x*x-1))/(np.log(1+ratio)-ratio/(1+ratio))
    return (4*cw.G*M500*factor*(1-cw.chi(z)/cw.chi(zsource))/(cw.c**2*D*a*a)*f/r**2)[...,None]*v
 e=.02*np.eye(2);J=(coef(e)-coef(-e)).T/.04
 k=np.trace(J)/2
 ang=coef(A)[0]-coef(A)[1]
 return dict(c500=ratio,mass_factor=factor,kappa=k,shear=np.hypot(J[0,0]-k,J[0,1]),pair_shift_mas=1000*np.linalg.norm(ang),
          nonaffine_mas=1000*np.linalg.norm(ang-J@(A[0]-A[1])))
dist=np.linalg.norm(p)
rows={str(zs):[model(c,f,zs) for c in [None,2,3,5] for f in [1,2]] for zs in [s1,s3]}
ans=dict(distance_arcmin=dist/60,distance_mpc=dist*D*a/1000,source_rows=rows)
print(json.dumps(ans,indent=2))
Path('jackpot_erosita_neighbor.json').write_text(json.dumps(ans,indent=2)+'\n')
