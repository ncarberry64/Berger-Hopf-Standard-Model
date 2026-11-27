"""Archived BHSM v0.3 neighborhood export, conditional on unit v0.5 gravity-only seam."""
from pathlib import Path
from contextlib import redirect_stdout
from itertools import combinations
import sys,json,io
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq,minimize_scalar
P=Path(__file__).resolve().parent
sys.path[:0]=[str(P.parent/'bhsm_environment_audit'),str(P.parent/'bhsm_environment_audit'/'pinned_extra')]
from r1_background_geometry import D,G,speed,xrad,bg,L
with redirect_stdout(io.StringIO()):
    import he0435_joint_projected as jp
    import s3_stellar_transfer as j
from he0435_joint_field_control import d1,d2,d12,w1,w2,theta_g,g_photo,positions,names
RH_0=L/np.sqrt(-bg.OMEGA_K0)
def seam(mfun,z):
    RH=RH_0/(1+z)
    # Exact spherical reference match, outer downward crossing. Rationalized.
    def F(r):
        m=mfun(r)
        return 2*m*RH/(r*r*(1+np.sqrt(1-2*m/r)))-1
    rr=np.geomspace(1e-6,2,260)
    roots=[brentq(F,t,u,xtol=1e-15) for t,u in zip(rr[:-1],rr[1:]) if F(t)*F(u)<0]
    assert F(roots[-1]*1.01)<0<F(roots[-1]*.99)
    return roots[-1],float(mfun(roots[-1]))
def shaper(x):
    if x>=1:return np.pi*x/2-1
    return x*np.arcsin(x)-x*x/(1+np.sqrt(1-x*x))
def shell(t,z,a,m,N):
    ang=np.linalg.norm(t)
    if ang==0:return np.zeros(2)
    b=ang*D(0,z)*xrad
    fac=shaper(b/a) if np.isinf(N) else shaper(b/a)-N*shaper(b/(N*a))
    V=m*speed**2/a
    alpha=4*a*V*fac/(speed**2*b*xrad)
    # Independent 3-D radial-ray projection with both breakpoints.
    def fx(u):
        r=b/np.cos(u)
        return V*(max(0.,min(r,N*a)-a)/r**2)*(b/np.cos(u))
    limits=[0]+[np.arccos(b/s) for s in (a,N*a) if np.isfinite(s) and s>b]+[np.pi/2]
    direct=4*sum(quad(fx,p,q,epsabs=1e-9,epsrel=1e-10)[0] for p,q in zip(limits[:-1],limits[1:]))/(speed**2*xrad)
    assert abs(direct-alpha)<1e-9
    return alpha*t/ang
def rms(b):return float(np.sqrt(np.mean(np.sum((b-b.mean(axis=0))**2,axis=1))))
def maxpair(b):return max(np.linalg.norm(b[a]-b[c]) for a,c in combinations(range(len(b)),2))
out={'classification':'Conditional BHSM v0.3 hash-pinned analytic shape, unit closure xi=1 and equal scalar-optical potentials assumptions. No fit enters the unit prediction. Nonclosing diagnostic amplitudes never used as BHSM predictions.',
'HE0435':[],'Jackpot':{}}
for name,logm in j.masses.items():
    m=10**np.array(logm)*G/speed**2
    def mfun(r):return j.m3(r,m)
    a,M=seam(mfun,j.z)
    base=j.theta-np.array([j.ray(t,m)[0] for t in j.theta])
    y=base[0]-base[1]
    tests=[]
    for span in [20.,100.,np.inf]:
        c=np.array([j.weight*shell(t,j.z,a,M,span) for t in j.theta])
        d=c[0]-c[1]
        A=float(y@d/(d@d))
        tests.append(dict(outer_seam_ratio=span if np.isfinite(span) else None,unit_pair_bend_arcsec=float(np.linalg.norm(d)),unit_gap_arcsec=float(np.linalg.norm(y-d)),
          diagnostic_best_nonnegative_export_multiplier=A,diagnostic_residual_perpendicular_arcsec=float(np.linalg.norm(y-A*d))))
    out['Jackpot'][name]=dict(stellar_seam_kpc=1000*a,baseline_gap_arcsec=float(np.linalg.norm(y)),runs=tests)
s=jp.Obj('sersic'); z=.4546
def star(t):
    R=np.linalg.norm(t)*d1*xrad
    def ext(u):
        c=np.cos(u); si=np.sin(u)
        return s.rho(min(R/c,4.))*R**3*si/(c*c*(1+si))
    m=s.mt*(s.enclosed(R)+quad(ext,0,np.pi/2,epsabs=2e-9,epsrel=5e-7)[0])
    return 4*m/(R*xrad)*t/np.linalg.norm(t)
