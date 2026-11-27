"""Second-order induced metric control; no independent dark halo added."""
from jackpot_response_tools import *
from scipy.integrate import quad
from scipy.special import roots_legendre
from r1_background_geometry import G,speed
GG=1000*G
R=np.array([r0,r1])*dk
# Projection M_eq=(c^2/4G) R integral_0^(pi/2) [w'(R sec(theta))]^2 dtheta.
x,w=roots_legendre(128)
theta=(x+1)*np.pi/4
weights=w*np.pi/4
def mquad(radius,df):
    rr=np.asarray(radius)
    return speed**2/(4*GG)*rr*np.sum(weights*df(rr[...,None]/np.cos(theta))**2,axis=-1)
def mp(r,L,A):
    return np.sqrt(np.pi)*speed**2/(8*GG)*A*A*r*r/L**3*np.exp(-(r/L)**2)
for rr,L,A in [(5,7,.05),(7,15,.1),(13,12,.2)]:
    df=lambda s:-A*s/L**2*np.exp(-.5*(s/L)**2)
    assert np.isclose(mquad(rr,df),mp(rr,L,A),rtol=1e-12)
    def delay(b):return .5*quad(lambda z:(df(np.hypot(b,z))*z/np.hypot(b,z))**2,-np.inf,np.inf,epsabs=1e-15)[0]
    Imp=-(delay(rr+1e-4)-delay(rr-1e-4))/2e-4
    assert np.isclose(mp(rr,L,A),speed**2/(4*GG)*rr*Imp,rtol=3e-9)
# Archived positive -Delta+ell²Delta² Green point profile. Its slope magnitude
# decreases because -w'=q integral_0^(1/ell) t exp(-rt) dt.
def dw(r,L):
    s=r/L
    a=np.where(s<.01,s*s*(.5-s/3+s*s/8-s**3/30),-np.expm1(-s)-s*np.exp(-s))
    return -a/r**2
grid=np.geomspace(.05,1000,101)
ratios=np.array([mquad(R,lambda r:dw(r,L)) for L in grid])
ratios=ratios[:,1]/ratios[:,0]
assert np.all(ratios < R[1]/R[0])
out={}
for tag, logs in [('Salpeter',[11.13,11.52]),('Chabrier',[10.85,11.27])]:
    u.stars[:]=10**np.array(logs)
    target[:]=np.array([M0,M1])-np.array([stars(r0),stars(r1)])-Mh
    required=target[1]/target[0]
    assert R[1]/R[0]<required<(R[1]/R[0])**2
    L=np.sqrt((R[1]**2-R[0]**2)/np.log((R[1]/R[0])**2/required))
    A=np.sqrt(target[0]/mp(R[0],L,1.))
    profile=lambda r:mp(r,L,A)
    assert np.allclose(profile(R),target,rtol=1e-12)
    out[tag]=dict(required_ratio=required,point_graph_strict_upper_bound=R[1]/R[0],
        point_graph_scan_max=float(ratios.max()), gaussian_width_kpc=L,gaussian_peak_kpc=A,
        gradient_max=A/L*np.exp(-.5),optical_mass_peak_kpc=L,
        excess_Msun=target.tolist(), **predict(profile))
(P/'jackpot_quadratic_embedding.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
