"""Frozen R1: distinguish thin-lens plane ordering from deformation of the leading quadrupole.
The pair's monopole and higher even modes are not included in the R1 response calculation.
"""
from contextlib import redirect_stdout
import io
with redirect_stdout(io.StringIO()):
    from controlled_tide import *
from scipy.optimize import brentq
from numpy.polynomial.legendre import leggauss

def one(label,z,src,_,axis,prof,n,tail,scale=.001,tilt_deg=45):
    b,C,eps,_=cfs(z)
    R=.4; eta=-scale*1e6/speed**2     # q/c^2: two positive neighbors, Mpc^-2.
    inc=np.deg2rad(tilt_deg)
    axis=np.r_[np.asarray(axis)[:2]*np.sin(inc),np.cos(inc)]
    xyunit=axis[:2]/np.linalg.norm(axis[:2])
    d,w=D(0,z),D(z,src)/D(0,src)
    m=-eta*R**3/2              # geometrical mass of each neighbor in Mpc
    T=np.linspace(np.log(1e-6),np.log(tail),n)
    def coeff(t):
        r=np.exp(t); M,N=prof(r); k=16*b*M*L*L/(bg.LAMBDA*C*C*r**3)
        return np.sqrt(1+k),.5*(N-3)*k/(1+k)
    S=CubicSpline(T,[coeff(t) for t in T],axis=0)
    def ode(t,x):
        s=S(t)[1]; a=x[0]; return 6*(1+s/2)-a*(a+1+s),a
    def solve(t0,t1,a):
        ans=solve_ivp(ode,[t0,t1],[a,0],rtol=2e-11,atol=2e-11,dense_output=True)
        assert ans.success
        return ans.sol
    u,v=solve(T[0],T[-1],2.),solve(T[-1],T[0],-3.)
    tR=np.log(R); ur,vr=u(tR),v(tR)
    amp=5*R*R/(S(tR)[0]*(ur[0]-vr[0]))
    assert abs(S(tR)[0]*amp*(vr[0]-ur[0])/R+5*R)<1e-12
    def radial(r):
        if r<=R: f,fp=r*r,2*r; a,k=u(np.log(r)); g=amp*np.exp(k-ur[1])
        elif r<tail: f,fp=R**5/r**3,-3*R**5/r**4; a,k=v(np.log(r)); g=amp*np.exp(k-vr[1])
        else: f,fp=R**5/r**3,-3*R**5/r**4; a=-3.; g=amp*np.exp(v(T[-1])[1]-vr[1])*(tail/r)**3
        return f,fp,g,a*g/r
    def flux(r,f,fp): return (2*fp**2/r-12*f*fp/r**2+6*f*f/r**3)/5
    assert abs(flux(.1,.01,.2)+.2)<1.e-14
    x,W=leggauss(12)
    for r in [.005,.15,.399,.401,.9]:
        f,fp,g,gp=radial(r)
        for y,yp in [(f,fp),(g,gp)]:
            avg=np.dot(W, (2*yp/r-6*y/r**2)*yp*((3*x*x-1)/2)**2
                       -(yp/r-y/r**2)*y/r*9*x*x*(1-x*x))/2
            assert np.isclose(avg,flux(r,y,yp),rtol=1e-12,atol=1e-16)
    def mono(r,s,k):
        f,fp,g,gp=radial(r)
        F=flux(r,g,gp)/(S(np.log(r))[0] if r<tail else coeff(np.log(r))[0])-flux(r,f,fp)
        pref=-b/(L*L*bg.LAMBDA*C)*(b*L*L*eta/C)**2
        return pref*F*s/r
    def lin(r,s,k,which):
        f,fp,g,gp=radial(r); g-=f;gp-=fp
        c2=axis[2]**2
        A=(3*(c2*k*k+(1-c2)*s*s/2)/r**2-1)/2
        ga=3*s*k*k*((1-c2)/2-c2)/r**4
        if which=='axis_minus_perp':
            A=1.5*(1-c2)*s*s/r**2;ga=3*(1-c2)*s*k*k/r**4
        return eps*eta*(gp*s/r*A+g*ga)
    def project(F,s):
        a=np.sqrt(R*R-s*s)
        return 4*w/xrad*1000*sum(quad(lambda l:F(np.hypot(l,s),s,l),lo,hi,
                   epsabs=1e-24,epsrel=2e-7,limit=500)[0] for lo,hi in [(0,a),(a,tail),(tail,np.inf)])
    # Thin-lens ordered-ray benchmark. Choose redshifts that give the signed
    # proper LOS offsets in this illustrative frozen background.
    dz=R*axis[2]
    zm=brentq(lambda zz:D(zz,z)-dz,z-.01,z-1e-7)
    zp=brentq(lambda zz:D(z,zz)-dz,z+1e-7,z+.01)
    zs=[zm,z,zp]; ds=[D(0,q) for q in zs]; ws=[D(q,src)/D(0,src) for q in zs]
    pos=[-R*axis[:2]/ds[0]/xrad,np.zeros(2),R*axis[:2]/ds[2]/xrad]
    def hatstar(Rp):
        v=quad(lambda t:prof(Rp/np.cos(t))[0]*np.cos(t),0,np.pi/2,epsabs=2e-17,epsrel=1e-8,limit=200)[0]
        return 4*v/(Rp*xrad)
    radii=np.linspace(.45,2.5,110)
    interp=CubicSpline(radii,[hatstar(a*d*xrad) for a in radii])
    def trace(t,include,ordered=True):
        past=[]
        for i in range(3):
            at=t.copy()
            if ordered:
                for j,a in past: at-=D(zs[j],zs[i])/ds[i]*a
            if i not in include: continue
            r=at-pos[i]; rho=np.linalg.norm(r)
            if i==1:
                val=interp(rho) if .45<=rho<=2.5 else hatstar(rho*d*xrad)
                a=val*r/rho
            else:a=4*m/(ds[i]*xrad*xrad*rho**2)*r
            past.append((i,a))
        return sum((ws[i]*a for i,a in past),np.zeros(2))
    def rings(theta):
        phis=2*np.pi*np.arange(64)/64
        e=np.c_[np.cos(phis),np.sin(phis)]
        def shifts(ordered,sel):
            return np.array([trace(theta*a,sel,ordered) for a in e])
        mixed=lambda ordered:shifts(ordered,{0,1,2})-shifts(ordered,{1})-shifts(ordered,{0,2})
        assert np.max(np.abs(mixed(False)))<2e-15
        p=(mixed(True)*e).sum(axis=1)*1000
        s=theta*d*xrad
        return dict(radius_arcsec=theta, ray_order_mean_radial_mas=float(np.mean(p)),
                    ray_order_range_radial_mas=[float(np.min(p)),float(np.max(p))],
                    tide_linear_sky_mean_mas=project(lambda *a:lin(*a,'mean'),s),
                    tide_linear_axis_minus_perp_mas=project(lambda *a:lin(*a,'axis_minus_perp'),s),
                    tide_quadratic_true_monopole_mas=project(mono,s))
    return dict(system=label,each_neighbor_mass_msun=m*speed**2/G,
                q_km2_s2_kpc2=-scale,neighbors_separation_from_main_kpc=R*1000,tilt_deg=tilt_deg,redshifts=zs,rings=[rings(t) for t in (1.,2.)])
