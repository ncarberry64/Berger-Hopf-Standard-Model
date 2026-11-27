"""Spherical Einstein-budget closure + nominal Webb square aperture (not a lens refit)."""
import json
import numpy as np
from scipy.integrate import simpson, cumulative_trapezoid
from pathlib import Path
G = 4.30091727003628e-6 # kpc (km/s)^2 / solar mass
RE, thetaE, rh, M0 = 7.026976, 1.182, 50.11625, 6.97318e12
stars, Mhalo2, sigcrit, n, re = 10**11.1, 1.50034724e11, 2.14927715e9, 3.51, 3.984
from scipy.special import gammaincinv, gammainc
b = gammaincinv(2*n, .5)
target = np.pi*RE**2*sigcrit
starfrac = gammainc(2*n,b*(RE/re)**(1/n))
Mmatched = (target-Mhalo2)/starfrac
def run(N):
    r=np.geomspace(1e-6,1e4,N)
    t=np.linspace(0,12, N//4+1)
    def deproject(rr):
        R=rr[:,None]*np.cosh(t)
        y=b*(R/re)**(1/n)
        return simpson(np.exp(-y)*y/(n*R),x=t,axis=1)/np.pi
    nu=np.concatenate([deproject(x) for x in np.array_split(r, max(1,N//300))])
    mass=cumulative_trapezoid(4*np.pi*r*r*nu,r,initial=0)
    mass/=mass[-1]
    x=r/rh
    halo=M0*(np.log1p(x)-x/(1+x))
    phi=np.linspace(0,np.pi/4,257)
    R=.275*RE/thetaE/np.cos(phi)
    s=np.minimum((R[:,None]/r)**2,1)
    u=np.sqrt(1-s)
    shell=s/(1+u)
    A=simpson(shell,x=phi,axis=0)
    B=simpson(shell**2*(u+2)/3,x=phi,axis=0)
    # integral of sin^2(theta) over both polar caps: 2/3 - u + u^3/3
    w=r*r*nu
    def pred(m, ra):
        I=np.ones_like(r) if ra is None else 1+(r/ra)**2
        beta=1-1/I
        rhs=G*m*nu*I/r**2
        pressure=-cumulative_trapezoid(rhs[::-1],r[::-1],initial=0)[::-1]/I
        return float(np.sqrt(simpson(r*r*pressure*(A-beta*B),x=r)/simpson(w*A,x=r)))
    return dict(frozen_stars=pred(stars*mass,None), frozen_plus_halo=pred(stars*mass+halo,None),
                frozen_plus_halo_bh1e9=pred(stars*mass+halo+1e9,None),
                aperture_matched_iso=pred(Mmatched*mass+halo,None),
                aperture_matched_OM={str(f):pred(Mmatched*mass+halo,f*re) for f in (.5,1,2,5)})
a,z=run(4097),run(8193)
assert max(abs(a[k]-z[k]) for k in a if k!="aperture_matched_OM")<.02
assert max(abs(v-z["aperture_matched_OM"][k]) for k,v in a["aperture_matched_OM"].items())<.02
# A two-amplitude closure is descriptive, not a test on independent data.
matrix=np.array([[stars*starfrac, Mhalo2],
                  [z['frozen_stars']**2,z['frozen_plus_halo']**2-z['frozen_stars']**2]])
scenarios=[]
for v in (215.9,220.1,224.3):
    star_scale,halo_scale=np.linalg.solve(matrix,[target,v**2])
    scenarios.append(dict(aperture_kms=v, stellar_scale=float(star_scale), halo_scale=float(halo_scale),
                          projected_halo_fraction=float(halo_scale*Mhalo2/target)))
res=dict(two_amplitude_closures=scenarios, observed=[220.1,4.2], projected_Einstein_proxy_Msun=target, projected_frozen_stars_Msun=stars*starfrac, projected_halo_Msun=Mhalo2, frozen_budget_fraction=(stars*starfrac+Mhalo2)/target, closure_stellar_rescale=Mmatched/stars, closure_stellar_Msun=Mmatched, predictions_kms=z)
print(json.dumps(res,indent=2))
Path(__file__).with_suffix('.json').write_text(json.dumps(res,indent=2)+'\n')
