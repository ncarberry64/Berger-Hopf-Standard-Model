"""Gravity-only WGD seam fixture on a finite-total-mass extended tracer; no fit."""
from pathlib import Path
import json,math
from scipy.optimize import brentq
import numpy as np
p=Path(__file__).resolve().parent
owned=p.parent/'wgd_frozen_transfer/wgd_frozen_transfer.py'
ns={'__file__':str(owned)}
exec(compile(owned.read_text().split('\nruns={}',1)[0],str(owned),'exec'),ns)
D=ns['d_l']; a=ns['a']; G=ns['G']; c=ns['speed']; xrad=ns['xrad']; dz=.230
Dls,Dos=ns['D'](dz,.777),ns['D'](0,.777)
b=1.30*xrad*D
crit=c*c/(4*G)*D*Dos/Dls*(b/D)**2
proj=ns['se_proj'](b/a)
R0=ns['L']/math.sqrt(-ns['bg'].OMEGA_K0)
def I(x):
 if x>=1:return math.pi*x/2-1
 return x*math.asin(x)-x*x/(1+math.sqrt(1-x*x))
def mus(r):return ns['sersic'](r/a)
grid=a*np.geomspace(1e-8,300,801)
rows=[]
for tag,RH in [('curvature_today',R0),('curvature_epoch',R0/(1+dz))]:
 for logM in (11.57,11.82):
  M=10**logM; m0=G*M/c**2
  def curve(r,xi):
   m=m0*mus(r)[0]
   # exactly rationalized spatial Brown-York deficit on static sphere.
   return 2*m*RH/(r*r*(1+math.sqrt(1-2*m/r)))-xi
  def roots(xi):
   v=[curve(r,xi) for r in grid]
   return [brentq(lambda r:curve(r,xi),r0,r1,xtol=1e-16,rtol=1e-14) for r0,r1,lo,hi in zip(grid[:-1],grid[1:],v[:-1],v[1:]) if lo*hi<0]
  crit_cap=math.pi**2/16*c*c*b*b/(G*RH)/crit
  bare=M*proj/crit
  vals=[]
  for x in (.75,1.,1.25):
   found=roots(x)
   rec=[]
   for r in found:
    mu,n=mus(r)
    ratio=M*mu*I(b/r)/crit
    assert ratio<=x*crit_cap*(1+1e-9)
    rec.append({'rstar_kpc':r*1e3,'b_over_rstar':b/r,'enclosed_mass_fraction':mu,
                'log_enclosed_mass_slope':n,'newton_Xi_d_log_r':(n-2)*m0*mu*RH/r**2,
                'projected_addition_over_critical':ratio,'status':'geometry roots only, not action-selected Hessian zeros'})
   vals.append({'prescribed_Xi_geo':x,'seams':rec})
  actual=vals[1]['seams'][-1]
  slopes=tuple(mus(r)[1] for r in np.geomspace(a,200*a,113))
  rows.append({'RH_case':tag,'RH_Gpc':RH/1000,'log_stellar_mass':logM,
               'bare_stars_over_critical':bare,'gravity_only_any_seam_shell_cap_over_critical':crit_cap,
               'combined_A_times_Weyl_ratio_times_Xi_needed_min':(1-bare)/crit_cap,
               'outer_geometric_root_fraction_of_remainder':actual['projected_addition_over_critical']/(1-bare),
               'scan_n_M_above_Re_max':max(slopes),'geom_threshold_sensitivity_toy':vals})
hst_fraction_upper=.2907593821 # F160W light within 1.36 arcsec, an upper cap within 1.30 arcsec
for row in rows:
 cap=row['gravity_only_any_seam_shell_cap_over_critical']
 mass=10**row['log_stellar_mass']
 row['hst_F160W_conservative_star_fraction_upper']=mass*hst_fraction_upper/crit
 row['hst_F160W_combined_A_times_Weyl_ratio_times_Xi_needed_min']=(1-mass*hst_fraction_upper/crit)/cap
out={'scope':'HST Chabrier 11.57 and +0.25 dex sensitivity, DES circularized Sersic shape as independent luminous proxy; static spatial GR Brown-York curvature applied to spherical enclosed mass, fixed galaxy epoch. Historical A=1 and Phi=Psi sharp shell extends to infinity as an upper control. The .75,1.25 neighboring values are explicit conditional sensitivities, not fitted or inferred.',
      'HST_F160W_fraction_at_1p36_arcsec':hst_fraction_upper,
     'HST_F160W_photometry_source':'https://github.com/TDCOSMO/WGD2038-4008/blob/85ee2127a7f668f0642f17ad52d09ed9da73e443/lenstronomy_modeling/notebooks/Fit%20deflector%20light%20using%20photutils.ipynb',
     'circular_critical_Msun':crit,'impact_kpc':b*1e3,'results':rows}
(p/'wgd_extended_seam_bracket.json').write_text(json.dumps(out,indent=2)+'\n')
for row in rows:
 a1=row['geom_threshold_sensitivity_toy'][1]['seams']
 print(row['RH_case'],row['log_stellar_mass'],'bare',row['bare_stars_over_critical'],'cap',row['gravity_only_any_seam_shell_cap_over_critical'],'min_product',row['combined_A_times_Weyl_ratio_times_Xi_needed_min'],'all_seams',a1,'max_nM',row['scan_n_M_above_Re_max'])
