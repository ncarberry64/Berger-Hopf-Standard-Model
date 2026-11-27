"""Project the archived distributed galaxy law, fit two ring mass targets, test S3."""
import json,sys
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from scipy.optimize import least_squares,brentq,root
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'visible_mass_envelope_20261126/external_weak/jackpot_neighbor'))
import jackpot_current_geometry_holdout as geo
from r1_background_geometry import H0,speed,G,bg
ep,u=geo.ep,geo.u
ep.W=geo.Ws['closed_R1']
u.get_exact=lambda t:np.zeros_like(t)
u.exact_origin=np.zeros((1,2))
basic=u.basic; pair=u.pair.copy()
cal=json.loads((P/'jackpot_equilibrium_calibration.json').read_text())
r0,r1=cal['apertures_arcsec']; Dk=cal['apertures_kpc'][0]/r0
R0,R1=np.array([r0,r1])*Dk
M0,M1=cal['total_projected_Msun']; Mh=1.6e9
a,b=u.scale.T
# Flat local full path projection, not curvature geometry within galaxy.
# M_3D = C max(r-s,0) before cutoff, corresponding to a continuous 1/r^2 density tail.
def outer_col(R,s): # spherical shell projection integral from s to infinity
    R=np.asarray(R)
    return R*np.arcsin(np.minimum(1,R/s))-s+np.sqrt(np.maximum(0,(s-R)*(s+R)))
def full(R,s,t=np.inf):
    return outer_col(R,s)-(outer_col(R,t) if np.isfinite(t) else 0)
for R,s,t in [(5,4,50),(3,4,np.inf),(5,4,np.inf),(3,2,7),(7,2,6)]:
    def proj(r):
        q=min(1,(R/r)**2)
        return q/(1+np.sqrt(1-q))
    q=max(R,s)
    test=max(0,min(t,R)-s)+(quad(proj,q,t,epsabs=1e-11)[0] if q<t else 0)
    assert abs(test-full(R,s,t))<2e-10
def moments(R,s):
    if R>=s:return np.pi/2,0.
    return np.arcsin(R/s),1/np.sqrt((s-R)*(s+R))
def deriv(R,s,t):
    d,dd=moments(R,s)
    if np.isfinite(t):
        dt,ddt=moments(R,t)
        d-=dt; dd-=ddt
    return R*d,R*d+R**2*dd
