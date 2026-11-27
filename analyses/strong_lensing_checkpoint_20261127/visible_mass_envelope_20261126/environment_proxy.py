"""Can independent galaxy counts predict held-out inner lensing masses? No group mass assigned."""
import json,re
from pathlib import Path
import numpy as np
from scipy.special import gammainc
from scipy.optimize import least_squares
T=Path('external_weak/env_slacs.txt').read_text().split('Summary of relevant measurements',1)[1]
by={}
for line in T.splitlines():
 q=line.split()
 if len(q)<10 or not re.fullmatch(r'J\d{4}[+−-]\d{4}',q[0]):continue
 if not all('±' in v for v in q[4:9]):continue
 z=float(q[1])
 a,b,c,d,e=map(lambda s:float(s.split('±')[0]),q[4:9])
 by['SDSS'+q[0].replace('-','−')]=[z,a/b,c/e]
S=json.loads(Path('slacs_results.json').read_text())['rows']
data=[(t,by[t['name']]) for t in S if t['name'] in by and '0946+1006' not in t['name']]
assert all(abs(t['z']-v[0])<.002 for t,v in data)
n=len(data)
M=np.array([t['L']-t['logSalp'] for t,v in data])
x=np.array([t['R']/t['Re'] for t,v in data])
s=gammainc(8,7.6692494425*x**.25)
jr=json.loads(Path('frozen_radial_transfer.json').read_text())
x0,eta=map(jr.get,('x0','eta'))
f=(x/x0)**eta
results={}
for k in ('constant','local','global','joint','mass_size_z','mass_size_z_and_local_global'):
 env=np.log(np.array([v[1:] for t,v in data]))
 phot=np.array([[t['logSalp']-11.5,np.log(t['Re']/5),t['z']-.2] for t,v in data])
 base=np.ones((n,1))
 terms={'constant':base,'local':np.c_[base,env[:,0]],'global':np.c_[base,env[:,1]],'joint':np.c_[base,env],
   'mass_size_z':np.c_[base,phot],'mass_size_z_and_local_global':np.c_[base,phot,env]}[k]
 def fn(p,i): return np.log10(s[i]+f[i]*np.exp(np.clip(terms[i]@p,-22,22)))-M[i]
 def fit(i):return least_squares(fn,np.r_[-2.5,np.zeros(terms.shape[1]-1)],args=(i,),bounds=(-10,10)).x
 e=np.array([fn(fit(np.arange(n)!=i),i) for i in range(n)])
 results[k]=dict(n=n,LOO_rms_dex=float(np.sqrt(np.mean(e**2))),LOO_med_abs_dex=float(np.median(abs(e))),coeff=fit(np.arange(n)).tolist())
print(json.dumps(results,indent=2))
Path('environment_proxy.json').write_text(json.dumps(dict(results=results,lenses=[t['name'] for t,v in data]),indent=2)+'\n')
