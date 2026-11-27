"""Point seeding in the v0.3 local operator; canonical flux vs diagnostic gradient export."""
import json
from pathlib import Path
import numpy as np
from scipy.integrate import quad, simpson
from scipy.optimize import brentq
from scipy.special import k1, gammaincinv
d=Path(__file__).parent
halo=json.loads((d/'he0435_halo_calibration.json').read_text())
ap=json.loads((d/'he0435_matched_aperture_proxy.json').read_text())
ref=halo['runs'][1]
RE=halo['RE_kpc']
M2=halo['projected_DM_Msun_at_RE']
v0=ap['predictions_kms']['frozen_stars']
G=4.30091727003628e-6
def mfrac(y):
    return np.where(y<1e-3,y*y*(.5+y*(-1/3+y/8)), -np.expm1(-y)-y*np.exp(-y))
def cyl(y):
    return 1-y*k1(y)
def prepare(N):
    r=np.geomspace(1e-6,1e4,N)
    t=np.linspace(0,12,N//4+1)
    n,re=3.51,3.984
    b=gammaincinv(2*n,.5)
    def nu_small(rr):
        R=rr[:,None]*np.cosh(t)
        y=b*(R/re)**(1/n)
        return simpson(np.exp(-y)*y/(n*R),x=t,axis=1)/np.pi
    nu=np.concatenate([nu_small(a) for a in np.array_split(r,N//250)])
    p=np.linspace(0,np.pi/4,257)
    a=.275*RE/1.182/np.cos(p)
    s=np.minimum((a[:,None]/r)**2,1)
    u=np.sqrt(1-s)
    h=s/(1+u)
    D=simpson(nu*r*r*simpson(h,x=p,axis=0),x=r)
    W=G*nu*r*simpson(h*(1+u+u*u)/3,x=p,axis=0)/D
    return r,W
def run(N):
    r,W=prepare(N)
    def moments(m):
        return float(np.sqrt(v0*v0+simpson(W*m,x=r)))
    def aperture(L):
        return moments(M2/cyl(RE/L)*mfrac(r/L))
    slope=next(row['flux_log_slope'] for row in ref['targets'] if np.isclose(row['r_kpc'],RE))
    y=brentq(lambda y:y*y*np.exp(-y)/mfrac(y)-slope,1e-2,10)
    L_slope=RE/y
    L_webb=brentq(lambda ell:aperture(ell)-220.1,.1,1000)
    def trial(L):
        x=RE/L
        projected=cyl(x)
        # independent cylinder integral through spherical shells of density exp(-r/L)/(4*pi*r*L^2)
        shell_proj=quad(lambda y: np.exp(-y)*x*x/(y*(1+np.sqrt(1-(x/y)**2))),x,np.inf,epsabs=1e-11)[0]+mfrac(x)
        assert abs(shell_proj-projected)<1e-9
        amp=M2/projected
        return dict(L_kpc=L,effective_total_Msun=amp,velocity_dispersion_kms=aperture(L),
                    flux_log_slope_at_RE=x*x*np.exp(-x)/mfrac(x),
                    radial_mass_relative_to_halo={str(row['r_kpc']):amp*mfrac(row['r_kpc']/L)/row['M3D']
                         for row in ref['targets']})
    massN=ref['M0']*(np.log1p(r/ref['scale_kpc'])-(r/ref['scale_kpc'])/(1+r/ref['scale_kpc']))
    assert abs(moments(massN)-ap['predictions_kms']['frozen_plus_halo'])<.02
    return dict(slope_matched=trial(L_slope),aperture_matched=trial(L_webb))
a,b=run(4097),run(8193)
assert abs(a['aperture_matched']['L_kpc']-b['aperture_matched']['L_kpc'])<.001
b['scope']='Local Euclidean 3D spherical, B constant and positive. Canonical-flux point source remains exactly inverse square. The alternative gradient export is not the candidate canonical BHSM rule. Each alternative fixes its amplitude to the spherical halo projected mass at RE; equal metric potentials, frozen spherical isotropic light-traces-mass stars, ideal unmasked Webb aperture. Off-aperture ratios compare to a halo-model continuation, not direct mass data.'
print(json.dumps(b,indent=2))
(d/'he0435_seed_surface_flux.json').write_text(json.dumps(b,indent=2)+'\n')
