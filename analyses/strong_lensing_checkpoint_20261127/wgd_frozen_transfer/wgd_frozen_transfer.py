"""Frozen retained R1: WGD independent photometric input / conditional spherical control."""
from pathlib import Path
import hashlib,json,math,sys
from functools import lru_cache
from scipy.integrate import quad
from scipy.special import gammainc,gammaincinv,gammaln
import numpy as np
p=Path(__file__).resolve().parent
src=p/'pr23'
sys.path.insert(0,str(src/'code'))
import background as bg
manifest=json.loads((src/'preregistration/prediction_manifest.json').read_text())['background_R1']
for name,array in [('Omega_m0',bg.OMEGA_M0),('Omega_r0',bg.OMEGA_R0),('Omega_k0',bg.OMEGA_K0),('lambda',bg.LAMBDA),('q',bg.Q)]:
 assert manifest[name]==array
bgsol=bg.integrate(manifest['V0_over_Mpl2H02']); assert bgsol.success
H0=67.4; speed=299792.458; G=4.300917270036279e-9
L=speed/H0; xrad=math.pi/(180*3600)
def cfs(z):
 N=-math.log1p(z); y=bgsol.sol(N)
 v,H=float(y[1]),float(y[2]); d=H*bg.rhs(N,y)[1]
 l=bg.LAMBDA; b=2*v*v/l; C=1+4*(d+2*H*v)/l-2*v**4/l**2
 return b,C,b*b/(2*C),H
def D(z1,z2):
 chi=quad(lambda z:1/float(bgsol.sol(-math.log1p(z))[2]),z1,z2,epsabs=2e-13)[0]
 a=math.sqrt(-bg.OMEGA_K0)
 return L*math.sin(a*chi)/(a*(1+z2))
b0,C0,e0,_=cfs(.3); rv0=(16*b0*(G*1e11/speed**2)*L**2/(bg.LAMBDA*C0*C0))**(1/3)
ref=json.loads((src/'artifacts/strong_lensing_r1_screened_20261020/review/r1_qs_coefficients.json').read_text())
assert abs(rv0/ref['prediction']['rV_Mpc']-1)<1e-10 and abs(e0/ref['prediction']['unscreened_mu_minus_one']-1)<1e-10
z_l=.230; d_l=D(0,z_l); b,C,e,H=cfs(z_l)
q=.77; re=3.45; sers_n=1.90
a=d_l*re*math.sqrt(q)*xrad
a_major=d_l*re*xrad
shape_n=2*sers_n+1; lognorm=gammaln(shape_n); bn=gammaincinv(2*sers_n,.5)
def pl(r):
 return (r/math.hypot(r,1))**3,3/(1+r*r)
def pl_proj(r):
 return r*r/(1+r*r)
@lru_cache(maxsize=120000)
def sersic(r):
 y0=bn*r**(1/sers_n)
 if y0>76:return 1.,0.
 def gam(y):return math.exp((shape_n-1)*math.log(y)-y-lognorm)
 def mp(t):
  y=y0+t*t; u=(y0/y)**sers_n
  if u<1e-3:
   ker=4/(3*math.pi)*u**3*(1+.3*u*u+9/56*u**4)
  else: ker=2/math.pi*(math.asin(u)-u*math.sqrt(max(0,1-u*u)))
  return 2*t*gam(y)*ker
 def slope(t):
  y=y0+t*t
  lu=-sers_n*math.log1p(t*t/y0); u=math.exp(lu)
  if t==0:
   return 8/math.pi*gam(y0)*math.sqrt(y0/(2*sers_n))
  return 8/math.pi*t*gam(y)*u**3/math.sqrt(-math.expm1(2*lu))
 mu=gammainc(shape_n,y0)+quad(mp,0,10,epsabs=1e-13,epsrel=2e-10)[0]
 m_slope=quad(slope,0,10,epsabs=1e-13,epsrel=2e-10)[0]
 return mu,m_slope/mu
def se_proj(r):return gammainc(2*sers_n,bn*r**(1/sers_n))
def integral_los(lookup,beta):
 return quad(lambda theta: lookup(beta/math.cos(theta))[0]*math.cos(theta),0,math.pi/2,epsabs=2e-13,epsrel=2e-9)[0]
def integral_shell(lookup,beta):
 def integrand(t):
  mass,log_slope=lookup(beta/t)
  return mass*log_slope*t/(1+math.sqrt(max(0,1-t*t)))
 return lookup(beta)[0]+quad(integrand,0,1,epsabs=2e-13,epsrel=2e-9)[0]
