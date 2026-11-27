"""Matched core on/off toy control. Only first two mass summaries and ring knots calibrate."""
import json
from pathlib import Path
import sys
import numpy as np
from scipy.special import k1, roots_legendre
from scipy.optimize import brentq, least_squares, root
from scipy.integrate import quad

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
nodes,weights=roots_legendre(64)
def yukawa_weight(s,L,r):
    """e^(-r/L) sinh(s/L)/(s/L), with r>=s; prevents overflow."""
    if s==0:return np.exp(-r/L)
    return np.exp((s-r)/L)*(-np.expm1(-2*s/L))/(2*s/L)
def force(r,s,L):
    r=np.asarray(r)
    ext=yukawa_weight(s,L,np.maximum(r,s))
    a=-np.expm1(np.log(np.maximum(ext,np.finfo(float).tiny))+np.log1p(r/L))/r**2
    if s==0:return a
    z=np.minimum(r,s)/L
    # e^-s/L times derivative of sinh(z)/z
    d=np.where(z<.01,np.exp(-s/L)*z*(1/3+z*z/30+z**4/840),
        ((z-1)*np.exp(z-s/L)+(z+1)*np.exp(-z-s/L))/(2*z*z))
    return np.where(r>=s,a,d/(s*L))
def mass(R,s,L):
    R=np.asarray(R,float)
    if s==0:return 1-(R/L)*k1(R/L)
    cut=np.arccos(np.minimum(1,R/s))
    # z=R tan(t) maps the semi-infinite LOS to [0,pi/2].
    def integrate(lo,hi):
        t=(hi+lo)[...,None]/2 + (hi-lo)[...,None]/2*nodes
        r=R[...,None]/np.cos(t)
        return (hi-lo)/2*np.sum(weights*r*r*force(r,s,L)*np.cos(t),axis=-1)
    return integrate(np.zeros_like(cut),cut)+integrate(cut,np.full_like(cut,np.pi/2))
for s in (0,1.843,22.3):
    for R in (4.97,5.15,7.63,13.11,25):
        for L in (4,16,50):
            z=np.sqrt(max(0,s*s-R*R))
            ref=sum(quad(lambda zz:R*R/np.hypot(R,zz)*force(np.hypot(R,zz),s,L),lo,hi,epsabs=1e-10)[0]
                    for lo,hi in ((0,z),(z,np.inf)) if hi>lo)
            assert abs(mass(R,s,L)-ref)<2e-8
            if R>=s:
                y= np.sinh(s/L)/(s/L) if s else 1.
                assert abs(mass(R,s,L)-(1-y*(R/L)*k1(R/L)))<2e-8
def gram(s,L):
    return -np.expm1(-s/L)/s, 1/s-L*(-np.expm1(-2*s/L))/(2*s*s)
def trace(s,L):
    def G(r):
        if min(r,s)==0:
            R=max(r,s)
            return -np.expm1(-R/L)/R if R else 1/L
        return 1/max(r,s)-L*np.exp(-abs(r-s)/L)*(-np.expm1(-2*min(r,s)/L))/(2*r*s)
    def dm(r):
        A,T=a*dk,b*dk
        return np.sum(2*u.stars/np.pi/(T-A)*(T*T/(T*T+r*r)-A*A/(A*A+r*r)))
    return Mh*G(0)+sum(quad(lambda r:G(r)*dm(r),lo,hi,epsrel=1e-10)[0]
                        for lo,hi in [(0,s),(s,np.inf)] if hi>lo)
def solve(s,beta,mode='matched_increment'):
    from functools import lru_cache
    R=np.array([r0,r1])*dk
    @lru_cache(None)
    def components(L):
        g0,gs=gram(s,L)
        w=beta/(1-beta)*g0/gs
        m=mass(R,s,L)
        unit=mass(R,0,L)+w*m
        off=(beta/(1-beta)/gs*trace(s,L)) if mode=='full_response' else 0.
        q=(target[0]-off*m[0])/unit[0]
        return q, q*unit+off*m
    def eq(L):
        return components(L)[1][1]/target[1]-1.
    grid=np.geomspace(.3,100,100)
    roots=[brentq(eq,x,y) for x,y in zip(grid[:-1],grid[1:]) if eq(x)*eq(y)<0]
    if len(roots)!=1:return dict(s=s,beta=beta,mode=mode,roots=roots)
    L=roots[0]
    q,m=components(L)
    assert np.allclose(m,target,rtol=1e-10)
    if q<=0:return dict(s=s,beta=beta,mode=mode,roots=roots,rejected_q=q)
    g0,gs=gram(s,L)
    lam=beta/gs
    traces=np.array([trace(0,L),trace(s,L)])
    B=np.array([[1/L,g0],[g0,gs]])
    assert np.linalg.eigvalsh(B)[0]>0
    lam=beta/gs
    reactions=np.linalg.solve([[1,0],[-lam*g0,1-lam*gs]],[q,0])
    amps=q*np.array([1,beta*g0/gs])

    assert np.allclose(reactions,amps/np.array([1,1-beta]))
    k=1/B[0,0]
    shell_off=lam*traces[1]/(1-beta)
    d=traces[0]+g0*shell_off+(B@reactions)[0]+q/k
    on=np.linalg.solve(np.eye(2)+np.diag([k,-lam])@B,
                       [k*(d-traces[0]),lam*traces[1]])
    assert np.allclose(on-[0,shell_off],reactions,rtol=1e-12)
    return dict(**ray(s,beta,L,q,shell_off if mode=='full_response' else 0.),mode=mode,reference_trace=traces.tolist(),core_target=d,
                shell_reaction_off=shell_off,shell_reaction_on=on[1],
                aperture_response_Msun=m.tolist())
def ray(s,beta,L,q,off):
    g0,gs=gram(s,L)
    w=beta/(1-beta)*g0/gs
    def shape(R):return mass(R,0,L)+(w+off/q)*mass(R,s,L)
    R=np.array([r0,r1])*dk
    assert np.allclose(q*shape(R),target,rtol=1e-10)
    def bplus(t):
        r=np.linalg.norm(t,axis=1)
        return basic(t)+(u.A0*q*shape(r*dk)/r**2)[:,None]*t
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
        return stars(r)+Mh+q*shape(r*dk)
    mx=(even(h)-even(-h))/(2*h)
    mxx=(even(h)+even(-h)-2*even(0))/h**2
    eta=1+.5*(mxx-3*mx+2*M0)/(M0-.5*mx)
    Rtest=np.array([4.97,*R,13.11,22.3,36.])
    raw=shape(Rtest)
    anchor=mass(Rtest,0,L)
    perp=raw-(raw@anchor)/(anchor@anchor)*anchor
    return dict(s=s,beta=beta,stability_margin=1-beta,L=L,q=q,eta=eta,
        fractional_perp=np.linalg.norm(perp)/np.linalg.norm(raw),
        ring_rms_mas=1e3*np.linalg.norm(opt.fun)/np.sqrt(14),
        source_gap_mas=1e3*np.linalg.norm(f(x,0,True)),
        B_pred=rr.x.tolist() if rr.success and np.linalg.norm(resid(rr.x))<1e-7 else None,
        B_error_mas=1e3*np.linalg.norm(rr.x-pair[1]) if rr.success and np.linalg.norm(resid(rr.x))<1e-7 else None)
rows=[solve(s*dk,beta,mode) for mode in ('matched_increment','full_response') for s in (.50,6.05) for beta in (0,.25,.50,.75,.90)]
(P/'jackpot_surface_susceptibility.json').write_text(json.dumps(rows,indent=2)+'\n')
for x in rows:print(x)
