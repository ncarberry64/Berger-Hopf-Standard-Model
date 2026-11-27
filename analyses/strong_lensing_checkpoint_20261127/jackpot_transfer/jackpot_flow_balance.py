"""Continuity-driven annular sensitivity with fixed optical closure and no B fit."""
from jackpot_annular_tide import *
a0,b0=bounds
def integrate(l,h,f):
    l,h=np.asarray(l),np.asarray(h)
    return (h-l)*np.sum(w*f(l[...,None]+(h-l)[...,None]*x),axis=-1)
def deriv(r):return dk*radial(r*dk,1)
def bump(r):
    z=(r-a0)/(b0-a0)
    return 16*z*z*(1-z)**2
def shoulders(r):return bump(r)*(2*(r-a0)/(b0-a0)-1)**2
bal=integrate(a0,b0,lambda r:deriv(r)*bump(r))/integrate(a0,b0,lambda r:deriv(r)*shoulders(r))
def h(r):return bump(r)-bal*shoulders(r)
assert abs(integrate(a0,b0,lambda r:deriv(r)*h(r)))<.1
g0=np.array(json.loads((P/'jackpot_annular_tide.json').read_text())['variants']['whole_band']['both']['g'])
g0/=np.linalg.norm(g0)
# Orientation fixed from previous first-two-source fit only. This is a prior
# direction sensitivity, not a measurement of a flow direction.
def alpha_q(t,d,eps):
    r=np.linalg.norm(t,axis=1)
    edge=np.clip(r,a0,b0)
    DM=d*integrate(np.full_like(r,a0),edge,lambda r:deriv(r)*h(r))
    if eps==0:return (u.A0*DM/r**2)[:,None]*t
    # A fixed optical bridge: projected storage times one common response
    # corresponds to radial mass derivative, with a coherent quadrupole.
    def kap(s):return u.A0*d*eps*deriv(s)*bump(s)/(2*s)
    I=integrate(np.full_like(r,a0),edge,lambda s:kap(s)*s**3)
    O=integrate(edge,np.full_like(r,b0),lambda s:kap(s)/s)
    psi=-.5*(I/r**2+r*r*O)
    psir=I/r**3-r*O
    er=t/r[:,None]; et=er[:,::-1]*[-1.,1.]
    C=er[:,0]**2-er[:,1]**2; S=2*er[:,0]*er[:,1]
    return ((u.A0*DM/r+psir*(C*g0[0]+S*g0[1]))[:,None]*er
            +(2*psi/r*(-S*g0[0]+C*g0[1]))[:,None]*et)
def run_balance(d,eps):
    r=np.linspace(a0,b0,250)
    ref=deriv(r)
    assert min(ref)>0
    L=1+d*(h(r)[:,None]+eps*bump(r)[:,None]*np.array([-1,1]))
    assert L.min()>0
    # Unit inward flux per angle. In arbitrary transport units, storage per
    # radial length is deriv(r)*L and speed is its inverse.
    assert np.allclose((ref[:,None]*L)*(1/(ref[:,None]*L)),1)
    def build():
        def bplus(t):
            r=np.linalg.norm(t,axis=1)
            return basic(t)+(u.A0*radial(r*dk)/r**2)[:,None]*t+alpha_q(t,d,eps)
        u.basic=bplus
        try:return ep.fn('none')
        finally:u.basic=basic
    f=build()
    lo,hi=u.lo[2:],u.hi[2:]
    sol=min((least_squares(lambda p:f(np.r_[0,0,p]),seed,bounds=(lo,hi),ftol=1e-11,xtol=1e-11,gtol=1e-11)
             for seed in (base[2:],[.08,.08,.3])),key=lambda z:z.cost)
    p=np.r_[0,0,sol.x]
    def F(t):
        u.pair=np.vstack([pair[0],t])
        try:return build()(p,0,True)
        finally:u.pair=pair
    rr=root(F,[1.,.75])
    assert rr.success and np.linalg.norm(F(rr.x))<1e-7
    return dict(contrast=d,quadrupole_fraction=eps,
        central_speed_relative_to_no_choke_along_reference_and_perpendicular_axes=[1/(1+d*(1+eps)),1/(1+d*(1-eps))],
        maximum_multiplier=float(L.max()),minimum_multiplier=float(L.min()),
        early_RMS_mas=1000*np.linalg.norm(f(p))/np.sqrt(14),B=rr.x.tolist(),
        B_error_mas=1000*np.linalg.norm(rr.x-pair[1]))
rows=[run_balance(0,0)]+[run_balance(d,e) for d in (.25,.5,.75) for e in (0,.5,-.5)]
assert abs(rows[0]['B_error_mas']-345.834)<.01
assert np.linalg.norm(alpha_q(pair,.75,0))<1e-11 # both observed rays outside the compensated band
(P/'jackpot_flow_balance.json').write_text(json.dumps(rows,indent=2)+'\n')
for r in rows:print(r)
