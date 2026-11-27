"""Archived Jackpot geometry, projected point kernel, and frozen counterimage tracer."""
import json
from pathlib import Path
import sys
import numpy as np
from scipy.special import k1
from scipy.optimize import least_squares, root

P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'visible_mass_envelope_20261126/external_weak/jackpot_neighbor'))
import jackpot_current_geometry_holdout as geo
ep,u=geo.ep,geo.u
ep.W=geo.Ws['closed_R1']
u.get_exact=lambda t:np.zeros_like(t)
u.exact_origin=np.zeros((1,2))
basic=u.basic
ap=json.loads((P/'jackpot_equilibrium_calibration.json').read_text())
r0,r1=ap['apertures_arcsec']
dk=ap['apertures_kpc'][0]/r0
M0,M1=ap['total_projected_Msun']
Mh=1.6e9
a,b=u.scale.T
def stars(r):
    return (u.stars/(b-a)*(np.hypot(r,a)-a-np.hypot(r,b)+b)).sum()
target=np.array([M0-stars(r0)-Mh,M1-stars(r1)-Mh])
base=ep.fit(ep.fn('none'),u.starts).x
def mass(R,s,L):
    assert s==0
    x=np.asarray(R)/L
    return 1-x*k1(x)
def predict(profile):
    R=np.array([r0,r1])*dk
    assert np.allclose(profile(R),target,rtol=1e-9)
    def bplus(t):
        r=np.linalg.norm(t,axis=1)
        return basic(t)+(u.A0*profile(r*dk)/r**2)[:,None]*t
    def build():
        u.basic=bplus
        try:return ep.fn('none')
        finally:u.basic=basic
    f=build()
    opt=min((least_squares(lambda p:f(np.r_[0,0,p]),seed,bounds=(u.lo[2:],u.hi[2:]),ftol=1e-11,xtol=1e-11,gtol=1e-11)
        for seed in [base[2:],[.08,.08,.3],[0,0,.05]]),key=lambda o:o.cost)
    x=np.r_[0,0,opt.x]
    # Read/use B only after calibration; the root is not seeded at B.
    pair=u.pair.copy()
    def resid(t):
        u.pair=np.vstack([pair[0],t])
        try:return build()(x,0,True)
        finally:u.pair=pair
    rr=root(resid,[1.,.75])
    h=.0005
    def even(t):
        r=r0*np.exp(t)
        return stars(r)+Mh+profile(r*dk)
    mx=(even(h)-even(-h))/(2*h)
    mxx=(even(h)+even(-h)-2*even(0))/h**2
    eta=1+.5*(mxx-3*mx+2*M0)/(M0-.5*mx)
    valid=rr.success and np.linalg.norm(resid(rr.x))<1e-7
    return dict(eta=eta,ring_rms_mas=1e3*np.linalg.norm(opt.fun)/np.sqrt(14),
        source_gap_mas=1e3*np.linalg.norm(f(x,0,True)),
        B_pred=rr.x.tolist() if valid else None,
        B_error_mas=1e3*np.linalg.norm(rr.x-pair[1]) if valid else None)
