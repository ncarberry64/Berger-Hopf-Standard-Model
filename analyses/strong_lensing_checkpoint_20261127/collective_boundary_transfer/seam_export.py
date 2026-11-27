"""Conditional v0.3 GHY mixed scalar under fixed HE 0435 observed-input proxies."""
import json,io
from contextlib import redirect_stdout
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
with redirect_stdout(io.StringIO()):
    from replay import crossing,RH,zl,s,speed,sep,gamma
A,B=.025,.761
def group_M(r):
    return gamma*(B*np.arctan(r/B)-A*np.arctan(r/A))*speed**2
def evaluate(Rp,N):
    ref=crossing(Rp)
    a=ref['seam_kpc'] / 1000
    h2=ref['tracefree_shape_shift_pc'][0]/1e6
    x,w=leggauss(N)
    y=np.sqrt(1-x*x)
    def geometry(h):
        rad=a+h*(3*x*x-1)/2
        d=-3*h*x*y
        d2=3*h*(1-2*x*x)
        E=np.hypot(rad,d)
        H=(rad*rad+2*d*d-rad*d2)/E**3+(rad+3*h*x*x)/(rad*E)
        Nrad,Ntheta=rad/E,-d/E
        area=rad*E # dA / dOmega
        rG=np.sqrt(rad*rad+sep*sep-2*rad*sep*x)
        ext=group_M(rG)/rG**3
        ext_rad=ext*(rad-sep*x)
        ext_theta=ext*sep*y
        acc=group_M(sep)/sep**2
        ext_rad+=acc*x
        ext_theta-=acc*y
        self_rad=np.array([s.sphere(r/s.a)[0] for r in rad])*s.m*speed**2/rad**2
        integrate=lambda val: np.dot(w,H*area*val)/4
        return integrate(Nrad*self_rad),integrate(Nrad*ext_rad+Ntheta*ext_theta),integrate(Nrad*x-Ntheta*y)
    steel,group,translation=geometry(0)
    sf,gf,tf=geometry(h2)
    _,gf2,_=geometry(-h2)
    assert abs(steel-(s.m*speed**2*ref['stellar_mass_fraction_at_seam']/a))/steel < 1e-13
    assert abs(translation)<1e-12 and abs(tf)<1e-12
    tg=ref['group_tidal_eigenvalues_kms2_Mpc2']
    # δH = 4h P2/a²; traceless ∂nΦ_group = (2/3)(Tpar-Tperp) a P2.
    # A finite group profile additionally has a nonconstant density evaluated on the nearby surface.
    cross_only= (4/15)*h2*a*(tg[0]-tg[1])
    return dict(RH_Gpc=Rp/1000,R_kpc=1000*a,prescribed_P2_amplitude_pc=h2*1e6,K_sphere_luminous_kms2=steel,
      K_sphere_group_kms2=group,group_fraction=group/steel,delta_K_total_kms2=sf+gf-steel-group,
      delta_K_luminous_kms2=sf-steel,delta_K_group_kms2=gf-group,delta_K_frac=(sf+gf-steel-group)/steel,
      finite_difference_odd_group_kms2=(gf-gf2)/2,tracefree_tide_analytic_kms2=cross_only,
      uniform_accel_integral=abs(tf))
if __name__=='__main__':
    vals=[]
    for r in [RH,RH/(1+zl)]:
        base=evaluate(r,48)
        refined=evaluate(r,96)
        for key in ['delta_K_luminous_kms2','delta_K_group_kms2','K_sphere_group_kms2']:
            assert abs(base[key]-refined[key])<1e-7
        vals.append(refined)
    Path(__file__).with_name('seam_export.json').write_text(json.dumps(vals,indent=2)+'\n')
    print(json.dumps(vals,indent=2))
