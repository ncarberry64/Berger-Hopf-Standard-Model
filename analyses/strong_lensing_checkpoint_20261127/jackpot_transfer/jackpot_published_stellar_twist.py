"""Conventional deflection of the published two-component HST light distribution."""
from jackpot_response_tools import *
from scipy.special import roots_legendre

# Sonnenfeld et al. (2012), Table 3; geometric-mean radii already in u.scale.
q0=[.66,.71]; PA0=[63.,-24.3]
ang=np.arange(256)*2*np.pi/256
nodes,weights=roots_legendre(256)
# Let integration variable u=t² to resolve the central core layer.
t=(nodes+1)/2; w=weights/2
def component(x, j,q,pa,matched):
    A,T=u.scale[j]
    r=np.linalg.norm(x,axis=1)
    a0=np.deg2rad(pa)
    R=np.array([[np.sin(a0),np.cos(a0)],[np.cos(a0),-np.sin(a0)]])
    X,Y=(x@R.T).T
    d=1-(1-q*q)*t*t
    rho=np.sqrt(q*t*t*(X[:,None]**2+Y[:,None]**2/d))
    k=(1/np.hypot(rho,A)-1/np.hypot(rho,T))*u.A0*u.stars[j]/(2*(T-A))
    alpha=(np.column_stack([q*X*np.sum(w*2*t*k/np.sqrt(d),axis=1),
                            q*Y*np.sum(w*2*t*k/d**1.5,axis=1)]))@R
    def shell(ss):
        r2=r[:,None]*np.sqrt(ss)
        return ((np.hypot(r2,A)-A-np.hypot(r2,T)+T)/ss).mean(axis=-1)*u.stars[j]/(T-A)
    circular=shell(np.array([1.]))
    if matched:
        ellipse_avg=shell(q*np.cos(ang)**2+np.sin(ang)**2/q)
        subtract=ellipse_avg
    else:subtract=circular
    return alpha-(u.A0*subtract/r**2)[:,None]*x
test=np.array([[1.,2.],[1.1,.9],[-3,-1.]])
assert np.max(abs(component(test,0,1,31,False)))<1e-10
for j in (0,1):
    ring=2*np.column_stack([np.cos(ang),np.sin(ang)])
    assert abs(np.mean(np.einsum('ij,ij->i',component(ring,j,q0[j],PA0[j],True),ring/2)))<1e-10
def option(label):
    pair=u.pair.copy()
    # Only source 1 and 2 knots enter the five-parameter conventional fit.
    def build():
        def bplus(pts):
            if label=='circular':return basic(pts)
            pa=PA0 if label!='aligned_matched' else [PA0[1]]*2
            return basic(pts)+sum(component(pts,j,q0[j],pa[j],label!='twisted_full') for j in (0,1))
        u.basic=bplus
        try:return ep.fn('none')
        finally:u.basic=basic
    f=build()
    sol=ep.fit(f,u.starts)
    def F(y):
        u.pair=np.vstack([pair[0],y])
        try:return build()(sol.x,0,True)
        finally:u.pair=pair
    r=root(F,[1,.75])
    valid=r.success and np.linalg.norm(F(r.x))<1e-7
    return dict(early_rms_mas=float(np.linalg.norm(sol.fun)*1000/np.sqrt(14)),
                source3_gap_mas=float(np.linalg.norm(f(sol.x,0,True))*1000),
                B_error_mas=float(np.linalg.norm(r.x-pair[1])*1000) if valid else None,
                B=r.x.tolist() if valid else None,params=sol.x.tolist())
out={}
for name,logs in [('Salpeter',[11.13,11.52]),('Chabrier',[10.85,11.27])]:
    u.stars[:]=10**np.array(logs)
    out[name]={label:option(label) for label in ('circular','aligned_matched','twisted_matched','twisted_full')}
    for k,x in out[name].items():print(name,k,x,flush=True)
assert abs(out['Chabrier']['circular']['B_error_mas']-37.57)<.15
(P/'jackpot_published_stellar_twist.json').write_text(json.dumps(out,indent=2)+'\n')