def model(mass,scale,profile,project,beta):
 m=G*mass/speed**2
 rv=(16*b*m*L*L/(bg.LAMBDA*C*C))**(1/3); k=(rv/scale)**3
 def extra(r):
  mu,n=profile(r); S=math.sqrt(1+k*mu/r**3)
  F=2*e/(1+S); nE=.5*((1+1/S)*n+3*(1-1/S))
  return mu*F,nE
 def total(r):
  mu,n=profile(r); u,ne=extra(r)
  return mu+u,(mu*n+u*ne)/(mu+u)
 x0=profile(beta)[0]; F=extra(beta)[0]/x0
 ex_los=integral_los(extra,beta)
 ex_shell=integral_shell(extra,beta)
 old=project(beta)
 old_projection_diff=abs(integral_shell(profile,beta)-old)
 mapped=integral_shell(total,beta)
 x=k*total(beta)[0]/beta**3
 u=x/(math.sqrt((1+e)**2+x)+1+e)
 inverse_mu=beta**3/k*u*(2+u)
 assert abs(inverse_mu-x0)<3e-15
 assert old_projection_diff<4e-10
 assert abs(ex_los-ex_shell)<4e-12
 assert abs(mapped-(old+ex_los))<6e-10
 assert ex_los<=e*old*(1+1e-11)
 return dict(beta=bEta(beta),rV_kpc=rv*1000,H_l_rV_over_c=H*rv/L,
     fractional_force_at_radius=F,epsilon= e,extra_deflection_over_bare_stellar_deflection=ex_los/old,
     mapped_extra_cyl_shell_relative_error=abs(ex_los-ex_shell)/ex_los,
     mapped_total_cyl_absolute_fraction_error=abs(mapped-(old+ex_los)),
     bare_cyl_projection_check_fraction=old_projection_diff,
     bare_stars_projected_Msun=mass*old,extra_projected_Msun=mass*ex_los,
     extra_mass_upper_bound_Msun=mass*old*e, mapped_total_projected_Msun=mass*mapped,
     inverse_bare_mass_fraction_absolute_error=abs(inverse_mu-x0))
def bEta(x):return float(x)
runs={}
for lab,prof,project in [('Plummer_proxy',pl,pl_proj),('Abel_Sersic',sersic,se_proj)]:
 runs[lab]={}
 for logM in [11.21,11.40,11.64,11.84]:
  rows=[model(10**logM,a,prof,project,beta) for beta in [.25,.5,1.,2.,4.]]
  runs[lab][str(logM)]=rows
Ein=[]
for scale_name,scale in [('circularized',a),('major_axis_as_spherical',a_major)]:
 beta=d_l*1.30*xrad/scale
 for logM in [11.40,11.64,11.84]:
  row=model(10**logM,scale,sersic,se_proj,beta)
  row.update(profile_scale=scale_name,log_stellar_mass=logM,assumed_arcsec=1.30,ratio_at_source_redshift={})
  for z_s in [.777,2.187]:
   crit=speed**2/(4*G)*d_l*D(0,z_s)/D(z_l,z_s)*(1.30*xrad)**2
   row['ratio_at_source_redshift'][str(z_s)]={'circular_critical_Msun':crit,'bare_over_critical':row['bare_stars_projected_Msun']/crit,'extra_over_critical':row['extra_projected_Msun']/crit,'extra_upper_bound_over_critical':row['extra_mass_upper_bound_Msun']/crit}
  Ein.append(row)
out={'classification':'CONDITIONAL_FROZEN_LOCAL_STELLAR_INPUT_TRANSFER_NOT_OBSERVATIONAL_VALIDATION',
 'base_commit':'4f044a6af5757f6f1c4e99e6547b43d6c45e353c',
 'input_sha256':{str(f.relative_to(src)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(src.rglob('*')) if f.is_file() and f.suffix in ['.json','.py']},
 'observational_inputs':{'primary_photometry':'https://academic.oup.com/mnras/article/479/4/4345/5032807','z_l':z_l,'major_Re_arcsec':re,'q':q,'n':sers_n,'mass_cases_log10':[11.21,11.40,11.64,11.84],'imaging_only_sie_Einstein_scale_arcsec':1.30},
 'notes':['All photometric masses and light-profile fits are adopted input, not derived by BHSM; no dynamics, shear, source geometry, or dark halo modeled. Circularized, spherical, constant M/L profiles; compact bulge omitted. Plummer is a proxy; Sersic integrates exact spherical Abel deprojection. Imported empirical M* not reestimated for R1 cosmology. No measured or fitted delays used.',
          'Critical-cylinder rows are separate circular single-plane, source-redshift conditional screens, not full quad mass or fit; quoted .777 and alternative 2.187 are not resolved by this calculation. A profile beyond the local radial regime is not physical exterior completion.',
          'Exact optical equivalence within retained spherical weak-field operator; compare input profile + explicit R1 or mapped total mass, never both. Positive effective density by monotone enclosed-mass identity.'],
 'coefficients':{'b':b,'C':C,'epsilon_inf':e,'H_l_over_H0':H,'H0_km_s_Mpc':H0,'lens_D_A_Mpc':d_l,'circularized_Re_kpc':a*1e3,'major_Re_kpc':a_major*1e3,'replayed_original_rV_kpc_at_z0p3_M1e11':rv0*1e3},
 'profiles':runs,'Einstein_radius_conditional_screen':Ein}
(p/'wgd_frozen_transfer.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out['coefficients'],indent=2))
for model_name,x in runs.items():
 print(model_name,'mean photometric M*: response @ .25,.5,1,2,4 Re',[(y['beta'],y['extra_deflection_over_bare_stellar_deflection'],y['mapped_extra_cyl_shell_relative_error']) for y in x['11.64']])
for row in Ein: print(row['profile_scale'],row['log_stellar_mass'],row['bare_stars_projected_Msun'],row['extra_projected_Msun'],row['ratio_at_source_redshift'])
