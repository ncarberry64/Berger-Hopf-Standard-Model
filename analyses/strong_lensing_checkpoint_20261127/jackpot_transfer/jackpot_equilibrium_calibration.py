"""Two-point projected residual calibration; not a BHSM equilibrium or halo-particle inference."""
from pathlib import Path
import json,sys
import numpy as np
from scipy.interpolate import CubicSpline
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'bhsm_environment_audit'/'pinned_extra'))
from r1_background_geometry import D, G, speed, xrad
z=.222
zs=(.609,2.035)
ang=np.array([1.397,2.07])
Dl=D(0,z)
w=np.array([D(z,i)/D(0,i) for i in zs])
# Physical mass uses Turner's reported inner mass. Use R1 angular efficiency ratios only
# to carry its unit scale consistently to the outer aperture.
M1=3.08e11
M2=M1*(ang[1]/ang[0])*(1.89/ang[0])*(w[0]/w[1])
a,t=np.array([[.066,.50],[.082,6.05]]).T
def stars(R,logm):
    return np.sum(10**np.array(logm)*(np.hypot(R,a)-a-np.hypot(R,t)+t)/(t-a))
def test(logm):
    ss=np.array([stars(R,logm) for R in ang])
    yy=np.array([M1,M2])-ss
    n=np.log(yy[1]/yy[0])/np.log(ang[1]/ang[0])
    assert np.allclose(ss+yy[0]*(ang/ang[0])**n,[M1,M2])
    def alpha(x):return (stars(x,logm)+yy[0]*(x/ang[0])**n)/x*(ang[0]**2/M1)
    def slope(step):
        p=ang[0]
        dif=np.array([alpha(p+i*step) for i in (-2,-1,0,1,2)])
        der=np.dot(dif,[1,-8,0,8,-1])/(12*step)
        der2=np.dot(dif,[-1,16,-30,16,-1])/(12*step**2)
        return 1+.5*p*der2/(1-.5*(der+1))
    assert abs(slope(.001)-slope(.0005))<1e-7
    return dict(stars_Msun=ss.tolist(),excess_Msun=yy.tolist(),excess_fractions=(yy/[M1,M2]).tolist(),
                projected_excess_enclosed_power=n,derived_total_lensing_equivalent_eta=slope(.001))
out=dict(scope='Spherical empirical calibration; primary outer deflection is from Turner joint model, not independent raw astrometry. No true 3D state or asymptotic power law implied.',
         apertures_arcsec=ang.tolist(),apertures_kpc=(ang*Dl*xrad*1000).tolist(),total_projected_Msun=[M1,M2],
         throughput_ratio=w[0]/w[1],Chabrier=test([10.85,11.27]),Salpeter=test([11.13,11.52]))
(P/'jackpot_equilibrium_calibration.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
