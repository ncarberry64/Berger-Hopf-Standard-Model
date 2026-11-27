"""Frozen Jackpot S3 same-light R1 control; no source, halo or coupling fit."""
from pathlib import Path
from itertools import product
import sys,json
import numpy as np
from scipy.integrate import quad
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'bhsm_environment_audit'/'pinned_extra'))
from r1_background_geometry import D,cfs,G,speed,L,xrad,bg
z=.222; source=5.975; dl=D(0,z); weight=D(z,source)/D(0,source)
b,C,eps,_=cfs(z)
# Independent inputs: Sonnenfeld+ 2012 photometry Tables 3/8.
angle_scales=np.array([[.066,.50],[.082,6.05]])
axes=np.array([.66,.71])
angles=np.deg2rad([63.0,-24.3])
masses={'Chabrier':[10.85,11.27],'Salpeter':[11.13,11.52]}
scales=angle_scales*(dl*xrad)
# Test inputs opened only after specifying a circular tPIEMD and the same R1 state as PR23.
theta=np.array([[3.,-1.91],[-1.03,.87]]) # Collett & Smith 2020 Table 1
angle_sis=lambda q:4*np.pi*(q/speed)**2/xrad
w12=D(.609,source)/D(0,source)
w23=D(2.035,source)/D(0,source)
s1_bound=2*w12*angle_sis(100.)
s2_bound=2*w23*angle_sis(150.)
def m3(r,m):
    a,t=scales.T
    return float(np.sum(m*2/np.pi*(t*np.arctan(r/t)-a*np.arctan(r/a))/(t-a)))
def m2(R,m):
    a,t=scales.T
    return float(np.sum(m*((R*R/(np.hypot(R,a)+a))-(R*R/(np.hypot(R,t)+t)))/(t-a)))
def elliptic(t,m,q=axes):
    # Homoeoidal integral for surface mass kappa(s) on nested ellipses;
    # s is area-preserving (same coordinate as Table 3).
    s=0.*t
    for (a,d),qm,pa,mi in zip(scales,q,angles,m):
        A=np.array([[np.sin(pa),np.cos(pa)],[np.cos(pa),-np.sin(pa)]])
        X,Y=A@t*(dl*xrad)
        def f(u,k):
            Z=1-(1-qm*qm)*u
            S=np.sqrt(qm*u*(X*X+Y*Y/Z))
            local=(1/np.hypot(S,a)-1/np.hypot(S,d))/(d-a)
            return local/Z**(k+.5)
        val=2*weight*dl*mi*qm*np.array([X*quad(f,0,1,args=(0,),epsabs=1e-8)[0],Y*quad(f,0,1,args=(1,),epsabs=1e-8)[0]])/(dl*xrad)
        s+=A.T@val
    return s
def ray(t,m):
    R=np.linalg.norm(t)*dl*xrad
    direction=t/np.linalg.norm(t)
    base=m2(R,m)*4*weight/(R*xrad)*direction
    def integrand(t):
        c=np.cos(t); r=R/c; enclosed=m3(r,m)
        S=np.sqrt(1+16*b*enclosed*L**2/(bg.LAMBDA*C*C*r**3))
        return enclosed*(2*eps/(1+S))*c
    Q,err=quad(integrand,0,np.pi/2,epsabs=2e-18,epsrel=1e-9,limit=400)
    Q2=quad(integrand,0,np.pi/2,epsabs=2e-20,epsrel=1e-11,limit=500)[0]
    assert abs(Q-Q2)*4*weight/(R*xrad)<2e-6
    assert np.max(abs(base-elliptic(t,m,q=np.ones(2))))<1e-8
    return base, Q*4*weight/(R*xrad)*direction,elliptic(t,m)
def replay(logm):
    m=10**np.array(logm)*G/speed**2
    def control():
        for R in (dl*xrad*.7,dl*xrad*4,dl*xrad*20):
            # Project ordinary spherical force directly from 3-D mass.
            check=quad(lambda u:m3(R/np.cos(u),m)*np.cos(u),0,np.pi/2,epsabs=2e-18,epsrel=1e-10)[0]
            assert abs(check-m2(R,m))/m2(R,m)<1e-9
    control()
    a,add,e=np.moveaxis(np.array([ray(t,m) for t in theta]),1,0)
    delta=tsep=lambda x:np.linalg.norm(x[0]-x[1])
    return dict(spherical_GR_arcsec=float(tsep(theta-a)),spherical_R1_arcsec=float(tsep(theta-a-add)),
        elliptical_GR_arcsec=float(tsep(theta-e)),paired_scalar_change_arcsec=float(delta(add)),
        required_extra_reduced_bending_vector_arcsec=(theta-a-add)[0].__sub__((theta-a-add)[1]).tolist(),
        # Triangle-inequality floor from optional fixed dispersions, independent of SIS center.
        leftover_floor_spherical_R1_if_SIS_bounds_arcsec=max(0.,float(tsep(theta-a-add))-s1_bound-s2_bound))
out={'data':'Collett & Smith 2020 Table 1; Sonnenfeld et al. 2012 Tables 3,8. Main plane only, fixed R1. Elliptical calculation changes only ordinary gravity; does not add spherical R1 to it.',
     'image_offsets_arcsec':theta.tolist(),'image_radii_arcsec':np.linalg.norm(theta,axis=1).tolist(),
     'intermediate_plane_SIS_sensitivity_assumptions_kms':[100,150],
     'max_intermediate_differential_in_arcsec':[s1_bound,s2_bound],'results':{}}
for name,a in masses.items():
    out['results'][name]=replay(a)
    signs=[(-.06,.09,-.08,.05),(-.11,.05,-.08,.06)][name=='Salpeter']
    corners=[replay(np.array(a)+[i,j]) for i,j in product(signs[:2],signs[2:])]
    out['results'][name]['mass_corner_checks_not_confidence_intervals']={k:[min(t[k] for t in corners),max(t[k] for t in corners)] for k in ('spherical_R1_arcsec','elliptical_GR_arcsec','paired_scalar_change_arcsec')}
(P/'s3_stellar_transfer.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
