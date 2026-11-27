"""Projection scale control of archived galaxy neighborhood law; no source/state fit."""
import json,math
from pathlib import Path
from scipy.optimize import brentq
from scipy.integrate import quad
from scipy.special import gammainc,gammaincinv
p=Path(__file__).resolve().parent
w=json.loads((p.parent/'wgd_frozen_transfer/wgd_frozen_transfer.json').read_text())
H0=67.4;c=299792.458;G=4.300917270036279e-9; omk_abs=.018
R0=c/H0/math.sqrt(omk_abs)
z=.230
dl=w['coefficients']['lens_D_A_Mpc']
b=dl*1.30*math.pi/(180*3600)
crit=w['Einstein_radius_conditional_screen'][0]['ratio_at_source_redshift']['0.777']['circular_critical_Msun']
critalt=w['Einstein_radius_conditional_screen'][0]['ratio_at_source_redshift']['2.187']['circular_critical_Msun']
a=w['coefficients']['circularized_Re_kpc']/1000
n=1.90; fre=gammainc(2*n,gammaincinv(2*n,.5)*(b/a)**(1/n))
def geom_projection(x):
 if x>=1: return math.pi*x/2-1
 return x*math.asin(x)-x*x/(1+math.sqrt(1-x*x))
def numer_projection(x):
 # In units r*: integrate shells outside cylinder using t=1/y.
 lower=max(1,x)
 return max(0,x-1)+quad(lambda t:x*x/(1+math.sqrt(max(0,1-(x*t)**2))),0,1/lower,
                          epsabs=1e-14,epsrel=2e-11)[0]
for x in (.1,.2,.75,.99,1,1.4,5):
 assert math.isclose(geom_projection(x),numer_projection(x),rel_tol=2e-10)
rows=[]
for label,curv in (('reference_RH_today',R0),('physical_RH_at_lens_epoch',R0/(1+z))):
 for logM in (11.40,11.57,11.64,11.82,11.84):
  M=10**logM; m=G*M/c**2
  s0=math.sqrt(m*curv)
  rs=brentq(lambda r:r*r/curv-r**3/(2*curv**2)-m,.99*s0,1.01*s0,xtol=5e-16)
  x=b/rs
  add=M*geom_projection(x); mstar=fRe=M*fre
  assert math.isclose(m,(2*m/(rs*(1+math.sqrt(1-2*m/rs))))*rs/2*(1+math.sqrt(1-2*m/rs)),rel_tol=1e-14)
  assert math.isclose(2*m/(rs*rs*(1+math.sqrt(1-2*m/rs))),1/curv,rel_tol=2e-11)
  rows.append({'curvature_radius_case':label,'RH_Gpc':curv/1e3,'logM':logM,'rstar_kpc':rs*1e3,'b_to_rstar':x,
        'stellar_projected_Msun':mstar,'conditional_seam_extra_Msun':add,'extra_over_critical_primary':add/crit,'extra_over_remaining_primary':add/(crit-mstar),
        'predicted_stars_plus_control_over_critical_primary':(mstar+add)/crit,'extra_over_remaining_alternate':add/(critalt-mstar)})
out={'scope':'Archived sharp-seam v0.3/v0.5 exterior law, total-M weak spherical exterior approximation, gravity-only curvature load, A=1 and metric slip ratio=1 (not derived); positive shell to infinity as upper control for truncating same profile with no extra outer source. No measurement of seam/support/current, no branch fitting, not stacked with R1.',
 'commit_BHSM':'551ce2c8e4e672538e520629b0d4a8962cbba968','b_kpc':b*1e3,
 'circular_critical_Msun_zs0p777':crit,'circular_critical_Msun_zs2p187':critalt,'results':rows}
(p/'wgd_archived_seam_control.json').write_text(json.dumps(out,indent=2)+'\n')
for row in rows: print(row['curvature_radius_case'],row['logM'],'r*',row['rstar_kpc'],'Madd',row['conditional_seam_extra_Msun'],'fraction critical',row['extra_over_critical_primary'],'fraction remainder',row['extra_over_remaining_primary'])
