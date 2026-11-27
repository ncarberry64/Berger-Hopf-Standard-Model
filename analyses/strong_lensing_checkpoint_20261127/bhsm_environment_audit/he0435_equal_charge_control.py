"""Spherical zero exterior charge control, not a predicted equilibrium."""
import json
from pathlib import Path
from math import sqrt,log1p
from scipy.integrate import quad
p=Path(__file__).parent
cal=json.loads((p/'he0435_halo_calibration.json').read_text())
c=cal['runs'][1]
b,rs,m0=cal['RE_kpc'],c['scale_kpc'],c['M0']
def m(r):
    x=r/rs
    return m0*(log1p(x)-x/(1+x))
def f(r):
    x=(b/r)**2
    return x/(1+sqrt(1-x))
def density(r): return m0*r/(r+rs)**2
ref=m(b)+quad(lambda r:density(r)*f(r),b,float('inf'),epsrel=1e-9)[0]
assert abs(ref/cal['projected_DM_Msun_at_RE']-1)<1e-8
ans=[]
for R in [20,50,100]:
    cyl=m(b)+quad(lambda r:density(r)*f(r),b,R,epsrel=1e-9)[0]-m(R)*f(R)
    # Integration by parts with zero exterior charge, no explicit shell.
    x=b/R
    angle_end=__import__('math').acos(x)
    second=quad(lambda t:m(b/__import__('math').cos(t))*__import__('math').cos(t),0,angle_end,epsrel=1e-10)[0]
    assert abs(second/cyl-1)<1e-8
    ans.append(dict(return_radius_kpc=R,cylinder_Msun=cyl,fraction=cyl/ref))
(p/'he0435_equal_charge_control.json').write_text(json.dumps(ans,indent=2)+'\n')
print(ans)
print('quartic bracket at cancellation:',5.84444718718846*(-18.1974927890349085)+81.5773688846122)
