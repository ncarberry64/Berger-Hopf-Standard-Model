"""Conditional mass screen with nonlinear joint response included.
Uniform box/resolution/depth across arms. S3 never used to fit or select mass.
"""
import json
import numpy as np
from scipy.ndimage import map_coordinates,spline_filter
from pathlib import Path
import inner_rings_shared_well as u
from coupled_well_screen import integrate
P=Path(__file__).resolve().parent
sky=np.array([146.733004235044,10.1036436603437])
c0=u.cw.radec[0]
cen=(sky-c0)*3600*[np.cos(np.deg2rad(c0[1])),1]
oldmt,oldcen=u.cw.mt,u.cw.centers
basic=u.basic
case=[]
r0=None
def fit_mass(M,rad):
    u.cw.centers=np.vstack((oldcen,cen*u.dk))
    u.cw.mt=lambda r,j: oldmt(r,j) if j<3 else M*(r/np.hypot(r,rad))**3
    f=P/f'sw_plume_four_source_{M:.0e}_{rad:d}.npz'
    if not f.exists():
        integrate(400,640,2200,96,[0,0,0,0],field_file=f)
    z=np.load(f)
    u.grid,u.gridbox,u.gridstep=[spline_filter(x,order=3) for x in z['field']],float(z['box']),float(z['step'])
    u.exact_origin=u.get_exact(np.zeros((1,2)))
    u.exact_on=True
    def v(t):
        d=t-cen
        return basic(t)+u.A0*M*d/(np.sum(d*d,axis=1)[:,None]+(rad/u.dk)**2)
    u.basic=v
    fun=u.mk(u.observed)
    fit=u.fit(fun,None,u.starts)
    return fit,fun
for M,rad in [(0,30),(3e11,30),(1e12,30),(3e12,30),(1e12,100)]:
    fit,f=fit_mass(M,rad)
    r=fit.fun
    if r0 is None:
        r0,p0=r,fit.x
    delta=r-r0
    change=f(p0,None)-r0
    rec=dict(mass=M,plummer_kpc=rad,train_mas=1e3*np.linalg.norm(r)/np.sqrt(14),
        refit_delta_mas=1e3*np.linalg.norm(delta)/np.sqrt(14),
        frozen_delta_mas=1e3*np.linalg.norm(change)/np.sqrt(14),params=fit.x.tolist())
    case.append(rec)
    print(rec,flush=True)
    (P/'weigh_sw_plume_four_source.json').write_text(json.dumps(case,indent=2)+'\n')
