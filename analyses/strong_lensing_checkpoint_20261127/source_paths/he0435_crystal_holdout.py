"""A mass-free HE0435 cross-filter held-image benchmark.
Uses only observed angular coordinates and calibrated JWST science pixels.
Region selection uses approximate published image identities, not a mass map.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from snl_light_audit import fits_sci
from scipy.optimize import least_squares
import numpy as np,json
P=Path(__file__).resolve().parent
ast=json.loads((P.parent/'resolved_galaxies/he0435_courbin_astrometry.json').read_text())['astrometry']['data'][:4]
hst=np.array([[r['delta_alpha'],r['delta_delta']] for r in ast])
bands=dict(f115w=.040,f150w=.050,f277w=.090,f356w=.115)
ra0,dec0=69.5619,-12.28745
def coords(h,shape):
 y,x=np.indices(shape)
 u,v=x+1-h['CRPIX1'],y+1-h['CRPIX2']
 cd=np.array([[h[f'PC{i}_{j}']*h[f'CDELT{i}'] for j in (1,2)] for i in (1,2)])
 X,Y=np.deg2rad(cd@np.array([u.ravel(),v.ravel()]))
 d,c=np.deg2rad([h['CRVAL2'],h['CRVAL1']])
 den=np.cos(d)-Y*np.sin(d)
 a=c+np.arctan2(X,den)
 b=np.arctan2(np.sin(d)+Y*np.cos(d),np.sqrt(den**2+X**2))
 ad,bd=np.deg2rad([ra0,dec0])
 K=np.sin(b)*np.sin(bd)+np.cos(b)*np.cos(bd)*np.cos(a-ad)
 e=np.cos(b)*np.sin(a-ad)/K
 n=(np.sin(b)*np.cos(bd)-np.cos(b)*np.sin(bd)*np.cos(a-ad))/K
 return (np.rad2deg(np.stack([e,n],1))*3600).reshape(*shape,2)
def fit_all(b,rad,profile,bg):
 d,h=fits_sci(P.parent/'common_host_20261126'/f'{b}.fits'); X=coords(h,d.shape); w=bands[b]
 res=[]
 for seed in hst+[1.26,.195]+[1.1706,.5665]: # summed approximate location of A, relative sky origin
  # Use catalog centers only to locate the image patch, then fit each band separately.
  ux=X-seed; kk=(np.linalg.norm(ux,axis=-1)<rad)&np.isfinite(d)&(d>0)
  u=ux[kk]; z=np.array(d[kk],dtype=float); i,j=u[z.argmax()]; z/=z.max()
  if bg==1: V=np.c_[np.ones(len(u)),u/rad]
  else: V=np.c_[np.ones(len(u)),u/rad,(u[:,0]/rad)**2,(u[:,1]/rad)**2,u[:,0]*u[:,1]/rad**2]
  def calc(t):
   r=u-t[:2]; s=(r[:,0]/t[2])**2+(r[:,1]/t[3])**2
   f=np.exp(-s/2) if profile=='gaussian' else (1+s)**(-2.5)
   B=np.c_[f,V]; return B@np.linalg.lstsq(B,z,rcond=None)[0]-z
  sol=least_squares(calc,[i,j,w*.52,w*.52],bounds=([-.16,-.16,w*.19,w*.19],[.16,.16,w*1.25,w*1.25]),max_nfev=100)
  assert np.max(np.abs(sol.x[:2]))<.158,(b,seed)
  res.append((sol.x[:2]+seed).tolist())
 return np.array(res)
def map_pred(x,y,z,mode):
 a=x-x.mean(0); b=y-y.mean(0)
 if mode=='translate': M=np.eye(2)
 elif mode=='similarity':
  U,s,V=np.linalg.svd(a.T@b); Q=np.diag([1.,np.linalg.det(U@V)])
  M=U@Q@V*(s@Q.diagonal())/np.sum(a*a)
 else:M=np.linalg.lstsq(a,b,rcond=None)[0]
 return (z-x.mean(0))@M+y.mean(0)
sweep=[]
for r in (.15,.19,.24):
 for shape in ('gaussian','moffat'):
  for bg in (1,2):
   pos={b:fit_all(b,r,shape,bg) for b in bands}; pos['hst']=hst
   row={}
   for a,b in [('f115w',x) for x in bands if x!='f115w']+[('hst',x) for x in bands]:
    pair={}
    for k in range(4):
     train=np.arange(4)!=k; pair['ABCD'[k]]={}
     for name in ('translate','similarity','affine'):
      p=map_pred(pos[a][train],pos[b][train],pos[a][k],name)
      pair['ABCD'[k]][name]=((pos[b][k]-p)*1000).tolist()
    row[f'{a}_to_{b}']=pair
   sweep.append(dict(radius=r,profile=shape,background_degree=bg,positions={b:v.tolist() for b,v in pos.items()},predictions=row))
summary={}
for p in sweep[0]['predictions']:
 summary[p]={}
 for im in 'ABCD':
  summary[p][im]={}
  for z in ('translate','similarity','affine'):
   v=np.array([r['predictions'][p][im][z] for r in sweep])
   summary[p][im][z]=dict(range_mas=np.percentile(np.linalg.norm(v,axis=1),[0,50,100]).tolist(),median_EN_mas=np.median(v,axis=0).tolist())
for p,s in summary.items():
 print(p,{i:{k:np.round(v['range_mas'],2).tolist() for k,v in ss.items()} for i,ss in s.items()})
P.joinpath('he0435_crystal_holdout.json').write_text(json.dumps(dict(summary=summary,sweep=sweep,limitations='cross-band predicting previously identified image, not new lens images; instrument fit variants not independent; no interpretation of mass or BHSM'),indent=2)+'\n')
