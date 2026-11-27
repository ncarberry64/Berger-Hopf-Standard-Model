"""Zero-net-charge radial redistribution witnesses; no tuning to S3."""
import json,sys
from pathlib import Path
import numpy as np
from scipy.special import k0,k1
from scipy.optimize import brentq,least_squares
from numpy.polynomial.legendre import leggauss
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'visible_mass_envelope_20261126/external_weak/jackpot_neighbor'))
import jackpot_current_geometry_holdout as geom
ep,u=geom.ep,geom.u
ep.W=geom.Ws['closed_R1']
u.get_exact=lambda t:np.zeros_like(t)
u.exact_origin=np.zeros((1,2))
basic=u.basic
T=json.loads((P/'jackpot_settled_envelope_template.json').read_text())
prior=json.loads((P/'jackpot_stationary_screen.json').read_text())
r0,r1=T['fit_range_arcsec']
M0,M1=T['total_mass_Msun']; Mh=1.6e9
ab=np.asarray(u.scale)
a,b=ab.T
# Pointwise lower bounds on C_eta, also valid for any weighted integral.
g=np.geomspace(.01,4,6000)
ratio_upper=g[1:]*k1(g[:-1])/k0(g[1:])
middle=np.min(g[:-1]**2-4+np.minimum(.93*(2-ratio_upper),.98*(2-ratio_upper)))
small=-4+.93*(2-1/k0(.01))
large=16-4+.98*(1.5-4) # lower bound from x K1/K0 <= x + .5, monotone above 4
bound=min(small,middle,large)
assert bound> -2.726
targets=prior['Salpeter']['target_curvature_functional']
assert max(targets.values())<bound
# Parameterized exact pairs: short screening length l, long length f*l.
# h integral avoids cancellation at small x and is also the exact log-scale mixture.
ns,ws=leggauss(64)
def kernel(x,f,eta=.96):
    log=np.log(f)/2
    t=np.asarray(x)[...,None]*np.exp((ns-1)*log)
    h=t*t*k0(t)
    v=h@ws*log
    cv=((t*t+2*eta-4)*h-eta*t**3*k1(t))@ws*log
    return v,cv
for f in (1.25,2,4,8):
    for x in (.03,.1,1,8,30):
        assert np.isclose(kernel(x,f)[0],(x/f)*k1(x/f)-x*k1(x),rtol=1e-8,atol=0)
u.stars=10**np.array([10.85,11.27])
def stars(r):
    r=np.asarray(r)[...,None]
    return np.sum(u.stars*(np.hypot(r,a)-a-np.hypot(r,b)+b)/(b-a),axis=-1)
b0,b1=np.array([M0,M1])-stars([r0,r1])-Mh
rt=b1/b0; ct=prior['Chabrier']['target_curvature_functional']['0.96']
pars0=ep.fit(ep.fn('none'),u.starts).x
norm_anchor=r0*r0/M0/ep.W[u.z0,u.z1]
r3=np.linalg.norm(u.pair,axis=1)
def tracer(norm,mass):
    def field(t):
        r=np.linalg.norm(t,axis=1)
        delta=norm*(stars(r)+Mh+mass(r))-u.A0*(stars(r)+Mh)
        return basic(t)+delta[:,None]*t/r[:,None]**2
    u.basic=field
    try: model=ep.fn('none')
    finally: u.basic=basic
    def fit(x):return model(np.r_[0.,0.,x])
    fit0=min((least_squares(fit,p,bounds=(u.lo[2:],u.hi[2:]),ftol=1e-11,xtol=1e-11,gtol=1e-11) for p in [pars0[2:],[.08,.08,.05],[.08,.08,.3],[0,0,.25]]),key=lambda o:o.cost)
    x=np.r_[0.,0.,fit0.x]
    v=1e3*model(x,0,True)
    return dict(ring_rms_mas=1e3*np.linalg.norm(fit(x[2:]))/np.sqrt(14),S3_vector_mas=v.tolist(),S3_gap_mas=np.linalg.norm(v))
