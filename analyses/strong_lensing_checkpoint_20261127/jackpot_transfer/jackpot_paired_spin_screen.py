"""Fixed-ray factorial test of a conditional shared-surface optical response."""
from jackpot_annular_tide import *
from scipy.integrate import quad
from itertools import product

# Equal-width normalized regular-surface perturbations, one at center and one
# at projected inter-ring midpoint on the axis from the early-only tide fit.
# These are hypothetical locations and equal induced profiles, not objects
# identified in the real galaxy or a derived spin -> surface coupling.
g=np.array(json.loads((P/'jackpot_annular_tide.json').read_text())['variants']['whole_band']['both']['g'])
theta=.5*np.arctan2(g[1],g[0])
axis=np.array([np.cos(theta),np.sin(theta)])
early=np.vstack(u.observed[:5])
mid=(r0+r1)/2
cent=[np.zeros(2),mid*axis]
L=mid
def screen(t,at):
    d=t-at
    return d/L**2*np.exp(-np.sum(d*d,axis=1)[:,None]/L**2)
def mass_part(t):
    r=np.linalg.norm(t,axis=1)
    return (u.A0*radial(r*dk)/r**2)[:,None]*t
m=(cent[0]+cent[1])/2
overlap=np.exp(-np.linalg.norm(cent[1]-cent[0])**2/(4*L**2))
def terms(t):
    return screen(t,cent[0]),screen(t,cent[1]),2*overlap*screen(t,m)
def ddz(t,z,at):
    return -z/L**2*np.exp(-(np.sum((t-at)**2)+z*z)/(2*L**2))
# Independent finite differences of line-of-sight cross potential, including sign.
for t in ([.8,.4],[-3,1.2],list(m)):
    t=np.asarray(t)
    def delay(z):
        return quad(lambda los:ddz(z,los,cent[0])*ddz(z,los,cent[1]),-np.inf,np.inf)[0]
    num=np.array([-(delay(t+v*1e-4)-delay(t-v*1e-4))/2e-4 for v in np.eye(2)])
    assert np.allclose(num,(np.sqrt(np.pi)/(2*L))*terms(t[None])[2][0],rtol=1e-8,atol=1e-10)
states=list(product((-1,1),repeat=2))
def for_sign(t,s1,s2,include_cross):
    u1,u2,cross=terms(t)
    # Simulated individual sign-odd deflections supplied as a deliberately
    # nonzero additive fixture. Their detailed template is irrelevant to
    # factorial cancellation. Shared optical terms are quadratic.
    add=.03*(s1*u1+s2*u2)+u1+u2
    return add+s1*s2*cross if include_cross else add
fixed=np.vstack([early,pair])
def factorial(t,shared):
    return sum(i*j*for_sign(t,i,j,shared) for i,j in states)/4
assert np.allclose(factorial(fixed,False),0,atol=1e-14)
assert np.allclose(factorial(fixed,True),terms(fixed)[2],atol=1e-14)
# Test the isolated interaction, not a sum that would double-count the existing
# background. Normalize hypothetical spin-induced self-bending to 10% of
# earlier static excess at early knots, fixed before the held-out comparison.
self_u=tuple(terms(early))[:2]
scale=.10*np.linalg.norm(mass_part(early))/np.linalg.norm(self_u[0]+self_u[1])
def interaction(t,balanced):
    raw=terms(t)[2]
    if not balanced:return raw
    r=np.linalg.norm(t,axis=1)
    ang=np.arange(96)*2*np.pi/96
    directions=np.column_stack([np.cos(ang),np.sin(ang)])
    other=r[:,None,None]*directions
    shells=terms(other.reshape(-1,2))[2].reshape(len(t),-1,2)
    circular=np.einsum('nki,ki->nk',shells,directions).mean(axis=1)
    return raw-circular[:,None]*t/r[:,None]
for r in (r0,r1):
    ang=np.arange(96)*np.pi/48
    dirs=np.column_stack([np.cos(ang),np.sin(ang)])
    assert abs(np.einsum('ij,ij->i',interaction(r*dirs,True),dirs).mean())<1e-13
def run_sign(sign,balanced=False,factor=1.,before=None):
    def build():
        u.basic=lambda t:basic(t)+mass_part(t)+sign*scale*factor*interaction(t,balanced)
        try:return ep.fn('none')
        finally:u.basic=basic
    f=build()
    sol=min((least_squares(lambda p:f(np.r_[0,0,p]),seed,bounds=(u.lo[2:],u.hi[2:]),ftol=1e-11,xtol=1e-11,gtol=1e-11)
        for seed in [base[2:],[.08,.08,.3],[0,0,.05]]),key=lambda z:z.cost)
    z=np.r_[0,0,sol.x]
    def trace(params):
        def F(t):
            u.pair=np.vstack([pair[0],t])
            try:return build()(params,0,True)
            finally:u.pair=pair
        seed=np.array([1.,.75] if before is None else before['B'])
        rr=root(F,seed)
        if rr.success and np.linalg.norm(F(rr.x))<1e-7:return rr.x
        return None
    result=trace(z)
    fixed_param=trace(np.array(before['params'])) if before else result
    return dict(early_rms_mas=1000*np.linalg.norm(f(z))/np.sqrt(14),params=z.tolist(),
            B=result.tolist() if result is not None else None,
            B_error_mas=1000*np.linalg.norm(result-pair[1]) if result is not None else None,
            delta_after_ring_fit_mas=1000*np.linalg.norm(result-before['B']) if before and result is not None else None,
            delta_before_ring_fit_mas=1000*np.linalg.norm(fixed_param-before['B']) if before and fixed_param is not None else None)
baseline=run_sign(0)
assert abs(baseline['B_error_mas']-345.834)<.01
rows={'without_pair_term':baseline}
for norm,factor in [('3percent',.3),('10percent',1.)]:
    for name,bal in [('full_cross',False),('circular_mean_removed',True)]:
        rows[norm+'_'+name]={k:run_sign(v,bal,factor,baseline)
                            for k,v in [('coordinated',1),('counterrotating',-1)]}
out=dict(separation_arcsec=mid,width_arcsec=L,same_depth_overlap=float(overlap),
    main_plane_pair_half_difference_at_A_B_mas=(1000*np.linalg.norm(scale*factorial(pair,True),axis=1)).tolist(),
    source3_reduced_pair_bend_at_A_B_mas=(1000*ep.W[u.z0,u.z3]*np.linalg.norm(scale*factorial(pair,True),axis=1)).tolist(),
    baseline_relative_self_bend_rms=.10,rows=rows)
(P/'jackpot_paired_spin_screen.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
