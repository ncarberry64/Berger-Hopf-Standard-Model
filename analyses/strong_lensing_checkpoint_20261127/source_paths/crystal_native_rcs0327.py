"""Frozen six-vs-wide RCS0327 comparison on calibrated HLA pixels.
Use Fig 1 for ID and seeds only. Primary F606W; ±2 aperture perturbations and
F390W/F814W sensitivity; d/f separate, as flagged by the source.
"""
from pathlib import Path
import json
import numpy as np
from scipy.spatial import ConvexHull
from scipy.ndimage import gaussian_filter
from scipy.optimize import least_squares
from rcs0327_inputs.read_hla import fits
P=Path(__file__).parent
ns={'__file__':str(P/'crystal_blocked_rule.py')}
exec((P/'crystal_blocked_rule.py').read_text().split('out={}\nfor name')[0],ns)
D=json.loads((P/'rcs0327_sharon_fig1.json').read_text())
def seedmap(i):
 if i=='3':
  F=[[597,111],[644,615],[897,260]]
  I=[[205,199],[216,311],[273,235]]
  offset=[940,1339]
 else:
  F=[[700,194],[611,213],[495,268]]
  I=[[210,228],[196,232],[179,238]]
  offset=[730,349]
 a,b=np.array(F),np.array(I)
 factor=(a-a.mean(0)).ravel()@(b-b.mean(0)).ravel()/np.sum((a-a.mean(0))**2)
 return {v:(np.array(z)-a.mean(0))*factor+b.mean(0) for v,z in D[i].items()},offset
def hdr(b):
 return fits(P/'rcs0327_inputs'/f'hla_{b}.fits')
def w(h):
 cd=3600*np.array([[float(h[f'CD{i}_{j}']) for j in (1,2)] for i in (1,2)])
 rp=np.array([float(h[f'CRPIX{i}'])-1 for i in (1,2)])
 return cd,rp
def band_seed(h0,h,p):
 # All three CRVALs coincide to roundoff; assert this before using their shared tangent plane.
 np.testing.assert_allclose([float(h0[k]) for k in ('CRVAL1','CRVAL2')],[float(h[k]) for k in ('CRVAL1','CRVAL2')],atol=1e-9,rtol=0)
 a,b=w(h0); c,d=w(h)
 return np.linalg.solve(c,a@(p-b))+d
def centroid(a,seed,R):
 X,Y=np.meshgrid(np.arange(-R,R+1),np.arange(-R,R+1))
 ix,iy=np.rint(seed).astype(int)
 z=np.asarray(a[iy-R:iy+R+1,ix-R:ix+R+1],float)
 Z=gaussian_filter(np.nan_to_num(z),.85)
 m=(X+ix-seed[0])**2+(Y+iy-seed[1])**2<=4.0**2
 peak=np.unravel_index(np.argmax(np.where(m,Z,-np.inf)),Z.shape)
 x0,y0=X[peak],Y[peak]
 region=(X-x0)**2+(Y-y0)**2<=(R-2)**2
 wing=(X-x0)**2+(Y-y0)**2>=(R-1)**2
 bg=np.median(z[wing]); sig=max(1.4826*np.median(abs(z[wing]-bg)),1e-8)
 X,Y,z=X[region],Y[region],z[region]
 def fun(t):
  x,y,sx,sy,amp,bg,bx,by=t
  return (bg+bx*X+by*Y+amp*np.exp(-.5*((X-x)**2/sx**2+(Y-y)**2/sy**2))-z)/sig
 p=least_squares(fun,[x0,y0,1.6,1.6,max(np.max(z)-bg,1e-8),bg,0,0],bounds=([x0-1.8,y0-1.8,.65,.65,0,-np.inf,-np.inf,-np.inf],[x0+1.8,y0+1.8,4,4,np.inf,np.inf,np.inf,np.inf]),max_nfev=90,loss='soft_l1')
 xy=p.x[:2]+[ix,iy]
 return dict(xy=xy.tolist(),snr=float(p.x[4]/sig),width=p.x[2:4].tolist(),seed=seed.tolist(),converged=bool(p.success))