rows=[]
xg=np.geomspace(.001,40,4000)
for f in (1.25,2.,4.,8.):
    def obs(x):
        v,c=kernel(x,f)
        return kernel(x*r1/r0,f)[0]/v,c/v,v
    Q,C,_=obs(xg)
    for fix in (.066,.50,6.05):
        qf,cf,vf=obs(r0/fix)
        def w(q):return (rt-q)/(qf-q)
        def residual(q,c):return (1-w(q))*c+w(q)*cf-ct
        y=residual(Q,C)
        sols=[]
        for j in np.flatnonzero(y[1:]*y[:-1]<0):
            x=brentq(lambda x:residual(*obs(x)[:2]),xg[j],xg[j+1])
            q,c,v=obs(x)
            if 0<w(q)<1:sols.append((x,w(q),v))
        assert len(sols)==1
        x,wt,v=sols[0]; short=np.array([r0/x,fix]); amplitudes=np.array([b0*(1-wt)/v,b0*wt/vf])
        def projected(r):
            return sum(A*kernel(np.asarray(r)/ell,f)[0] for A,ell in zip(amplitudes,short))
        def dimensionless_enclosed_3d(r):
            return sum(A*((1+(y:=r/ell/f))*np.exp(-y)-(1+(x:=r/ell))*np.exp(-x)) for A,ell in zip(amplitudes,short))
        assert np.allclose(projected(np.array([r0,r1])),[b0,b1],rtol=1e-9)
        assert abs(residual(q,c))<1e-9
        assert projected(5000)<1 and dimensionless_enclosed_3d(5000)<1
        radii=np.geomspace(.01,1000,2500)
        def dd(r,ell):return np.exp(-r/ell)/ell**2
        diff=sum(A*(dd(radii,ell)-dd(radii,f*ell)) for A,ell in zip(amplitudes,short))
        # Compare signed implied density with same enclosed stellar profile's 3D density.
        stellar=sum(m*2/np.pi/(B-A)*(B*B/(radii*radii+B*B)-A*A/(radii*radii+A*A))/radii
                    for m,(A,B) in zip(u.stars,ab))
        # 4 pi r rho cancels, point mass contributes nothing here.
        negative=radii[diff+stellar<0]
        rows.append(dict(ratio_long_to_short=f,fixed_short_arcsec=fix,short_scales_arcsec=short.tolist(),strengths_Msun=amplitudes.tolist(),
             pair_sign_crossover_arcsec=(2*short*np.log(f)/(1-1/f)).tolist(),
             S3_envelope_Msun=projected(r3).tolist(),
             radii_negative_implied_optical_density_arcsec=[float(negative.min()),float(negative.max())] if negative.size else [],
             shared=tracer(u.A0,projected),anchored=tracer(norm_anchor,projected)))
scope='Static spherical redistribution at unchanged net exterior charge. Exact matches to the two Chabrier aperture targets and eta=.96; nominal rays, S2 absent. Not a derived BHSM branch.'
budgets={}
for label,logs in [('Salpeter',[11.13,11.52]),('Chabrier',[10.85,11.27])]:
    ordinary_mass=10**np.array(logs)
    far=ordinary_mass.sum()+Mh
    budgets[label]=dict(total_visible_plus_point_Msun=far,
             lens_calibration_aperture_Msun=[M0,M1],
             max_remaining_mass_at_or_beyond_second_ring_Msun=far-M1)
o=dict(scope=scope,positive_density_equal_baryonic_charge_budget=budgets,lower_curvature_bound=bound,pointwise_bounds=[small,middle,large],
       excludes_nominal_Salpeter_positive_pair_sums=True,Chabrier=rows)
(P/'jackpot_compensated_screen.json').write_text(json.dumps(o,indent=2)+'\n')
for j in rows:print(j['ratio_long_to_short'],j['fixed_short_arcsec'],round(j['shared']['ring_rms_mas'],1),round(j['shared']['S3_gap_mas'],1),round(j['anchored']['S3_gap_mas'],1),j['radii_negative_implied_optical_density_arcsec'])
print('bound',bound)
