"""Held-out projected mass; environmental proxy from TDCOSMO environment release.
No fit to Jackpot. Same training sets and host/aperture law in each comparison.
"""
import csv,json
import numpy as np
from scipy.optimize import least_squares
from scipy.special import gammainc
from scipy.integrate import quad
from pathlib import Path
p=Path(__file__).resolve().parent
def main():
 catalog=json.loads((p/'external_weak/sdss_lens_environment.json').read_text())
 env={}
 for k,v in catalog.items():
  if not isinstance(v['rows'],list):continue
  z=v['z']; da=299792.458/70*quad(lambda q:(.3*(1+q)**3+.7)**-.5,0,z)[0]/(1+z)
  mass_weight=[]; dist=[]
  verified=False
  for r in v['rows']:
   ra,de,zz=map(float,(r['ra'],r['dec'],r['z']))
   aa=np.hypot((ra-v['ra'])*np.cos(np.deg2rad(v['dec'])),de-v['dec'])
   if aa*3600<3 and abs(zz-z)<.002:verified=True
   if aa*3600<10 or abs(zz-z)*299792.458/(1+z)>1000:continue
   R=np.deg2rad(aa)*da
   if R>1.:continue
   try: mag=float(r['modelMag_r'])
   except (ValueError,TypeError): continue
   if not 12<mag<19.3:continue
   mr=mag-5*np.log10(da*(1+z)**2)-25 # proxy, no K or dust correction
   if mr>-22.:continue
   mass_weight.append(10**(-.4*(mr+22)))
   dist.append(R)
  if verified:
   env[k]=[len(mass_weight),sum(mass_weight),sum(a/max(.1,r) for a,r in zip(mass_weight,dist))]
 t=json.loads((p/'slacs_results.json').read_text())['rows']
 t=[r for r in t if '0946+1006' not in r['name'] and r['name'].replace('−','-') in env]
 E=np.array([env[a['name'].replace('−','-')] for a in t])
 print('counts',len(t),np.sum(E[:,0]>0),int(E[:,0].sum()),'jackpot',env.get('SDSSJ0946+1006'))
 X=np.array([[1,a['logSalp']-11.5,np.log(a['Re']/5),a['z']-.2] for a in t])
 m=np.array([a['L']-a['logSalp'] for a in t])
 x=np.array([a['R']/a['Re'] for a in t])
 s=gammainc(8,7.6692494425*x**.25)
 rz=json.loads((p/'frozen_radial_transfer.json').read_text())
 f=(x/rz['x0'])**rz['eta']
 y=np.log1p(E)
 feats={'base':X,'spec_count':np.c_[X,y[:,0]],'spec_luminosity':np.c_[X,y[:,1]],'spec_distance_weighted_luminosity':np.c_[X,y[:,2]]}
 res={};n=len(m)
 for name,A in feats.items():
  def error(b,i): return np.log10(s[i]+f[i]*np.exp(np.clip(A[i]@b,-22,22)))-m[i]
  def fit(i):return least_squares(error,np.r_[-2.5,np.zeros(A.shape[1]-1)],args=(i,),bounds=(-10,10)).x
  errs=np.array([error(fit(np.arange(n)!=i),i) for i in range(n)])
  res[name]=dict(n=n,rms_dex=np.linalg.norm(errs)/np.sqrt(n),med_abs_dex=np.median(abs(errs)),errors=errs.tolist())
 b=np.array(res['base']['errors'])
 rng=np.random.default_rng(1364); ix=rng.integers(0,n,(5000,n))
 for name,r in res.items():
  a=np.array(r['errors']); d=np.sqrt(np.mean(a[ix]**2,axis=1))-np.sqrt(np.mean(b[ix]**2,axis=1))
  r['descriptive_paired_rms_difference_quantiles_dex']=np.quantile(d,[.16,.5,.84]).tolist()
  print(name,r['n'],r['rms_dex'],r['med_abs_dex'],r['descriptive_paired_rms_difference_quantiles_dex'])
 (p/'luminosity_environment_holdout.json').write_text(json.dumps(dict(n=n,models=res,catalog_features=env,sample=[a['name'] for a in t]),indent=2)+'\n')
if __name__=='__main__':main()
