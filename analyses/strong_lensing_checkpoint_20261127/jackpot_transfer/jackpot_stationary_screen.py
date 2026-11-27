"""Stationary positive screened response candidates, not derived BHSM."""
from pathlib import Path
import json,sys
import numpy as np
from scipy.special import k0,k1
from scipy.optimize import brentq,least_squares
from scipy.integrate import quad
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'visible_mass_envelope_20261126/external_weak/jackpot_neighbor'))
import jackpot_current_geometry_holdout as gg
ep,u=gg.ep,gg.u
ep.W=gg.Ws['closed_R1']
u.get_exact=lambda t:np.zeros_like(t)
u.exact_origin=np.zeros((1,2))
base=u.basic
T=json.loads((P/'jackpot_settled_envelope_template.json').read_text())
r0,r1=T['fit_range_arcsec']; M=np.array(T['total_mass_Msun']); r3=np.linalg.norm(u.pair,axis=1)
a,b=u.scale.T
F=lambda x:1-x*k1(x)
Mh=1.6e9
# Independently integrate spherical shell fractions, with the outer integral
# remapped at the cylinder edge to avoid loss in 1-sqrt(1-b*b/r*r).
for x in [.01,.1,.5,1,2,10]:
 def tail(r):
    q=(x/r)**2
    return r*np.exp(-r)*q/(1+np.sqrt(max(0.,1-q)))
 assert np.isclose(F(x),quad(lambda r:r*np.exp(-r),0,x)[0]+quad(tail,x,np.inf,epsabs=1e-12)[0],rtol=1e-8)
# Continuous conservative bound using monotonicity of K0, K1 and F.
g=np.geomspace(.01,50,6000)
bound_mid=max((1.07*g[1:]**2*k0(g[:-1])+g[1:]**3*k1(g[:-1]))/F(g[:-1]))
bound_small=2*(1.07+1/k0(.01))
bound_large=np.exp(-50)*(1.07*50**2*np.sqrt(np.pi/100)+50**3*np.sqrt(np.pi/98))/F(50)
bound=max(bound_mid,bound_small,bound_large); assert bound<2.679
old_stars=u.stars.copy()
xgrid=np.geomspace(.001,60,2000)
results={}
for label,logm in [('Salpeter',[11.13,11.52]),('Chabrier',[10.85,11.27])]:
    u.stars=10**np.array(logm)
    z=u.stars/(b-a)
    def stars(r):
        r=np.asarray(r)[...,None]
        return np.sum(z*(np.hypot(r,a)-a-np.hypot(r,b)+b),axis=-1)
    ms=M-stars([r0,r1])-Mh
    sx=r0*r0*np.sum(z*(1/np.hypot(r0,a)-1/np.hypot(r0,b)))
    sxx=sx+r0*r0*np.sum(z*(a*a/np.hypot(r0,a)**3-b*b/np.hypot(r0,b)**3))
    Tcurv=lambda xi:-(sxx+(-3+xi/2)*sx+(2-xi)*M[0])/ms[0]
    Qratio=lambda x:F(x*r1/r0)/F(x)
    ratio=ms[1]/ms[0]
    x=brentq(lambda x:Qratio(x)-ratio,.001,40)
    single=[(r0/x,ms[0]/F(x))]
    q=ep.fit(ep.fn('none'),u.starts)
    norm_anchor=r0*r0/M[0]/ep.W[u.z0,u.z1]
    def summarize(r,params):
        return dict(ring_rms_mas=np.linalg.norm(r(params))*1e3/np.sqrt(14),
                    S3_signed_pair_mas=(r(params,0,True)*1e3).tolist(),
                    S3_splits_mas=[np.linalg.norm(r(params,s,True))*1e3 for s in (0,75,150)])
    def check(modes):
        def envmass(r):
            return sum(Q*F(r/ell) for ell,Q in modes)
        assert np.allclose(envmass(np.array([r0,r1])),ms,rtol=1e-10)
        mx=sx+sum(Q*(x:=r0/ell)**2*k0(x) for ell,Q in modes)
        mxx=sxx+sum(Q*(2*(x:=r0/ell)**2*k0(x)-x**3*k1(x)) for ell,Q in modes)
        eta=1+.5*(mxx-3*mx+2*M[0])/(M[0]-mx/2)
        assert M[0]-mx/2>0
        out=dict(modes_arcsec_Msun=modes,eta=eta,S3_effective_mass_Msun=envmass(r3).tolist(),total_residual_charge_Msun=sum(Q for ell,Q in modes))
        for name,norm in [('shared',u.A0),('anchored',norm_anchor)]:
            def field(t):
                r=np.linalg.norm(t,axis=1)
                delta=norm*(stars(r)+Mh+envmass(r))-u.A0*(stars(r)+Mh)
                return base(t)+delta[:,None]*t/r[:,None]**2
            u.basic=field
            try:r=ep.fn('none')
            finally:u.basic=base
            params=min((least_squares(lambda p:r(np.r_[0.,0.,p]),v,bounds=(u.lo[2:],u.hi[2:]),gtol=1e-11,ftol=1e-11,xtol=1e-11) for v in [q.x[2:],[.08,.08,.05],[.08,.08,.3],[0,0,.25]]),key=lambda a:a.cost).x
            out[name]=summarize(r,np.r_[0.,0.,params])
        return out
    res=dict(conventional=summarize(ep.fn('none'),q.x),one_mode=check(single),
             target_curvature_functional={str(eta):Tcurv(2*(eta-1)) for eta in (.93,.96,.98)})
    res['excluded_by_continuous_bound']=bool(max(res['target_curvature_functional'].values())<-bound)
    if label=='Chabrier':
        # Illustrative scales from stellar template, not derived couplings.
        xi=-.08
        C=lambda x:((-1+xi/2)*x*x*k0(x)-x**3*k1(x))/F(x)
        for ell in (.066,.50,6.05):
            y=r0/ell
            w=lambda x:(ratio-Qratio(x))/(Qratio(y)-Qratio(x))
            def f(x):return (1-w(x))*C(x)+w(x)*C(y)-Tcurv(xi)
            vals=f(xgrid)
            modes=[]
            for j in np.flatnonzero(vals[1:]*vals[:-1]<0):
                x=brentq(f,xgrid[j],xgrid[j+1])
                if 0<w(x)<1:
                   modes.append((r0/x,ms[0]*(1-w(x))/F(x)))
                   modes.append((ell,ms[0]*w(x)/F(y)))
            assert len(modes)==2
            out=check(modes)
            assert abs(out['eta']-.96)<1e-9
            res[f'two_modes_fixed_{ell}']=out
    results[label]=res
u.stars=old_stars
results['curvature_abs_bound']={'x_lt_0.01':bound_small,'interval_0.01_to_50':bound_mid,'x_gt_50':bound_large}
results['scope']='Static spherical optical-potential candidate only; same-potential dynamical consequences not tested. Third source did not enter mode choices, fits or normalizations. Refitted conventional controls by stellar input.'
(P/'jackpot_stationary_screen.json').write_text(json.dumps(results,indent=2)+'\n')
for name in ('Salpeter','Chabrier'):
 print(name)
 print('coefficients target=',results[name]['target_curvature_functional'],'excluded=',results[name]['excluded_by_continuous_bound'])
 print('conventional',results[name]['conventional'])
 for key,v in results[name].items():
  if isinstance(v,dict) and 'eta' in v:print(key,v['modes_arcsec_Msun'],v['eta'],v['shared']['S3_splits_mas'],v['anchored']['S3_splits_mas'])
print(results['curvature_abs_bound'])
