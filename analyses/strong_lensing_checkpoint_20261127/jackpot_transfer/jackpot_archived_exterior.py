"""Compact stationary source, independent generalized flux and screened trace."""
from pathlib import Path
import json,sys
import numpy as np
from scipy.special import k0,k1
from scipy.optimize import brentq,least_squares
from scipy.integrate import quad
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'visible_mass_envelope_20261126/external_weak/jackpot_neighbor'))
import jackpot_current_geometry_holdout as geo
ep,u=geo.ep,geo.u
ep.W=geo.Ws['closed_R1']
u.get_exact=lambda t:np.zeros_like(t)
u.exact_origin=np.zeros((1,2))
base=u.basic
cal=json.loads((P/'jackpot_equilibrium_calibration.json').read_text())
r0,r1=cal['apertures_arcsec']; Dk=cal['apertures_kpc'][0]/r0
M0,M1=cal['total_projected_Msun']; Mh=1.6e9
K=lambda x:x*k1(x)
# Validate the optical projection of the exterior Yukawa mode by direct force integral.
for x in [.1,.5,1,2,5]:
    ans=quad(lambda z:x*x*(1+(r:=np.hypot(z,x)))*np.exp(-r)/r**3,0,np.inf,epsabs=2e-12)[0]
    assert abs(ans-K(x))<1e-10
result={}
for name,logs in [('Salpeter',[11.13,11.52]),('Chabrier',[10.85,11.27])]:
    u.stars=10**np.array(logs)
    a,b=u.scale.T
    z=u.stars/(b-a)
    def stars(r):
        r=np.asarray(r)[...,None]
        return (z*(np.hypot(r,a)-a-np.hypot(r,b)+b)).sum(axis=-1)
    B0,B1=np.array([M0,M1])-stars([r0,r1])-Mh
    sx=r0*r0*np.sum(z*(1/np.hypot(r0,a)-1/np.hypot(r0,b)))
    sxx=sx+r0*r0*np.sum(z*(a*a/np.hypot(r0,a)**3-b*b/np.hypot(r0,b)**3))
    def moments(x):
        Y=(B1-B0)/(K(x)-K(x*r1/r0))
        Q=B0+Y*K(x)
        d=sx+Y*x*x*k0(x)
        dd=sxx+Y*(2*x*x*k0(x)-x**3*k1(x))
        return Q,Y,d,dd
    result[name]={}
    for eta in [.93,.96,.98]:
        xi=2*(eta-1)
        def eq(x):
            q,y,d,dd=moments(x)
            return (dd+(-3+xi/2)*d+(2-xi)*M0)/M0
        x=brentq(eq,.2,1.2)
        q,y,d,dd=moments(x)
        assert np.isclose(1+.5*(dd-3*d+2*M0)/(M0-d/2),eta)
        ell=r0/x
        def envmass(r):return q-y*K(r/ell)
        assert np.allclose(envmass(np.array([r0,r1])),[B0,B1])
        row=dict(q_Msun=q,y_Msun=y,y_over_q=y/q,ell_kpc=ell*Dk,eta=eta,
          outer_S3_extra_projected_Msun=envmass(np.linalg.norm(u.pair,axis=1)[0]))
        # For nonnegative compact source Y/Q is an average of sinh(r/ell)/(r/ell).
        if y>=q:
            sh=ell*brentq(lambda v:np.sinh(v)/v-y/q,1e-5,10)
            row['positive_source_thin_shell_radius_kpc']=sh*Dk
            allr=np.linalg.norm(np.vstack([*u.observed,u.pair]),axis=1)
            assert sh<r0
            if sh<allr.min():
                nom=ep.fit(ep.fn('none'),u.starts).x
                for kind,norm in [('shared',u.A0),('anchored',r0*r0/M0/ep.W[u.z0,u.z1])]:
                    def bplus(t):
                        r=np.linalg.norm(t,axis=1)
                        v=norm*(stars(r)+Mh+envmass(r))-u.A0*(stars(r)+Mh)
                        return base(t)+(v/r**2)[:,None]*t
                    u.basic=bplus
                    try:f=ep.fn('none')
                    finally:u.basic=base
                    xx=min((least_squares(lambda x:f(np.r_[0,0,x]),start,bounds=(u.lo[2:],u.hi[2:]),ftol=1e-11,xtol=1e-11,gtol=1e-11) for start in [nom[2:],[.08,.08,.3],[0,0,.05]]),key=lambda o:o.cost)
                    xfit=np.r_[0,0,xx.x]; s3=f(xfit,0,True)
                    row[kind]=dict(ring_rms_mas=1e3*np.linalg.norm(xx.fun)/np.sqrt(14),S3_gap_mas=1e3*np.linalg.norm(s3),S3_signed_mas=(1e3*s3).tolist())
        else:row['positive_compact_source_impossible_for_this_branch']=True
        result[name][str(eta)]=row
(P/'jackpot_archived_exterior.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