def transfer(sets,knots,blocks):
 rr=[]
 for i,j in [('3','4'),('4','3')]:
  X,Y=[np.array([sets[t][k] for k in knots]) for t in (i,j)]
  for k,x in enumerate(X):
   order=np.argsort(np.sum((X-x)**2,axis=1),kind='stable'); order=order[order!=k]
   for block in blocks:
    ids=order[block:]; l=ids[:6]; assert len(l)==6
    p,q=[ns['fit'](X[t],Y[t],x) for t in (l,ids)]
    alter=Y.copy(); alter[[k,*order[:block]]]+=9e3
    np.testing.assert_array_equal(p,ns['fit'](X[l],alter[l],x))
    np.testing.assert_array_equal(q,ns['fit'](X[ids],alter[ids],x))
    inside=lambda t: bool(np.max(ConvexHull(X[t]).equations@np.r_[x,1])<=1e-9)
    rr.append(dict(knot=knots[k],direction=[i,j],block=block,inside=inside(ids),inside_local=inside(l),local=float(np.linalg.norm(p-Y[k])),wide=float(np.linalg.norm(q-Y[k])),mid=float(np.linalg.norm((p+q)/2-Y[k])),spread=float(np.linalg.norm(p-q)),n_wide=len(ids)))
 return dict(scores=ns['scores'](rr),rows=rr)
def extract():
 h0,_=hdr('f606w'); out={}
 for b in ('f606w','f390w','f814w'):
  h,a=hdr(b)
  for R in (6,7,8):
   m={}
   for i in ('3','4'):
    S,off=seedmap(i)
    m[i]={k:centroid(a,band_seed(h0,h,np.array([x+off[0],off[1]-y])),R) for k,(x,y) in S.items()}
   out[f'{b}_{R}']=m
 return out
if __name__=='__main__':
 (P/'rcs0327_native_centroids.json').write_text(json.dumps(extract(),indent=2)+'\n')
def evaluate(out):
 keys=[k for k in D['3'] if k not in D['low_quality']]
 assert len(keys)==8
 quality={}
 for k in keys:
  quality[k]=max(float(np.linalg.norm(np.array(out[v][i][k]['xy'])-out['f606w_7'][i][k]['xy']))*0.03962
    for v in out for i in ('3','4'))
 strict=[k for k in keys if quality[k]<=0.1]
 d={'strict_stability_0.1_arcsec':strict,'max_coordinate_perturbation_arcsec':quality,'runs':{}}
 for v,o in out.items():
  h,_=hdr(v.split('_')[0]); cd,rp=w(h)
  sets={i:{k:cd@(np.array(q['xy'])-rp) for k,q in t.items()} for i,t in o.items()}
  d['runs'][v]=transfer(sets,keys,[0])
 if len(strict)>=8:
  h0,_=hdr("f606w"); cd,rp=w(h0)
  d['strict_f606w']=transfer({i:{k:cd@(np.array(q['xy'])-rp) for k,q in t.items()} for i,t in out['f606w_7'].items()},strict,[0])
 return d
if __name__=='__main__':
 d=evaluate(json.loads((P/'rcs0327_native_centroids.json').read_text()))
 (P/'crystal_native_rcs0327.json').write_text(json.dumps(d,indent=2)+'\n')
 print('strict',d['strict_stability_0.1_arcsec'],d['max_coordinate_perturbation_arcsec'])
 for name,q in d['runs'].items():
  print(name)
  for key in ('0_all','0_inside_local','0_outside_local'):
   s=q['scores'].get(key)
   if s:print(key,s['n'],[[round(s[r][m],4) for m in ('median','rms','max')] for r in ('local','wide','mid')])
  if name=='f606w_7': print([(r['direction'],r['knot'],round(r['local'],3)) for r in q['rows'] if r['inside_local']])
