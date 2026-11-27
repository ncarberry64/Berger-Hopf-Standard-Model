"""Candidate curvature-normalized displacement law. No optical amplitudes fitted."""
from pathlib import Path
from contextlib import redirect_stdout
import sys,json,io
import numpy as np
from scipy.integrate import quad
from scipy.interpolate import PchipInterpolator,RegularGridInterpolator
from scipy.fft import rfft2,irfft2,fftfreq,rfftfreq
P=Path(__file__).resolve().parent
sys.path[:0]=[str(P.parent/'bhsm_environment_audit'),str(P.parent/'bhsm_environment_audit'/'pinned_extra')]
from r1_background_geometry import D,G,speed,xrad,bg,L
with redirect_stdout(io.StringIO()):
    import he0435_joint_projected as jp
    import s3_stellar_transfer as j
from he0435_joint_field_control import d1,d2,d12,w1,w2,theta_g,g_photo,positions,names
RH0=L/np.sqrt(-bg.OMEGA_K0)
def a0(z):return speed**2*(1+z)/RH0
def gain(g,a):
    # Stable evaluation of sqrt((1+sqrt(1+4/y^2))/2)-1.
    g=np.asarray(g); z=np.divide(a,g,out=np.zeros_like(g),where=g>0)
    u=2*z*z/(np.hypot(1.,2*z)+1)
    return u/(1+np.sqrt(1+u))
def extra(g,a):return g*gain(g,a)
for y in (1e-10,1e-12): assert abs(extra(y,1)/np.sqrt(y)-1)<3e-5
assert abs(extra(1e5,1)/(0.5e-5)-1)<1e-8
def radial(t,mfun,z,cut=np.inf,law=extra):
    t=np.asarray(t)
    norm=np.linalg.norm(t)
    if not norm:return t
    R=D(0,z)*xrad*norm
    f=lambda th:law(speed**2*mfun(R/np.cos(th))/(R/np.cos(th))**2,a0(z))*R/np.cos(th)
    lim=np.pi/2 if np.isinf(cut) else np.arctan(cut/R)
    A=4*quad(f,0,lim,epsabs=1e-6,epsrel=2e-8,limit=400)[0]/(speed**2*xrad)
    return A*t/norm
# Point-mass angular-deflection ceiling for these specific isolated, radial fields.
def ceiling(m,z):return 2*np.pi*np.sqrt(a0(z)*m*speed**2)/(speed**2*xrad)
# Verify far-out point mass limit and response reference.
mt=1e-8
ref=radial(np.array([1500000.,0.]),lambda r:mt,.222)[0]
assert abs(ref/ceiling(mt,.222)-1)<1e-4
jac={}
for name,logm in j.masses.items():
    m=10**np.array(logm)*G/speed**2
    base=np.array([j.ray(t,m)[0] for t in j.theta])
    corr=np.array([j.weight*radial(t,lambda r:j.m3(r,m),j.z) for t in j.theta])
    diff=lambda p:p[0]-p[1]
    norm=np.linalg.norm
    need=diff(j.theta-base)
    v=diff(corr)
    jac[name]=dict(bare_rays_arcsec=norm(need),added_pair_bending_arcsec=norm(v),
        new_pair_gap_arcsec=norm(need-v),direction_cosine=float(need@v/(norm(need)*norm(v))),
        point_mass_per_ray_ceiling_arcsec=j.weight*ceiling(sum(m),j.z),
        radial_class_extra_pair_upper_arcsec=float(sum(j.weight*np.linalg.norm(radial(t,lambda r:j.m3(r,m),j.z,law=lambda g,a:np.sqrt(a*g))) for t in j.theta)),
        
        conditional_floor_after_intermediate_SIS_arcsec=max(0.,norm(need-v)-j.s1_bound-j.s2_bound))
# HE0435: add fields first. Split correction into two independently projected
# spherical pieces plus the projected longitudinal non-additivity, so coarse
# grid cancellation cannot replace the central stellar response.
for row in jac.values():
    row['radial_class_floor_after_intermediate_SIS_arcsec']=max(0.,row['bare_rays_arcsec']-row['radial_class_extra_pair_upper_arcsec']-j.s1_bound-j.s2_bound)
    assert row['radial_class_floor_after_intermediate_SIS_arcsec']>0
s=jp.Obj('sersic'); e=jp.Agroup; group=jp.axis*67.1
z=.4546
target=np.vstack([[positions[i]-positions['G'] for i in names],theta_g/xrad])
def primary(t):
    R=np.linalg.norm(t)*d1*xrad
    def integ(th):
        c=np.cos(th); si=np.sin(th)
        return s.rho(min(R/c,4.))*R**3*si/(c*c*(1+si))
    return 4*s.mt*(s.enclosed(R)+quad(integ,0,np.pi/2,epsabs=2e-9,epsrel=1e-7)[0])/(R*xrad)*t/np.linalg.norm(t)