def environment(t):
    q=t-67.1*jp.axis
    R=np.linalg.norm(q)*d1*xrad
    a,b=.025,jp.r200
    m=np.pi*jp.gamma/2*R**2*(1/(np.hypot(a,R)+a)-1/(np.hypot(b,R)+b))
    return 4*m/(R*xrad)*q/np.linalg.norm(q)
obs=np.vstack([[positions[n]-positions['G'] for n in names],theta_g/xrad])
base=np.array([star(t)+environment(t) for t in obs])
def trace(alpha):
    out=[]
    for t,f in zip(obs[:-1],alpha[:-1]):
        x=xrad*(d2*(t-obs[-1])-d12*(f-alpha[-1]))
        b,_=g_photo.apply(x,False)
        out.append(t-w1*f-w2*b/xrad)
    return np.array(out)
T0=trace(base)
assert abs(rms(T0)-.8988788685852)<1e-7
a,M=seam(lambda r:float(s.mass(r)),z)
for span in [20.,100.,np.inf]:
    de=np.array([shell(t,z,a,M,span) for t in obs])
    T=lambda A:trace(base+A*de)
    res=minimize_scalar(lambda A:rms(T(A)),bounds=(0,30),method='bounded')
    out['HE0435'].append(dict(outer_seam_ratio=span if np.isfinite(span) else None,stellar_seam_kpc=1000*a,baseline_rms_arcsec=rms(T0),
      unit_pair_shift_arcsec=maxpair(T(1)-T0),unit_rms_arcsec=rms(T(1)),diagnostic_best_multiplier=float(res.x),diagnostic_residual_rms_arcsec=float(res.fun)))
# Leave-one-system-out diagnostics, not action-owned amplitudes.
out['conditional_cross_transfer']=[]
for i,span in enumerate([20.,100.,np.inf]):
    h=out['HE0435'][i]['diagnostic_best_multiplier']
    dHe=np.array([shell(t,z,a,M,span) for t in obs])
    for label,logm in j.masses.items():
        m=10**np.array(logm)*G/speed**2
        mfun=lambda r:j.m3(r,m)
        aa,mm=seam(mfun,j.z)
        B=j.theta-np.array([j.ray(t,m)[0] for t in j.theta])
        d=np.array([j.weight*shell(t,j.z,aa,mm,span) for t in j.theta])
        y=B[0]-B[1]; d=d[0]-d[1]
        l=out['Jackpot'][label]['runs'][i]['diagnostic_best_nonnegative_export_multiplier']
        out['conditional_cross_transfer'].append(dict(outer_seam_ratio=span if np.isfinite(span) else None,
            stellar_IMF=label,HE_fit_applied_to_Jackpot_gap_arcsec=float(np.linalg.norm(y-h*d)),
            Jackpot_fit_applied_to_HE_rms_arcsec=rms(trace(base+l*dHe))))
assert all(0.8<r['unit_rms_arcsec']<.83 for r in out['HE0435'])
(P/'native_seam_transfer.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
# A second external observable: isotropic, spherical, top-hat aperture
# (no PSF or dynamical anisotropy); luminosity weights from HST F814W.
Lums=10.**(-.4*(np.array([18.75,17.15])-17.15))
aa,bb=j.scales.T
rap=.6*j.dl*xrad
def nu(r):return float(np.sum(Lums/(2*np.pi**2*(bb-aa))*(1/(aa*aa+r*r)-1/(bb*bb+r*r))))
def Jgeo(r):
    if r<=rap:return r**3
    f=(rap/r)**2
    return -r**3*np.expm1(1.5*np.log1p(-f))
den=j.m2(rap,Lums)
out['Jackpot_aperture_control']={}
for label,logs in j.masses.items():
    m=10**np.array(logs)*G/speed**2
    mfun=lambda r:j.m3(r,m)
    aj,mj=seam(mfun,j.z)
    def evaluate(A):
        def g(r):
            N=mfun(r)*speed**2/r**2
            return N+A*mj*speed**2/aj*max(0,min(r,20*aj)-aj)/r**2
        val=sum(quad(lambda r:nu(r)*g(r)*Jgeo(r),l,u,epsrel=1e-9)[0] for l,u in [(0,rap),(rap,aj),(aj,20*aj),(20*aj,np.inf)])
        return float(np.sqrt(4*np.pi/3*val/den))
    out['Jackpot_aperture_control'][label]={'GR_kms':evaluate(0),'unit_export_kms':evaluate(1),'HE0435_fitted_export_kms':evaluate(out['HE0435'][0]['diagnostic_best_multiplier'])}
print(json.dumps(out['Jackpot_aperture_control'],indent=2))
(P/'native_seam_transfer.json').write_text(json.dumps(out,indent=2)+'\n')
