"""First-order R1 susceptibility at fixed stellar density. Controlled external quadrupole."""
from pathlib import Path
from contextlib import redirect_stdout
import sys,json,io
import numpy as np
from scipy.integrate import solve_ivp,quad
from scipy.interpolate import CubicSpline
P=Path(__file__).resolve().parent
sys.path[:0]=[str(P.parent/'bhsm_environment_audit'),str(P.parent/'bhsm_environment_audit'/'pinned_extra')]
from r1_background_geometry import D,cfs,G,speed,L,xrad,bg
with redirect_stdout(io.StringIO()):
    import he0435_joint_projected as h
    import s3_stellar_transfer as j
from he0435_joint_field_control import d1,w1,positions,names
he=h.Obj('sersic')
def hs(r):
    R=min(r,4.)
    M=he.mt*he.enclosed(R)
    N=he.mt*he.rho(R)*r**3/M if r<4. else 0.
    return M,N
def js(label):
    M=10**np.array(j.masses[label])*G/speed**2
    a,b=j.scales.T
    def profile(r):
        x=j.m3(r,M)
        deriv=np.sum(2*M/(np.pi*(b-a))*r*r*(1/(a*a+r*r)-1/(b*b+r*r)))
        n=deriv*r/x
        # Analytic cancellation-free limit well inside all cores.
        return x,n
    return profile
def compute(label,z,source,pts,axis,prof,n,tail):
    b,C,eps,_=cfs(z)
    T=np.linspace(np.log(1e-6),np.log(tail),n)
    def coeff(t):
        r=np.exp(t)
        m,N=prof(r)
        k=16*b*m*L*L/(bg.LAMBDA*C*C*r**3)
        return [np.sqrt(1+k),.5*(N-3)*k/(1+k)]
    CS,H=CubicSpline(T,np.array([coeff(t) for t in T]),axis=0),None
    assert np.min(1+.5*CS(T)[:,1])>.249
    def ode(t,x):
        e=CS(t)[1];q=x[0]
        return 6*(1+e/2)-q*(q+1+e),q
    u=solve_ivp(ode,[T[0],T[-1]],[2.,0.],rtol=2e-11,atol=2e-11,dense_output=True)
    v=solve_ivp(ode,[T[-1],T[0]],[-3.,0.],rtol=2e-11,atol=2e-11,dense_output=True)
    assert u.success and v.success
    dist=D(0,z);wgt=D(z,source)/D(0,source); axis=np.asarray(axis)
    assert abs(np.linalg.norm(axis)-1)<1e-10
    def run(R):
        tt=np.log(R)
        ur,vr=u.sol(tt),v.sol(tt); S=CS(tt)[0]
        amp=R*R*5/(S*(ur[0]-vr[0]))
        assert abs(S*amp*(vr[0]-ur[0])/R+5*R)<1e-12
        def grad(r):
            if r>tail:
                f=amp*np.exp(v.sol(T[-1])[1]-vr[1])*(tail/r)**3
                return f,-3*f/r,R**5/r**3,-3*R**5/r**4
            ri=np.log(r)
            if r<=R:
                q,n=u.sol(ri);ref=ur[1];g=r*r;gp=2*r
            else:
                q,n=v.sol(ri);ref=vr[1];g=R**5/r**3;gp=-3*g/r
            f=amp*np.exp(n-ref)
            return f,q*f/r,g,gp
        def bent(t):
            xy=np.asarray(t)*dist*xrad
            zz=np.sqrt(R*R-xy@xy)
            def integ(z,k,i):
                xyz=np.r_[xy,z];r=np.linalg.norm(xyz);E=xyz/r; m=axis@E
                f,fp,g,gp=grad(r)
                if i==0:f,fp=f-g,fp-gp
                else:f,fp=g,gp
                return (fp*(3*m*m-1)/2*E+3*m*f/r*(axis-m*E))[k]
            out=np.array([[sum(quad(lambda z:integ(z,k,i),l,h,epsabs=2e-12,epsrel=5e-7)[0] for l,h in [(0,zz),(zz,tail),(tail,np.inf)]) for k in [0,1]] for i in [0,1]])
            # q=1 (km/s)^2/kpc^2; projection factor 2, half LOS factor 2.
            coeff=4.*1e6*wgt/(speed**2*xrad)*1000
            return [coeff*eps*out[0],coeff*out[1]]
        dif,GR=np.moveaxis(np.array([bent(t) for t in pts]),1,0)
        pair=lambda a:np.max(np.linalg.norm(a[:,None]-a,axis=2))
        return dict(radius_kpc=R*1000,trace_response_ratio=amp/R**2,
           rays_extra_mas=dif.tolist(),rays_ordinary_tide_mas=GR.tolist(),
           extra_max_pair_mas=float(pair(dif)),ordinary_tide_max_pair_mas=float(pair(GR)))
    return dict(system=label,eps=eps,spherical_tests=[run(r) for r in [.2,.4,.8]])
points=np.array([positions[k]-positions['G'] for k in names])
cases=[('HE0435',.4546,1.693,points,np.r_[h.axis,0.],hs),('Jackpot Salpeter',j.z,j.source,j.theta,[1.,0.,0.],js('Salpeter'))]
a=[compute(*q,1300,60) for q in cases]
b=[compute(*q,780,40) for q in cases]
for r,s in zip(a,b):
    for x,y in zip(r['spherical_tests'],s['spherical_tests']):
        assert abs(x['extra_max_pair_mas']-y['extra_max_pair_mas'])<max(2e-6,1e-3*x['extra_max_pair_mas'])
        assert abs(x['ordinary_tide_max_pair_mas']-y['ordinary_tide_max_pair_mas'])<1e-6
out={'scope':'Controlled projected laboratory tide; not a physical environment model for either lens. Signed l=2 surface-density perturbation; HE uses observed axis, Jackpot an East control direction. Additional bending is scalar joint minus isolated scalar tide on frozen rays. No first-order l=0 from pure l=2 about spherical stars; unresolved interface excluded.',
     'normalization':'Newtonian interior tide q r² P2 with q=1 (km/s)^2/kpc^2. Both rays projected through entire interior and exterior; HE rear light propagation is not reapplied.', 'results':a}
(P/'controlled_tide.json').write_text(json.dumps(out,indent=2)+'\n')
for r in a:
    print(r['system'],r['eps'])
    for z in r['spherical_tests']: print({k:v for k,v in z.items() if 'rays' not in k})
