"""Frozen Jackpot profile substitution: matched same-optics retrospective test."""
from pathlib import Path
import sys,json
import numpy as np
from scipy.optimize import least_squares
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'visible_mass_envelope_20261126/external_weak/jackpot_neighbor'))
import jackpot_current_geometry_holdout as geom
ep,u=geom.ep,geom.u
basic=u.basic
u.get_exact=lambda t:np.zeros_like(t)
u.exact_origin=np.zeros((1,2))
rings=[x.copy() for x in u.observed]; pair=u.pair.copy()
template=json.loads((P/'jackpot_settled_envelope_template.json').read_text())
control=json.loads((P/'jackpot_conventional_composite_control.json').read_text())
r0,r1=template['fit_range_arcsec']; L=np.log(r1/r0)
m0,m1=template['total_mass_Msun']
shape=template['shape']['Salpeter']; A=shape['A_Msun']
eta=.96; p=shape['targets'][str(eta)]['p']; c=shape['targets'][str(eta)]['c']
assert np.allclose(u.stars,10**np.array([11.13,11.52]))
assert np.allclose(u.scale,[[.066,.50],[.082,6.05]])
def stars(r):
    r=np.asarray(r)[...,None]
    a,b=u.scale.T
    return (u.stars*(np.hypot(r,a)-a-np.hypot(r,b)+b)/(b-a)).sum(axis=-1)
def env(r,how):
    x=np.log(r/r0)
    y=x if how=='quadratic' else np.clip(x,0,L)
    return A*np.exp(p*y+c*y*y+(p+2*c*y)*(x-y))
def make(norm,how,ray_extra=None):
    def correction(t):
        r=np.linalg.norm(t,axis=1)
        # Calibration's residual includes central point mass since the original
        # subtraction was stars-only; remove it before adding to basic.
        tot=norm*(stars(r)+env(r,how))
        keep=u.A0*(stars(r)+1.6e9)
        return ((tot-keep)/r**2)[:,None]*t
    def field(t):
        base=basic(t)+correction(t)
        if ray_extra is not None and len(t)==2:
            base+=np.asarray(ray_extra)[:,None]*t/np.linalg.norm(t,axis=1)[:,None]
        return base
    u.basic=field
    try:return ep.fn('none')
    finally:u.basic=basic
def fit(f,pars):
    def call(x):return f(np.r_[0.,0.,x])
    bounds=(np.array(u.lo[2:]),np.array(u.hi[2:]))
    starts=[pars,np.array([0.,0.,.25]),np.array([.08,.08,.28]),np.array([.08,.08,.05])]
    ans=min((least_squares(call,x,bounds=bounds,ftol=1e-11,xtol=1e-11,gtol=1e-11,max_nfev=250) for x in starts),key=lambda o:o.cost)
    return np.r_[0.,0.,ans.x]
def score(f,x):
    v={str(s):(1000*f(x,s,True)).tolist() for s in (0,75,150)}
    return dict(ring_rms_mas=float(1000*np.linalg.norm(f(x))/np.sqrt(14)),x=x.tolist(),
                third_pair_vectors_mas=v,third_pair_mas={s:float(np.linalg.norm(a)) for s,a in v.items()},
                s1_reduced_to_s2_arcsec=float(x[-1]*ep.W[u.z1,u.z2]))
assert np.allclose(stars([r0,r1])+env(np.array([r0,r1]),'tangent'),[m0,m1])
ep.W=geom.Ws['closed_R1']
W01=ep.W[u.z0,u.z1]; norm_anchor=r0*r0/m0/W01
norms={'shared_physical':u.A0,'aperture_anchored':norm_anchor}
f0=ep.fn('none')
pars0=np.array(control['closed_R1']['x'])
assert np.isclose(score(f0,pars0)['third_pair_mas']['0'],control['closed_R1']['third_pair_mas']['0'])
rows={}
for kind,norm in norms.items():
    for how in ('tangent','quadratic'):
        f=make(norm,how)
        x=fit(f,pars0[2:])
        rows[kind+'_'+how]=dict(fixed_geometry=score(f,np.r_[0.,0.,pars0[2:]]),ring_only_nuisance_refit=score(f,x),
          anchor_deflections_arcsec=[norm*m0/r0*W01,norm*m1/r1*ep.W[u.z0,u.z2]])
