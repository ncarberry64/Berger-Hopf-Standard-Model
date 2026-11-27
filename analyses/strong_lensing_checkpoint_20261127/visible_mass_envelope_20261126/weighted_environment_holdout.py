"""Held-out projected mass; environmental proxy from TDCOSMO environment release.
No fit to Jackpot. Same training sets and host/aperture law in each comparison.
"""
import csv,json
import numpy as np
from scipy.optimize import least_squares
from scipy.special import gammainc
from pathlib import Path
p=Path(__file__).resolve().parent
def main():
 d={}
 for r in csv.DictReader((p/'external_weak/tdcosmo_LineOfSightData.csv').open()):
  try:
   d[r['#name']]=[float(r[k]) for k in ['Nmed','NoverRmed','oS10','oD1','zd']]
  except (ValueError,TypeError):continue
 t=json.loads((p/'slacs_results.json').read_text())['rows']
 t=[r for r in t if '0946+1006' not in r['name'] and r['name'].replace('−','-') in d]
 env=np.array([d[a['name'].replace('−','-')] for a in t])
 assert np.all(abs(env[:,-1]-np.array([a['z'] for a in t]))<.0011)
 assert np.all(env>0)
 X=np.array([[1,a['logSalp']-11.5,np.log(a['Re']/5),a['z']-.2] for a in t])
 m=np.array([a['L']-a['logSalp'] for a in t])
 x=np.array([a['R']/a['Re'] for a in t])
 s=gammainc(8,7.6692494425*x**.25)
 rz=json.loads((p/'frozen_radial_transfer.json').read_text())
 f=(x/rz['x0'])**rz['eta']
 one=X[:,:1]; y=np.log(env[:,:4]/[63.,1.028768,1.,1.])
 feats={'base':X,'plain_count':np.c_[X,y[:,0]],'weighted_count':np.c_[X,y[:,1]],
        'plain_and_weighted':np.c_[X,y[:,:2]],'lens_slice_counts':np.c_[X,y[:,2:]],
        'weighted_and_slice':np.c_[X,y[:,1:]]}
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
 (p/'weighted_environment_holdout.json').write_text(json.dumps(dict(n=n,models=res,sample=[a['name'] for a in t]),indent=2)+'\n')
if __name__=='__main__':main()