out={}
for label,logs in [('Salpeter',[11.13,11.52]),('Chabrier',[10.85,11.27])]:
    u.stars=10**np.array(logs)
    z=u.stars/(b-a)
    sps=float(u.stars.sum())
    def stars(r):
        return (z*(np.hypot(np.asarray(r)[...,None],a)-a-np.hypot(np.asarray(r)[...,None],b)+b)).sum(axis=-1)
    def stars_enclosed(s):
        x=s/Dk
        return Mh+np.sum((2/np.pi)*z*(b*np.arctan(x/b)-a*np.arctan(x/a)))
    B=np.array([M0,M1])-stars([r0,r1])-Mh
    sx=r0*r0*np.sum(z*(1/np.hypot(r0,a)-1/np.hypot(r0,b)))
    sxx=sx+r0*r0*np.sum(z*(a*a/np.hypot(r0,a)**3-b*b/np.hypot(r0,b)**3))
    nom=ep.fit(ep.fn('none'),u.starts).x
    scl=r0*r0/M0/ep.W[u.z0,u.z1]
    def model(norm,mass):
        def bplus(t):
            r=np.linalg.norm(t,axis=1)
            v=norm*(stars(r)+Mh+mass(r*Dk))-u.A0*(stars(r)+Mh)
            return basic(t)+(v/r**2)[:,None]*t
        u.basic=bplus
        try:return ep.fn('none')
        finally:u.basic=basic
    def counterimages(builder,px):
        # Forward-locate a counterimage from measured A only. Search the same
        # fixed field for all roots; B is read solely for reporting distances.
        def residual(t):
            u.pair=np.vstack([pair[0],t])
            try:return builder()(px,0,True)
            finally:u.pair=pair
        roots=[]
        for x in np.arange(-4,4.01,.80):
            for y in np.arange(-4,4.01,.80):
                if np.hypot(x,y)<.05:continue
                rr=root(residual,[x,y])
                if not rr.success or np.linalg.norm(residual(rr.x))>1e-8 or np.linalg.norm(rr.x)>6 or np.min(np.linalg.norm(np.array([pair[0],*roots])-rr.x,axis=1))<1e-4:continue
                roots.append(rr.x)
        return [dict(xy_arcsec=p.tolist(),offset_from_observed_B_arcsec=np.linalg.norm(p-pair[1])) for p in sorted(roots,key=lambda a:a[0])]
    def run(mass,norm,hyp=False):
        f=model(norm,mass)
        opt=min((least_squares(lambda x:f(np.r_[0,0,x]),start,bounds=(u.lo[2:],u.hi[2:]),ftol=1e-11,xtol=1e-11,gtol=1e-11) for start in [nom[2:],[.08,.08,.3],[0,0,.05]]),key=lambda o:o.cost)
        px=np.r_[0,0,opt.x]
        ans=dict(ring_rms_mas=1e3*np.linalg.norm(opt.fun)/np.sqrt(14),S3_gap_mas=[1e3*np.linalg.norm(f(px,d,True)) for d in [0,75,150]],S3_signed_mas=(1e3*f(px,0,True)).tolist(),nuisance=opt.x.tolist())
        if hyp:ans['counterimages_from_A']=counterimages(lambda:model(norm,mass),px)
        return ans
    rows={}
    for t in (np.inf,20.,50.,100.):
        def er(s):
            mass=full(np.array([R0,R1]),s,t)
            return mass[1]/mass[0]-B[1]/B[0]
        s=brentq(er,.001,18)
        C=B[0]/full(R0,s,t)
        def mass(R):return C*full(R,s,t)
        assert np.allclose(mass(np.array([R0,R1])),B,rtol=1e-10)
        dx,dxx=C*np.array(deriv(R0,s,t))
        mx=sx+dx; mxx=sxx+dxx
        eta=1+.5*(mxx-3*mx+2*M0)/(M0-mx/2)
        rows[str(t)]=dict(transition_kpc=s,C_Msun_kpc=C,v_flat_kms=np.sqrt(G*1000*C),eta=eta,
         required_point_proxy_Msun=C*s,stellar_plus_compact_enclosed_at_transition_Msun=stars_enclosed(s),
         extra_budget_Msun=(C*(t-s) if np.isfinite(t) else None),
         pair_projected_excess_Msun=mass(np.linalg.norm(pair,axis=1)*Dk).tolist(),
         shared=run(mass,u.A0,hyp=np.isinf(t)),anchored=run(mass,scl))
    # A deliberately conditional uncalibrated control: use full fitted stellar
    # inventory and the archived gravity-only xi≈1, locally normalized with R1 radius.
    RH_kpc=1000*speed/(H0*np.sqrt(-bg.OMEGA_K0)*(1+u.z0))
    S=np.sqrt(G*1000*(sps+Mh)*RH_kpc/speed**2)
    C=(sps+Mh)/S
    anchor_pred=C*full(np.array([R0,R1]),S)
    f=ep.fn('none')
    out[label]=dict(target_projected_Msun=B.tolist(),conventional_nominal_gap_mas=1e3*np.linalg.norm(f(nom,0,True)),continuations=rows,conventional_counterimages_from_A=counterimages(lambda:ep.fn('none'),nom),
      gravity_only_xi1_stress=dict(s_kpc=S,aperture_masses_Msun=anchor_pred.tolist(),fraction_of_target=(anchor_pred/B).tolist()))
(P/'jackpot_distributed_galaxy_prediction.json').write_text(json.dumps(out,indent=2)+'\n')
for name,o in out.items():
 print(name, o['target_projected_Msun'],o['gravity_only_xi1_stress'])
 for k,v in o['continuations'].items():print(k,v['transition_kpc'],v['v_flat_kms'],v['eta'],v['required_point_proxy_Msun'],v['stellar_plus_compact_enclosed_at_transition_Msun'],v['shared']['ring_rms_mas'],v['shared']['S3_gap_mas'],v['anchored']['S3_gap_mas'])
 print('S3 image roots',o['continuations']['inf']['shared']['counterimages_from_A'])

for name,o in out.items():print(name,"baseline roots",o["conventional_counterimages_from_A"])