if __name__=='__main__':
    A=[one(*q,1300,60) for q in cases]
    B=[one(*q,780,40) for q in cases]
    for x,y in zip(A,B):
        for h,k in zip(x['rings'],y['rings']):
            for p in h:
                if p.startswith('tide'):assert np.isclose(h[p],k[p],atol=2e-9,rtol=.003),(h,k)
    H=[one(*q,1300,60,.0005) for q in cases]
    for a,h in zip(A,H):
        for x,y in zip(a['rings'],h['rings']):
            for k in ['tide_linear_sky_mean_mas','tide_linear_axis_minus_perp_mas']:
                assert np.isclose(x[k],2*y[k],atol=1e-14,rtol=1e-10)
            assert np.isclose(x['tide_quadratic_true_monopole_mas'],4*y['tide_quadratic_true_monopole_mas'],atol=1e-14,rtol=1e-10)
    out={'scope':'Illustrative symmetric point masses/order benchmark vs leading quadrupole-only frozen R1 terrain derivative, not full actual environment. Signs are inward-positive for reduced radial deflection. True monopole is only the second-order spherical-average contribution from the quadrupole squared, not total second-order projected signal. Source, halo and coupling never refit.',
         'results':A}
    data=json.dumps(out,indent=2)+'\n'
    (P/'symmetric_neighbors.json').write_text(data)
    print(data)
