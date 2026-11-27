"""No mass or envelope equations: surface brightness of an outer clump held out."""
from pathlib import Path
import numpy as np,json,itertools
from scipy.ndimage import map_coordinates,gaussian_filter
from snl_light_audit import sky_cutout
P=Path(__file__).resolve().parent
land=json.loads((P/'hamilton_landmark_holdout.json').read_text())
native=json.loads((P/'hamilton_native_outer.json').read_text())
means={k:(np.array(v[:6])-[612.5,866.5])*[-1/67,-2.2/67] for k,v in land['marker_pixels'].items()}

def mapping(a,b,mode):
 x,y=means[a],means[b]; c,e=x.mean(0),y.mean(0)
 if mode=='affine': K=np.linalg.lstsq(x-c,y-e,rcond=None)[0]
 else:
  u,s,v=np.linalg.svd((x-c).T@(y-e))
  q=np.diag([1,(-1 if mode=='mirror' else 1)*np.linalg.det(u@v)])
  K=u@q@v*(s@q.diagonal())/np.sum((x-c)**2)
 return c,e,K

def scat(a,n):
 return np.sqrt(np.mean((a-n)**2))
out=[]
for f in sorted((P/'hamilton_inputs').glob('*fits')):
 dx=.064125
 x,d=sky_cutout(f,337.54041667,-8.161111111,dx,23)
 pix=native[f.name]; om={k:np.array(o) for k,o in pix['translation'].items()}
 b0=np.array(pix['peak_fit']['A'][0]) # A only; B clump coordinate never read
 t=np.arange(-19,20)*dx; xx,yy=np.meshgrid(t,t); xy=np.stack([xx,yy],axis=-1); rr=np.linalg.norm(xy,axis=-1)
 def sample(X):
  v=(X-x[0])/dx
  return map_coordinates(d,[v[...,1],v[...,0]],order=1)
 def subtract(im,rlo,rhi):
  M=np.stack([np.ones_like(xx),xx,yy],axis=-1); ann=(rr>=rlo)&(rr<rhi)
  z=im[ann]; A=M[ann]; keep=np.ones(len(z),bool)
  for _ in range(4):
   q=np.linalg.lstsq(A[keep],z[keep],rcond=None)[0]
   er=z-A@q; med=np.median(er[keep]); sig=max(1e-9,1.4826*np.median(abs(er[keep]-med)))
   keep=abs(er-med)<3*sig
  return im-M@q
 a,b='A','B'; c,e,J=mapping(a,b,'mirror')
 anchor=(b0-om[a]-c)@J+e+om[b]
 # Fix the target footprint exclusively from source, hypothesized mirror
 # and inner landmarks; all comparator predictions scored on the same pixels.
 obs_raw=sample(anchor+xy)
 for R,ann,sig in itertools.product([.38,.46,.54],[(.66,1.04),(.76,1.12)],[.052,.067,.082]):
  O=subtract(obs_raw,*ann); obs=gaussian_filter(O,sig*np.sqrt(abs(np.linalg.det(J)))/dx)
  mask=rr<R
  y=obs[mask]
  line={}
  for label in ('mirror','affine','rotate','one_clump'):
   c,e,K=mapping(a,b,'mirror' if label=='one_clump' else label)
   z=(anchor+xy-e-om[b])@np.linalg.inv(K)+c+om[a]
   # Do not learn gain or offset from target patch. Surface brightness,
   # not total flux, is copied. Smooth all templates by the native B PSF proxy.
   pred_raw=sample(z)
   if label=='one_clump':
    amp,sigA=pix['peak_fit']['A'][1:3]
    pres=amp*np.exp(-.5*np.sum((z-b0)**2,axis=-1)/sigA**2)
   else:
    pres=subtract(pred_raw,*ann)
   ave=gaussian_filter(pres,sig/dx)[mask]
   # The baseline and controls explain no light where they predict none.
   line[label]=dict(gain_vs_zero=1-float(np.sum((y-ave)**2)/np.sum(y*y)), corr=float(np.corrcoef(y,ave)[0,1]),
    aperture_flux_pred_over_obs=float(ave.sum()/y.sum()),rms=float(scat(y,ave)))
  out.append(dict(filter=f.name.split('_')[5],R=R,annulus=ann,sigma=sig,count=int(mask.sum()),anchor_EN=anchor.tolist(),fit=line))
(P/'hamilton_pixel_holdout.json').write_text(json.dumps(out,indent=2)+'\n')
for f in sorted(set(r['filter'] for r in out)):
 for m in ('mirror','affine','rotate','one_clump'):
  print(f,m,{k:np.round(np.percentile([r['fit'][m][k] for r in out if r['filter']==f],[0,50,100]),3).tolist() for k in ('gain_vs_zero','corr','aperture_flux_pred_over_obs')})
