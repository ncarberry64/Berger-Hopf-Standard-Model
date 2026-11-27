"""Fixed-mass scalar spin-energy tests, not a derived BHSM spin law."""
from jackpot_response_tools import *
from jackpot_settled_distributed_graph import optics
from scipy.interpolate import CubicSpline

R=np.array([r0,r1])*dk
u.stars[:]=10**np.array([10.85,11.27])
target[:]=np.array([M0-stars(r0)-Mh,M1-stars(r1)-Mh])
saved=json.loads((P/'jackpot_settled_distributed_graph.json').read_text())['Chabrier']['solutions']['total_above_ordinary']['held_out']
ell0=saved['ell']; p0=saved['p']; s0=saved['s']
assert np.allclose(np.array(saved['c']),[p0*p0,2*p0*s0,s0*s0])
def erot(chi):return 1-np.sqrt((1+np.sqrt(1-chi**2))/2)
def profile(e,mode):
    ell,p,s=ell0,p0,s0
    if mode=='same_optical_shape':
        q=(1+e)*np.array(saved['c'])
    else:
        if mode=='pin_strength':p*=1+e
        elif mode=='operator_reach':ell*=np.sqrt(1+e)
        elif mode=='tension_softening':
            ell*=np.sqrt(1+e)
            p*=1+e
            s*=1+e

        else:raise ValueError(mode)
        q=np.array([p*p,2*p*s,s*s])
    return ell,q
def trace(ell,q):
    grid=np.geomspace(.02,35,450)
    mass=np.concatenate([optics(g,ell)@q for g in np.array_split(grid,30)])
    opt=CubicSpline(grid,mass)
    def build():
        def bplus(t):
            r=np.linalg.norm(t,axis=1)
            assert np.min(r*dk)>.02 and np.max(r*dk)<35
            return basic(t)+(u.A0*opt(r*dk)/r**2)[:,None]*t
        u.basic=bplus
        try:return ep.fn('none')
        finally:u.basic=basic
    f=build()
    sol=min((least_squares(lambda p:f(np.r_[0,0,p]),q,bounds=(u.lo[2:],u.hi[2:]),ftol=1e-11,xtol=1e-11,gtol=1e-11)
        for q in (base[2:],[.08,.08,.3],[0,0,.05])),key=lambda s:s.cost)
    x=np.r_[0,0,sol.x]
    pair=u.pair.copy()
    def F(t):
        u.pair=np.vstack([pair[0],t])
        try:return build()(x,0,True)
        finally:u.pair=pair
    b=root(F,[1.,.75])
    good=b.success and np.linalg.norm(F(b.x))<1e-7
    return dict(B=b.x.tolist() if good else None,
        B_error_mas=float(1000*np.linalg.norm(b.x-pair[1])) if good else None,
        inner_rms_mas=float(1000*np.linalg.norm(sol.fun)/np.sqrt(14)))
baseline=trace(*profile(0,'pin_strength'))
assert np.linalg.norm(np.array(baseline['B'])-saved['forward']['B_pred'])<1e-6
out={}
for mode in ['same_optical_shape','pin_strength','operator_reach','tension_softening']:
    out[mode]={}
    for chi in (0.,.5,.9,1.):
        e=erot(chi); ell,q=profile(e,mode)
        ellneg,qneg=profile(erot(-chi),mode)
        assert ell==ellneg and np.array_equal(q,qneg)
        m=optics(R,ell)@q
        rec=dict(ell_kpc=ell,fractional_aperture_changes=(m/target-1).tolist(),
            ratio_change_fraction=(m[1]/m[0]/(target[1]/target[0])-1),
            rotational_fraction=e)
        if chi==1.:
            raw=trace(ell,q)
            rec['forecast_fixed_force']=raw
            rec['raw_B_shift_mas']=1000*np.linalg.norm(np.array(raw['B'])-baseline['B']) if raw['B'] else None
            # Explicit first-aperture normalization separates size from strength.
            unit=trace(ell,q*target[0]/m[0])
            rec['forecast_first_aperture_renormalized']=unit
            rec['renormalized_B_shift_mas']=1000*np.linalg.norm(np.array(unit['B'])-baseline['B']) if unit['B'] else None
        out[mode][str(chi)]=rec
assert abs(out['same_optical_shape']['1.0']['ratio_change_fraction'])<1e-12
assert out['same_optical_shape']['1.0']['renormalized_B_shift_mas']<1e-5
(P/'jackpot_spin_envelope_sensitivity.json').write_text(json.dumps(dict(baseline=baseline,models=out),indent=2)+'\n')
for m,a in out.items():print(m,a['1.0'],flush=True)
