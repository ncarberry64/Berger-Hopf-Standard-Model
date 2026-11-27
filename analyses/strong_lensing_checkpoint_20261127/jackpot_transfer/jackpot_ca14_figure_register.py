"""Approximate chart registration using published red crosses and F814W morphology."""
from pathlib import Path
from PIL import Image
from scipy.ndimage import map_coordinates,gaussian_filter
from scipy.optimize import minimize
import json,numpy as np
from astropy.io import fits
from astropy.wcs import WCS
P=Path(__file__).resolve().parent
src=P/'jackpot_registered_knot_control.py'
aux={'__file__':str(src),'__name__':'base'}
exec(compile(src.read_text().split('\nout={}',1)[0],str(src),'exec'),aux)
g=aux['g']; obs=aux['obs']; th=g['th']; K=lambda r:.5*(2-1.027)*(g['R0']/r)**1.027
img=np.array(Image.open('/tmp/ca14vis-3.png').convert('RGB'))*1.
# Chart pixel zero and 20-pixel tick pitch digitized from x/y axes of Figure 2.
def figpix(v):return (473.-3.23*v[:,1],93.5+3.23*v[:,0])
crosses=np.array([[70.,74.],[32.,31.],[41.,25.],[54.,22.]])
p0=np.array([51.885,51.429])
xx,yy=np.meshgrid(np.arange(6.,99.),np.arange(6.,99.))
xy=np.column_stack([xx.ravel(),yy.ravel()])
rr=np.linalg.norm(xy-p0,axis=1)
a=np.array([map_coordinates(img[...,k],figpix(xy),order=1) for k in range(3)]).T
mask=(rr>=21)&(rr<=46)&((a.max(axis=1)-a.min(axis=1))<5)
xy=xy[mask]; r=rr[mask]
y=-a[mask].mean(axis=1)
# Use residual contrast, subtract radial median to suppress foreground galaxy light.
with fits.open(obs/'u_phot/f814w.fits') as h:
 im=h[0].data.astype(float); wo=WCS(h[0].header)
 cp=np.array(wo.all_world2pix(146.73617048,10.11469530,0))
I=gaussian_filter(np.nan_to_num(im),.6)
iy,ix=np.indices(I.shape)
rad=np.hypot(ix-cp[0],iy-cp[1])
def detrend(ar,val):
    bins=np.floor(ar).astype(int)
    ret=val.copy()
    for b in np.unique(bins):ret[bins==b]-=np.median(val[bins==b])
    return ret
J=detrend(rad.ravel(),I.ravel()).reshape(I.shape)
yt=detrend(r,y);yt=yt/np.linalg.norm(yt)
def calc(a,h,coor):
    t=np.deg2rad(a[0]); R=np.array([[np.cos(t),-np.sin(t)],[np.sin(t),np.cos(t)]])
    return ((coor-p0)*[1,h])@R.T
def score(a,h):
    X=calc(a,h,xy)+cp+a[1:]
    v=map_coordinates(J,[X[:,1],X[:,0]],order=1)
    return -(v@yt)/max(np.linalg.norm(v),1e-10)
rows=[]
for h in (-1,1):
    aa=np.arange(0,360,2.)
    st=sorted(aa,key=lambda t:score([t,0,0],h))[:8]
    fitsc=[minimize(score,[t,0,0],args=(h,),method='Powell',bounds=[(t-9,t+9),(-3.,3.),(-3.,3.)]) for t in st]
    f=min(fitsc,key=lambda o:o.fun)
    x=f.x
    # WCS shows north up, east left, 0.05 arcsec/pixel.
    E=calc(x,h,crosses)*np.array([-.05,.05])
    def orient(a):
      m=np.array([np.cos(np.deg2rad(a)),np.sin(np.deg2rad(a))])*[1,h]
      t=np.deg2rad(x[0]); R=np.array([[np.cos(t),-np.sin(t)],[np.sin(t),np.cos(t)]])
      v=(R@m)*[-1,1]
      return float(np.degrees(np.arctan2(v[1],v[0])))
    # Trial assumes CA14 angles are mathematical angles in their displayed chart.
    U=g['matrix'](orient(-27.20)); sh=U.T@np.diag([.069,-.069])@U
    def main(t):return np.array([g['ell'](v,.946,orient(30.6),K) for v in t])+t@sh
    c=(E-main(E)).mean(axis=0)
    v=th-main(th)-c; u=v/np.linalg.norm(v,axis=1)[:,None]
    hist=th-1.49*main(th)-1.22*.161*u
    delta=hist[1]-hist[0]
    rows.append(dict(hand=h,registration=x.tolist(),correlation=-f.fun,red_cross_EN_arcsec=E.tolist(),source1_center=c.tolist(),
         forecast_B_minus_A_arcsec=delta.tolist(),norm_arcsec=float(np.linalg.norm(delta))))
(P/'jackpot_ca14_figure_register.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
