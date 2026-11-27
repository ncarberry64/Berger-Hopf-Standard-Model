"""Radial footprint of existing JWST host masks and sheet-subtracted front-plane sensitivity."""
from pathlib import Path
import json
import numpy as np
from scipy.integrate import quad
from scipy.interpolate import PchipInterpolator
from scipy.signal import fftconvolve
from score import read,design,moff,th
audit=Path('../bhsm_environment_audit')
c=json.loads((audit/'he0435_halo_calibration.json').read_text())
sheets=json.loads((audit/'he0435_outer_shape_vs_sheet.json').read_text())
re,Mref=c['RE_kpc'],c['projected_DM_Msun_at_RE']
rs,M0=c['runs'][1]['scale_kpc'],c['runs'][1]['M0']
D=re/1.182
frozen=json.loads(Path('f356w_matched.json').read_text())
def sig(r,R,kapmass):
    b=D*r
    def m(x):
        y=x/rs
        return M0*(np.log1p(y)-y/(1+y))
    # stable difference: just subtract the tail cut off by the zero-charge completion
    dm=-quad(lambda t:m(b/np.cos(t))*np.cos(t),np.arccos(b/R),np.pi/2,epsrel=1e-9)[0]
    return 1000*1.182**2/r*(dm-kapmass*(r/1.182)**2)/(Mref/.45)
sample=np.linspace(.45,2.66,491)
kernels={row['kpc']:PchipInterpolator(sample,[sig(r,row['kpc'],row['equivalent_sheet_at_RE_Msun']) for r in sample]) for row in sheets}
rows=[]
for band in ['f115w','f150w','f277w','f356w']:
    I,X,nuc,pix,good,_=read(Path(band+'.fits'))
    r=np.linalg.norm(X,axis=-1)
    distances=np.linalg.norm(X[...,None,:]-nuc,axis=-1)
    near=distances.argmin(axis=-1)
    ds=distances.min(axis=-1)
    F=max(.043,.034*int(band[1:-1])/100)*.93
    yy,xx=np.indices((35,35))-17
    pk=moff(np.hypot(xx,yy)*pix,2.7,F);pk/=pk.sum()
    for anchor in (False,True):
      for rad in (5,65):
        B,_,_=design(X,near,3,anchor,rad)
        for w in (.043,.065):
          nodes=next(np.array(k['nodes']) for k in frozen if k['anchor']==anchor and k['g4']==rad and k['width']==w and k['psf']==.93 and k['held']=='D')
          footprint=np.max([fftconvolve(np.exp(-.5*np.sum((B-z)**2,axis=-1)/w**2),pk,mode='same') for z in nodes],axis=0)
          clean=good&(r>.46)&(ds>max(.17,1.75*F))&(ds<.75)&(np.linalg.norm(B,axis=-1)<.33)&(footprint>.21)
          for label,mask in [('all_sectors',clean),('D',clean&(near==3))]:
            rr=r[mask]
            if len(rr)<20:continue
            rows.append(dict(band=band,anchor=anchor,rad=rad,w=w,mask=label,pixel_mas=pix*1000,count=len(rr),
                 radial_quantiles_arcsec=np.quantile(rr,[0,.05,.5,.95,1]).tolist(),
                 residual_quantiles_mas={str(R):np.quantile(np.abs(fun(rr)),[.5,.95,1]).tolist() for R,fun in kernels.items()}))
assert len(rows)>=48
rng=lambda a:[float(min(a)),float(max(a))]
print('Quasar radii',np.linalg.norm(th,axis=-1))
for label in ('all_sectors','D'):
  subset=[r for r in rows if r['mask']==label]
  print(label,len(subset), 'r bounds',rng([r['radial_quantiles_arcsec'][1] for r in subset]),rng([r['radial_quantiles_arcsec'][3] for r in subset]))
  for k in kernels:
    print(k,[rng([r['residual_quantiles_mas'][str(k)][i] for r in subset]) for i in (1,2)])
Path('outer_geometry_arc_leverage.json').write_text(json.dumps(rows,indent=2)+'\n')
