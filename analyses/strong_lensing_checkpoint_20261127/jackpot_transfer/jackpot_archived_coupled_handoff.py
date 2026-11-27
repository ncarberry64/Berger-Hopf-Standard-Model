"""Conditional linked archive test: §9 onset and strength share the same enclosed mass.
No third-source evaluation until after checking the inner shape."""
from jackpot_response_tools import *
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import k0
from r1_background_geometry import H0,speed,G,bg
RH=1000*speed/(H0*np.sqrt(-bg.OMEGA_K0)*(1+u.z0))
R=np.array([r0,r1])*dk
A,T=a*dk,b*dk
def enclosed(s):
    return Mh+np.sum((2/np.pi)*u.stars/(T-A)*(T*np.arctan(s/T)-A*np.arctan(s/A)))
def col(R,s):
    R=np.asarray(R)
    x=np.minimum(1,R/s)
    # Algebraically equivalent to R asin(x)-s+sqrt(s²-R²); avoids cancellation.
    return R*np.arcsin(x)-s*x*x/(1+np.sqrt(1-x*x))
def flow(R,s,t):
    C=enclosed(s)/s
    return C*(col(R,s)-(col(R,t) if np.isfinite(t) else 0))
def xi(s):
    return G*1000*enclosed(s)*RH/(speed**2*s*s)
for s,t,X in [(4,50,5),(22,100,13),(2,np.inf,8),(22,np.inf,5)]:
    def cap(r):
        f=min(1,(X/r)**2);return f/(1+np.sqrt(1-f))
    m=quad(cap,s,t,points=[X] if s<X<t and np.isfinite(t) else None)[0] if not(s<X<t and np.isinf(t)) else X-s+quad(cap,X,t)[0]
    assert np.isclose(flow(X,s,t),enclosed(s)/s*m,rtol=2e-9)
def scanroots(fn, grid):
    ys=[fn(x) for x in grid]
    return [brentq(fn,a,b,xtol=1e-11) for a,b,y,z in zip(grid[:-1],grid[1:],ys[:-1],ys[1:]) if y*z<0]
assert np.all(np.diff(R)>0)
def anchor(s,t):
    Q=target-flow(R,s,t)
    if min(Q)<=0:return None
    def rank(L):
        m=mass(R,0,L);return Q[0]*m[1]/m[0]-Q[1]
    lo,hi=.01,1e4
    if rank(lo)*rank(hi)>=0:return None
    L=brentq(rank,lo,hi)
    q=Q[0]/mass(R[0],0,L)
    def profile(X):return flow(X,s,t)+q*mass(X,0,L)
    X=R[0]
    z=r0
    w=u.stars/(b-a)
    stellar_d=z*z*np.sum(w*(1/np.hypot(z,a)-1/np.hypot(z,b)))
    stellar_dd=stellar_d+z*z*np.sum(w*(a*a/np.hypot(z,a)**3-b*b/np.hypot(z,b)**3))
    def dm(t):
        if X>=t:return np.array([X*np.pi/2,X*np.pi/2])
        d=np.arcsin(X/t)
        return np.array([X*d,X*d+X*X/np.sqrt((t-X)*(t+X))])
    C=enclosed(s)/s
    dflow=C*(dm(s)-(dm(t) if np.isfinite(t) else np.zeros(2)))
    x=X/L
    dpin=q*np.array([x*x*k0(x),x*x*(2*k0(x)-x*k1(x))])
    dx,dxx=np.array([stellar_d,stellar_dd])+dflow+dpin
    m0=M0
    eta=1+.5*(dxx-3*dx+2*m0)/(m0-.5*dx)
    assert np.allclose(profile(R),target,rtol=1e-10)
    return eta,L,q,profile
out={}
for tag,Ms in [('Salpeter',[11.13,11.52]),('Chabrier',[10.85,11.27])]:
    # Shared projection helpers resolve the same global mass array in place.
    u.stars[:]=10**np.array(Ms)
    target[:]=np.array([M0,M1])-np.array([stars(x) for x in (r0,r1)])-Mh
    ths=scanroots(lambda s:xi(s)-1,np.geomspace(.01,100,400))
    row={}
    for t in (20.,50.,100.,np.inf):
        g=np.unique(np.r_[np.geomspace(.015,min(70.,t*.999),1500),R*(1-2e-4),R*(1+2e-4)])
        zero=[]
        rs=[(s,anchor(s,t)) for s in g if s<t]
        admiss=[(s,a) for s,a in rs if a is not None and abs(np.log(s/R[0]))>2e-4]
        def eq(s):return anchor(s,t)[0]-.96
        for (s,va),(z,vb) in zip(rs[:-1],rs[1:]):
            if va is None or vb is None or (s<R[0]<z) or (va[0]-.96)*(vb[0]-.96)>=0:continue
            x=brentq(eq,s,z,xtol=1e-9)
            assert abs(eq(x))<1e-5
            zero.append(x)
        def result(s,predict_B=False):
            v=anchor(s,t)
            if v is None:return dict(s=s,xi=xi(s),admissible=False)
            e,L,q,profile=v
            if predict_B:
                hold=predict(profile)
                assert abs(hold['eta']-e)<2e-5
            return dict(s=s,xi=xi(s),eta=e,L=L,q=q,flow_fraction=(flow(R,s,t)/target).tolist(),**(dict(held_out=hold) if predict_B else {}))
        row[str(t)]=dict(min_s_kpc=float(g[0]),max_s_kpc=float(g[-1]),slope_range=[min(a[0] for _,a in admiss),max(a[0] for _,a in admiss)],
                       gravity_only=[result(s) for s in ths if s<t],
                       slope_calibrated=[result(s,True) for s in zero])
    out[tag]=row
(P/'jackpot_archived_coupled_handoff.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