# Signed directional diagnostic only. Independent derivatives are not a
# proposed physical radial profile, and nothing is updated with S3 observations.
err=np.array([.02,.02,.05,.04])
def local_diag(norm,how,pars,h):
    f=make(norm,how)
    delta=f(pars,0,True)
    J=np.column_stack([(make(norm,how,h*e)(pars,0,True)-make(norm,how,-h*e)(pars,0,True))/(2*h) for e in np.eye(2)])
    U,s,V=np.linalg.svd(J)
    if U[0,0]<0: U[:,0]*=-1
    if np.linalg.det(U)<0: U[:,1]*=-1
    H=[]
    try:
        for e in np.eye(4).reshape(4,2,2):
            u.pair=pair+h*e; plus=make(norm,how)(pars,0,True)
            u.pair=pair-h*e; minus=make(norm,how)(pars,0,True)
            H.append((plus-minus)/(2*h))
    finally:u.pair=pair
    H=np.array(H).T
    C=(H*err**2)@H.T
    return dict(delta_mas=1e3*delta,strong_unit=U[:,0],weak_unit=U[:,1],
        singular_values=s,residual_along_axes_mas=1e3*(U.T@delta),
        diagnostic_only_linear_kicks_mas=-1e3*np.linalg.solve(J,delta),
        source_jacobian=H,covariance=C,local_positional_chi2=delta@np.linalg.solve(C,delta))
for kind,norm in norms.items():
    for how in ('tangent','quadratic'):
        row=rows[kind+'_'+how]
        pars=np.array(row['ring_only_nuisance_refit']['x'])
        d=local_diag(norm,how,pars,1e-5)
        d2=local_diag(norm,how,pars,5e-6)
        for key in d:assert np.allclose(d[key],d2[key],rtol=1e-6,atol=1e-7),key
        row['no_S2_local_diagnostic']={k:np.asarray(v).tolist() for k,v in d.items()}
# Paired jitter with the same coordinate-error model and seed as the control.
rng=np.random.default_rng(161348); trial=[]
for _ in range(128):
    u.observed=[x+rng.normal(0,.03,x.shape) for x in rings]
    u.pair=pair+rng.normal(0,[[.02,.02],[.05,.04]])
    base=ep.fn('none'); cb=ep.fit(base,[pars0]).x
    vals=[]
    for label,norm in norms.items():
        f=make(norm,'tangent')
        x=fit(f,np.array(rows[label+'_tangent']['ring_only_nuisance_refit']['x'][2:]))
        v=np.array([1000*np.linalg.norm(f(x,s,True)) for s in (0,75,150)])
        b=np.array([1000*np.linalg.norm(base(cb,s,True)) for s in (0,75,150)])
        vals.append([b,v,v-b])
    trial.append(vals)
u.observed=rings;u.pair=pair
out=dict(scope='Same observed knots, geometry and angular backbone as nominal conventional control; no S3 fitting. Same shear and S1 ranges. Shared normalization uses the archived flat physical normalization with R1 angular efficiencies in both models. Aperture-anchored sensitivity renormalizes only the central spherical total, keeping the nearby galaxies fixed.',
 profiles=rows,conventional=score(f0,pars0),anchored_to_shared_physical_ratio=norm_anchor/u.A0,
 mass_at_S3_rays={how:env(np.linalg.norm(pair,axis=1),how).tolist() for how in ['tangent','quadratic']},
 conventional_extended_equivalent_mass_Msun={str(r):float(pars0[0]*(r/1.43)**pars0[1]*r/u.A0) for r in [r0,r1,*np.linalg.norm(pair,axis=1)]},
 paired_jitter_fraction_envelope_lower=np.mean(np.array(trial)[:,:,2,:]<0,axis=0).tolist(),
 jitter_model='128 paired draws, independent 30 mas per ring coordinate, 20/20 and 50/40 mas for S3. Not a posterior.',
 jitter_q16_q50_q84=np.quantile(trial,[.16,.5,.84],axis=0).tolist(),
 jitter_axes_after_quantiles=['normalization: shared physical, anchored','control, envelope, envelope minus control','S2 dispersion 0,75,150 km/s'])
(P/'jackpot_matched_composite_substitution.json').write_text(json.dumps(out,indent=2)+'\n')
for l,r in rows.items():print(l,r['fixed_geometry']['ring_rms_mas'],r['fixed_geometry']['third_pair_mas'],r['ring_only_nuisance_refit']['ring_rms_mas'],r['ring_only_nuisance_refit']['third_pair_mas'])
print('normalizations',norm_anchor/u.A0)
print(np.array(out['jitter_q16_q50_q84'])[:,:,:,0])
