"""Fixed-input HE0435 sharp-seam and muon-inspired scalar conormal transfer.
No fitted environmental coefficients, no timing or flux-ratio inputs.
"""
from pathlib import Path
import sys, math, json
import numpy as np
from scipy.optimize import brentq
from scipy.special import spherical_kn
p=Path(__file__).resolve().parent
sys.path.insert(0,str(p.parent/'bhsm_environment_audit'))
from he0435_joint_field_control import D,G,speed,bg,L,xrad,Profile
zl,zs=.4546,1.693
dl,ds,dls=D(0,zl),D(0,zs),D(zl,zs)
RH=L/np.sqrt(-bg.OMEGA_K0)
Deff=dl*dls/ds
b=dl*1.2*xrad
s=Profile(10**11.1,3.984,3.51,zl)
mcrit=speed**2*b*b/(4*G*Deff)
sep=dl*67.1*xrad
gamma=2*(470/speed)**2
def group_tide(d):
    a,R=.025,.761
    M=gamma*(R*np.arctan(d/R)-a*np.arctan(d/a))
    dM=gamma*d*d*(1/(d*d+a*a)-1/(d*d+R*R))
    return speed**2*(dM/d**2-2*M/d**3),speed**2*M/d**3
def crossing(Rp):
    def deficit(a):
        f,_=s.sphere(a/s.a)
        m=s.m*f
        return 2*m*Rp/(a*a*(1+np.sqrt(1-2*m/a)))-1
    a=brentq(deficit,s.a,0.06,xtol=1e-15)
    f,slope=s.sphere(a/s.a)
    group=np.array(group_tide(sep))
    tidal=group-np.mean([group[0],group[1],group[1]])
    da=a*a*tidal/(speed**2/Rp)/(2-slope)
    x=b/a
    xfun=lambda x:x*np.arcsin(x)-(x*x)/(1+np.sqrt(1-x*x)) if x<=1 else np.pi*x/2-1
    M_extra=s.m*speed**2/G*f*(xfun(x)-20*xfun(x/20))
    mono_cap=np.pi**2*Deff/(4*Rp)
    stars=10**11.1*s.cyl(b,False)[0]/mcrit
    assert M_extra/mcrit<=mono_cap
    return dict(R_H_Gpc=Rp/1000,seam_kpc=a*1000,stellar_mass_fraction_at_seam=f,
        acceleration_log_slope=slope-2,group_tidal_eigenvalues_kms2_Mpc2=group.tolist(),
        tracefree_shape_shift_fraction_along_and_across_group=da.tolist(),
        tracefree_shape_shift_pc=(da*a*1e6).tolist(),
        projected_extra_over_circular_critical=M_extra/mcrit,
        sharp_shell_any_radius_cap_over_critical=mono_cap, stars_over_circular_critical=stars,
        min_product_if_stars_and_shell_only=(1-stars)/mono_cap)
def scalar_test():
    # Spherical static vacuum exterior; scale-free replay, not fitted B.
    R=1
    cases=[]
    for ell in (0,1,2,3,6):
        for ratio in (.2,1,4,10):
            x=1/ratio
            h=-(ell+1)/R
            y=spherical_kn(ell,x,True)/spherical_kn(ell,x)/ratio
            # Same visible value at R but two different hidden normal traces.
            for H,V in ((1.,0.),(0.,1.),(.37,.63)):
                t=H+V
                d=h*H+y*V
                recovered=(d-y*t)/(h-y)
                # Independent second derivative from each radial ODE at R.
                lap_h=-2*h/R+ell*(ell+1)/R**2+2*h/R-ell*(ell+1)/R**2
                lap_y=x*x
                flux=h*H+(1-ratio**2*lap_y)*y*V-ratio**2*lap_h*h*H
                assert abs(recovered-H)<1e-12 and abs(flux-h*H)<1e-12
                cases.append(dict(ell=ell,sqrt_B_over_R=ratio,trace=t,normal=d,canonical_flux=flux,det=h-y))
    return cases
out=dict(zl=zl,zs=zs,impact_kpc=1000*b,group_projected_offset_kpc=1000*sep,circular_critical_Msun=mcrit,
    geometry=[crossing(RH),crossing(RH/(1+zl))],boundary_checks=scalar_test())
(p/'results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='boundary_checks'},indent=2))
print(len(out['boundary_checks']),'boundary checks passed')
