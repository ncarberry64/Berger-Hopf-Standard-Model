"""First-order lens recentering and odd-projection controls; not a BHSM solve."""
import json, numpy as np
from scipy.special import eval_legendre
from numpy.polynomial.hermite import hermgauss
from pathlib import Path
phi=np.arange(512)*2*np.pi/512
cosphi=np.cos(phi)
x=cosphi
def coef(f,m): return 2*np.mean(np.cos(m*phi)*f)
def gauss(b,M,s,d=0.):
    return M/(2*np.pi*s*s)*np.exp(-(b*b+d*d-2*b*d*cosphi)/(2*s*s))
d=1e-4
relative=[]
for b in [.5,1.,1.5,2.]:
    B,E=.6,.4
    sb,se=1.,2.
    # Coordinates recentered on the total projected mass centroid.
    exact=(gauss(b,B,sb,-E*d)+gauss(b,E,se,B*d)-gauss(b,B,sb,E*d)-gauss(b,E,se,-B*d))/(2*d)
    theory=b*(-E*gauss(b,B,sb)[0]/sb**2+B*gauss(b,E,se)[0]/se**2)
    numerical=coef(exact,1)
    assert abs(numerical-theory)<1e-10
    relative.append(dict(b=b,c_fixed_total_centroid_m1=numerical,expected=float(theory)))

z,w=hermgauss(40)
z=np.sqrt(2)*z[:,None]
b=1.2
r=np.sqrt(b*b+z*z)
deform=[]
for deg in [0.,30.,60.,90.]:
    i=np.deg2rad(deg)
    s,c=np.sin(i),np.cos(i)
    eta=(s*b*cosphi+ c*z)/r
    surf=(w@ (r**3*eval_legendre(3,eta)))/np.sqrt(np.pi)
    theory=5/8*s**3*b**3
    numerical=coef(surf,3)
    assert abs(numerical-theory)<1e-12
    deform.append(dict(i_degrees=deg, normalized_m1=coef(surf,1),normalized_m3=numerical,expected_m3=theory))
r1=[]
for e in [1e-2,1e-3,1e-4]:
    rtranslated=e*x+np.sqrt(1-e**2*(1-x*x))
    err=np.max(np.abs(1+e*x-rtranslated))
    assert abs(err/e**2-.5)<2e-5
    r1.append(dict(e=e,max_remainder=err))
rec=dict(scope='translation and linear projected-density controls, not a lens fit or BHSM action solution', exact_translation_check=r1, relative_component_offset=relative, octupole_projection=deform)
Path(__file__).with_suffix('.json').write_text(json.dumps(rec,indent=2)+'\n')
print(json.dumps(rec,indent=2))
