"""Axisymmetric Jackpot inner-normalized, outer radial holdout, not full astrometry."""
import json,numpy as np
from itertools import product
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import gammainc
from pathlib import Path
from functools import lru_cache
ZL,Z1,Z2=.222,.609,2.035
c,G=299792.458,4.30091727e-6
xs=np.pi/648000
@lru_cache(None)
def D(a,b,Om=.3):
 return (c/70)/(1+b)*quad(lambda z:(Om*(1+z)**3+1-Om)**-.5,a,b)[0]
def dpie(t,imf):
 a,b=np.array([[.066,.50],[.082,6.05]]).T
 m=10**np.array([11.13,11.52] if imf=='Salpeter' else [10.85,11.27])
 return float(np.sum(m*(np.hypot(t,a)-a-np.hypot(t,b)+b)/(b-a)))
def dev(t,imf):
 return 10**(11.59 if imf=='Salpeter' else 11.34)*gammainc(8,7.6692494425*(t/2.35)**.25)
def trial(profile,imf,ri,rs,z2,p2,cen,Om):
 K= D(0,ZL,Om)*1000*xs
 b=lambda z: D(ZL,z,Om)/D(0,z,Om)
 # Reduced angular deflection in arcsec from projected primary aperture mass.
 def unit(t,z):return 4*G/c**2*b(z)/(K*t*xs)
 Mi=ri/unit(ri,Z1)
 star=lambda t:profile(t,imf)+cen
 ei=Mi-star(ri)
 assert ei>0
 assert p2>0
 shapes={'traces_stars':lambda t:profile(t,imf)/profile(ri,imf),
         'doubled_light_scale':lambda t:profile(t/2,imf)/profile(ri/2,imf),
         'slope_1p5':lambda t:(t/ri)**1.5,
         'slope_2_sheet_limit':lambda t:(t/ri)**2,
         'no_added_mass_outside_inner':lambda t:1.0}
 out={}
 for name,f in shapes.items():
  # Source plane 1 carries an independent effective SIS deflection strength,
  # at this centered positive near-axis approximation and outside inner critical curve.
  def residual(t): return unit(t,z2)*(star(t)+ei*f(t))+p2-t
  rr=np.linspace(ri+1e-5,5.,201)
  rt=[brentq(residual,l,r) for l,r in zip(rr[:-1],rr[1:]) if residual(l)>=0>residual(r)]
  out[name]=dict(predicted_R2_arcsec=(float(rt[-1]) if rt else None),
    main_alpha_at_observed_R2=unit(rs,z2)*(star(rs)+ei*f(rs)),
    residual_deflection_at_observed_R2=float(residual(rs)),
    normalized_envelope_at_R2=f(rs))
 req= (rs-p2)/unit(rs,z2)-star(rs)
 if req<=0: raise RuntimeError(req)
 return dict(R1=ri,R2=rs,central_mass=cen,Om=Om,first_source_SIS=p2,M1=Mi,env1=ei,env2=req,
     env1_to_stars=ei/star(ri),env2_to_stars=req/star(rs),fraction_outer_annulus_of_env2=1-ei/req,
     implied_growth_slope=np.log(req/ei)/np.log(rs/ri),R1_kpc=ri*K,R2_kpc=rs*K,variants=out,
     z2=z2,photo=profile.__name__,imf=imf)
def main():
 central=[trial(p,I,1.43,2.07,Z2,.161,0,.3) for p,I in product([dpie,dev],['Salpeter','Chabrier'])]
 stress=[trial(p,I,r1,r2,z2,b,cen,om) for p,I,r1,r2,z2,b,cen,om in product([dpie,dev],['Salpeter','Chabrier'],[1.42,1.43,1.44],[2.05,2.07,2.09],[2.035],[.14,.161,.186],[0,8e9],[.27,.33])]
 extra=[trial(p,'Salpeter',1.43,2.07,Z2,b,0,.3) for p,b in product([dpie,dev],[.000001,.10,.22])]
 Path('jackpot_radial_holdout.json').write_text(json.dumps(dict(central=central,stress=stress,first_plane_nuisance_wide=extra),indent=2)+'\n')
 for v in central:
  print(v['photo'],v['imf'],[round(v[k],3) for k in ('R1_kpc','R2_kpc','env1_to_stars','env2_to_stars','fraction_outer_annulus_of_env2','implied_growth_slope')])
  print([(k,w['predicted_R2_arcsec'],w['main_alpha_at_observed_R2']) for k,w in v['variants'].items()])
 for I in ['Salpeter','Chabrier']:
  V=[x for x in stress if x['imf']==I]; print(I,[(k, min(x[k] for x in V),max(x[k] for x in V)) for k in ['implied_growth_slope','fraction_outer_annulus_of_env2','env1_to_stars','env2_to_stars']])
  for k in V[0]['variants']:
   rr=[x['variants'][k]['predicted_R2_arcsec'] for x in V];rr=[s for s in rr if s is not None]
   print(k,len(rr),None if not rr else (min(rr),max(rr)))
if __name__=='__main__':main()
