"""Exact joint spherical monopole of locally angular-averaged SIS group density.

This evaluates the existing R1 quasi-static regular radial branch using the
projected group offset as a 3D offset proxy. Radius <= 12 kpc, not an optical
projection of the entire group, not a 3D anisotropic or native stress solve.
"""
import math, json
from pathlib import Path
from scipy.integrate import quad
p=Path(__file__).resolve().parent
src=p/'he0435_joint_field_control.py'
ns={'__file__':str(src)}
exec(compile(src.read_text().split('# Main:',1)[0],str(src),'exec'), ns)
Profile=ns['Profile']; G=ns['G']; c=ns['speed']; xrad=ns['xrad']; zl=ns['z1']; dl=ns['d1']; L=ns['L']; bg=ns['bg']
stars=Profile(10**11.1,4.4*math.sqrt(.82),3.51,zl)
d=dl*67.1*xrad
q=16*stars.b*(G/c**2)*L**2/(bg.LAMBDA*stars.C**2)
def group_enclosed(r,sig):
 x=r/d
 J=sum(2*x**(2*k+3)/((2*k+1)*(2*k+3)) for k in range(8))
 # Nested spherical integral over the sky angle at r and the radial volume.
 test=quad(lambda y:y*math.log1p(2*y/(1-y)),0,x,epsabs=1e-18,epsrel=1e-12)[0]
 assert math.isclose(J,test,rel_tol=2e-12)
 return sig*sig/G*d*J
def delta(M,r):
 return M*(2*stars.eps/(1+math.sqrt(1+q*M/r**3)))
rows=[]
for sig in [370,470,570]:
 for radius in [3.,6.,8.,12.]:
  r=radius/1000
  M=stars.sphere(r/stars.a)[0]*10**11.1
  Mg=group_enclosed(r,sig)
  fs,fg,fj=delta(M,r),delta(Mg,r),delta(M+Mg,r)
  assert fs < fj < fs+fg
  rows.append(dict(group_SIS_sigma_km_s=sig,radius_kpc=radius,stars_3D_enclosed_Msun=M,
    group_angular_average_3D_enclosed_Msun=Mg,group_fraction_of_stellar_3D_enclosed=Mg/M,
    joint_R1_scalar_correction_fraction_of_full_force=fj/(M+Mg),
    joint_minus_isolated_stars_R1_fraction_of_full_force=(fj-fs)/(M+Mg),
    separately_added_scalar_exceeds_joint_fraction_of_joint_scalar=(fs+fg-fj)/fj))
o=dict(scope=__doc__,group_projected_centroid_Mpc=d,group_offset_arcsec=67.1,
  group_spectroscopy='Sluse et al. Table 4, 10.1093/mnras/stx1484, nominal 470±100 km/s.',
  scalar_coefficients=dict(eps=stars.eps,C=stars.C),results=rows)
(p/'he0435_local_group_l0_control.json').write_text(json.dumps(o,indent=2)+'\n')
print(json.dumps([x for x in rows if x['group_SIS_sigma_km_s']==470],indent=2))