def groupgr(t):
    dt=t-group; R=np.linalg.norm(dt)*d1*xrad
    a,b=.025,jp.r200
    M=np.pi*jp.gamma/2*R**2*(1/(np.hypot(a,R)+a)-1/(np.hypot(b,R)+b))
    return 4*M/(R*xrad)*dt/np.linalg.norm(dt)
base=np.array([primary(t)+groupgr(t) for t in target])
def trace(alpha):
    ba=[]
    for t,a in zip(target[:-1],alpha[:-1]):
        imp=xrad*(d2*(t-target[-1])-d12*(a-alpha[-1]))
        h,_=g_photo.apply(imp,False)
        ba.append(t-w1*a-w2*h/xrad)
    return np.array(ba)
pair=lambda a:float(np.max(np.linalg.norm(a[:,None]-a,axis=-1)))
rms=lambda a:float(np.sqrt(np.mean(np.sum((a-a.mean(axis=0))**2,axis=1))))
base_b=trace(base)
assert abs(rms(base_b)-.8988788685852)<3e-6
def integrated_nonadd(n,box,los,nz):
    pg=np.arange(n)*2*box/n-box
    X,Y=np.meshgrid(pg,pg,indexing='ij'); E=X-jp.sep*jp.axis[0]; F=Y-jp.sep*jp.axis[1]
    a=X*X+Y*Y; b=E*E+F*F
    t,w=np.polynomial.legendre.leggauss(nz)
    Hmax=np.arcsinh(los/.012)
    T=.5*Hmax*(t+1)
    heaps=np.zeros((2,n,n))
    for l,ww in zip(.012*np.sinh(T),w*.5*Hmax*.012*np.cosh(T)):
        r=np.sqrt(a+l*l); q=np.sqrt(b+l*l)
        A=speed**2*s.mass(r)/r**3
        B=speed**2*e.mass(q)/q**3
        u,v=X*A,Y*A
        h,k=E*B,F*B
        gain_a=gain(A*r,a0(z)); gain_b=gain(B*q,a0(z))
        gain_tot=gain(np.sqrt((u+h)**2+(v+k)**2+((A+B)*l)**2),a0(z))
        heaps[0]+=ww*((gain_tot-gain_a)*u+(gain_tot-gain_b)*h)
        heaps[1]+=ww*((gain_tot-gain_a)*v+(gain_tot-gain_b)*k)
    heaps*=4/(speed**2*xrad)
    # Longitudinal xy projection of slab-integrated correction. Ends treated
    # only by convergence and isolated-ray controls; not a global S3 solver.
    kx=fftfreq(n)[:,None]; ky=rfftfreq(n)[None,:]
    denom=kx*kx+ky*ky; denom[0,0]=1
    pot=(kx*rfft2(heaps[0])+ky*rfft2(heaps[1]))/denom
    return np.column_stack([RegularGridInterpolator((pg,pg),irfft2(k*pot,s=(n,n)),method='linear')(target*(d1*xrad)) for k in (kx,ky)])
def rec(n,box,los,nz):
    S=np.array([radial(t,s.mass,z) for t in target])
    E=np.array([radial(t-group,e.mass,z) for t in target])
    F=integrated_nonadd(n,box,los,nz)
    exact=trace(base+S+E+F)
    return dict(n=n,box_Mpc=box,los_Mpc=los,nz=nz,stellar_only_correction_rms=rms(trace(base+S)),
        additive_rms=rms(trace(base+S+E)),joint_rms=rms(exact),joint_pair_bend_arcsec=pair(exact-base_b),
        ordered_nonadditive_pair_arcsec=pair(exact-trace(base+S+E)))
out={'definition':'Sum measured/proxy Newtonian fields, apply nu(y)=sqrt((1+sqrt(1+4/y²))/2), project longitudinally; aH=c²/R_H(z); equal metric potentials. Replace, not add to R1.',
     'Jackpot_isolated_stellar':jac,'HE0435_stars_plus_nominal_effective_group_proxy':dict(base_rms_arcsec=rms(base_b),runs=[])}
dst=out['HE0435_stars_plus_nominal_effective_group_proxy']['runs']
for q in [(384,.9,1.8,48),(640,.9,1.8,64),(768,1.5,3.,72)]:
    dst.append(rec(*q)); print(dst[-1],flush=True)
(P/'cumulative_rule.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
