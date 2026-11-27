"""Matched global radial control for HE0435 + angular-averaged local group.

Assumptions: frozen static R1; angular-averaged off-center spherical SIS
group, cut at its SIS r200; measured projected centroid used as 3D radius;
not a native BHSM stress or an anisotropic group solution. Thin-lens projected
mean only. No measured timings, image fitting, source fit, or independent G1.
"""
import math, json, contextlib, io
from pathlib import Path
from scipy.integrate import quad
p=Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()):
 from he0435_joint_field_control import m, d1, w1, z1, G, speed as c, xrad, bg, L, cfs
M=10**11.1
d=67.1*xrad*d1
q=16*m.b*G/c**2*L**2/(bg.LAMBDA*m.C**2)
RAY=[6,8]
def group(sigma):
 rt=math.sqrt(2)*sigma/(10*c/L*cfs(z1)[3])
 mt=2*sigma*sigma/G*rt
 def enclosed(r):
  full=min(rt,max(0.,r-d))
  lo=abs(r-d); hi=min(rt,r+d)
  # Exact partial overlap fraction of a source-centered shell s around the lens-centered ball r.
  # Quadrature avoids cancellation in the small-ball limit.
  val=quad(lambda s:(r*r-(s-d)**2)/(4*s*d),lo,hi,epsabs=1e-16,epsrel=2e-12)[0] if hi>lo else 0.
  return 2*sigma*sigma/G*(full+val)
 assert math.isclose(enclosed(d+rt),mt,rel_tol=1e-14)
 return rt,mt,enclosed
def Mstar(r):return M*m.sphere(r/m.a)[0]
def extra(M,r):return M*2*m.eps/(1+math.sqrt(1+q*M/r**3))
def flux_error(M,r):
 b=m.b; C=m.C; la=bg.LAMBDA; x=r/L; mn=G*M/(c*c*L)
 grad=-2*b*mn/(x*x*(C+C*math.sqrt(1+q*M/r**3)))
 return abs(C*x*x*grad-4*x*grad*grad/la+b*mn)/(b*mn)
results=[]
for sigma in [370,470,570]:
 rt,mt,mg=group(sigma)
 inner=[]
 maxflux=0.
 for rk in [6,8,20,40,80,150,250,400,800,2000,5000]:
  r=rk/1000; mtot=Mstar(r)+mg(r)
  maxflux=max(maxflux,flux_error(mtot,r))
  if rk in [20,40,80]:
   for s in [1-1e-7,1+1e-7]:
    rr=r*s
    assert math.isclose((Mstar(r)+mg(r)),Mstar(rr)+mg(rr),rel_tol=1e-6)
  if rk in RAY:
   beta=r
   def cylinder(lookup):
    pts=[math.acos(beta/x) for x in [d,abs(d-rt),d+rt] if x>beta]
    return quad(lambda t:lookup(beta/math.cos(t))*math.cos(t),0,math.pi/2,points=sorted(set(pts)),epsabs=2.,epsrel=1e-9,limit=200)[0]
   ps,pg=[cylinder(fun) for fun in [Mstar,mg]]
   pj,pi=[cylinder(fun) for fun in [lambda r:extra(Mstar(r)+mg(r),r),lambda r:extra(Mstar(r),r)+extra(mg(r),r)]]
   # In the spherical radial model the ordinary and scalar projections each yield angle 4G M_cyl/(c² b).
   narrow=4*G*w1/(c*c*r*xrad)
   inner.append(dict(impact_kpc=rk,stars_bare_Mcyl_Msun=ps,group_averaged_bare_Mcyl_Msun=pg,R1_joint_Mcyl_Msun=pj,
      R1_isolated_stack_Mcyl_Msun=pi,nonstack_over_total_deflection=(pi-pj)/(ps+pg+pj),
      joint_R1_arcsec=narrow*pj, ordinary_group_arcsec=narrow*pg))
 assert maxflux<1e-14
 results.append(dict(group_sigma_kms=sigma,r200_Mpc=rt,trunc_mass_Msun=mt,max_radial_flux_relative_residual=maxflux,scenarios=inner))
data=dict(scope=__doc__,group_projected_centroid_Mpc=d,results=results)
(p/'he0435_group_monopole_exterior.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(results[1],indent=2))
