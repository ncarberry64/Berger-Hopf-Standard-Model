"""Geometry-only feasibility test of affine source-plane PSF transfer."""
import itertools,json,numpy as np
from scipy.optimize import root
from score import design,th
from pathlib import Path
step=1e-4
ee={.134:'F115W/F150W',.209:'F277W',.246:'F356W'}
vv=np.stack([np.cos(np.arange(32)*np.pi/16),np.sin(np.arange(32)*np.pi/16)],axis=1)
out=[]
a=json.loads(Path('f356w_matched.json').read_text())
for j,k,p in itertools.product(range(4),[False,True],[5,65]):
 K=lambda t:design(t,j,3,k,p)[0]
 # Every branch uses the one fit to the A/B/C quasar astrometry.
 nodes=next(np.array(c['nodes']) for c in a if c['held']=='D' and c['anchor']==k and c['g4']==p and c['width']==.043 and c['psf']==.93)
 for s in nodes:
  r=root(lambda t:K(t)-s,th[j],tol=1e-10)
  C=r.x
  if np.linalg.norm(K(C)-s)>1e-7 or np.linalg.norm(C-th[j])>.75 or np.argmin(np.linalg.norm(C-th,axis=1))!=j:continue
  J=np.column_stack([(K(C+step*v)-K(C-step*v))/(2*step) for v in np.eye(2)])
  small=np.linalg.svd(J,compute_uv=False)
  for q,b in {**ee,.06:'F356W approx core HWHM'}.items():
   T=q*vv
   exact=K(C+T)-s; pred=T@J.T
   d=np.linalg.norm(exact-pred,axis=1);a0=np.linalg.norm(pred,axis=1)
   out.append(dict(anchor=k,branch='ABCD'[j],rad=p,radius=q,band=b,src=s.tolist(),theta=C.tolist(),singular=small.tolist(),rms_mas=float(1000*np.sqrt(np.mean(d*d))),max_mas=float(1000*d.max()),rel_rms=float(np.sqrt(np.mean(d*d)/np.mean(a0*a0))),min_rms_20mas=float(20*small[-1]),max_rms_20mas=float(20*small[0])))
Path('psf_map_geometry.json').write_text(json.dumps(out,indent=2)+'\n')
for Q in sorted({x['radius'] for x in out}):
 print(Q)
 for j in 'ABCD':
  v=[x for x in out if x['radius']==Q and x['branch']==j]
  print(j,len(v),{k:np.percentile([x[k] for x in v],[10,50,90]).round(3).tolist() for k in ['rms_mas','rel_rms','min_rms_20mas','max_rms_20mas']})
