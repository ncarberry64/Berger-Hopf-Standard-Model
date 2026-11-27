"""Independent FastSpecFit stellar masses and dispersion-based SIS sensitivity, no fit to Jackpot."""
import numpy as np
from pathlib import Path
import json
from scipy.integrate import quad
from catalog import tables,lens
h=.7; om=.3
c=299792.458; G=4.300917270e-6; asec=206264.806247
zs=5.975
theta=np.array([[3.,-1.91],[-1.03,.87]])
T=tables(Path('fastspec.fits'))
A=T['METADATA']; B=T['SPECPHOT']
def chi(z):return c/(100*h)*quad(lambda x:(om*(1+x)**3+1-om)**-.5,0,z)[0]
out={}
for convention in (-1,1):
 for id in [39628027746848157,39628027746848720]:
  a,=A[A['TARGETID']==id]; b,=B[B['TARGETID']==id]
  z=a['Z']; dl=chi(z)/(1+z)*1e3; w=1-chi(z)/chi(zs)
  pos=3600*np.array([convention*(a['RA']-lens[0])*np.cos(np.deg2rad(lens[1])), a['DEC']-lens[1]])
  v=theta-pos; s=np.linalg.norm(v,axis=1)
  m=10**float(b['LOGMSTAR'])/h**2
  sigma=float(b['VDISP']); err=float(b['VDISP_IVAR'])**-.5
  k=4*G*m/c**2/dl*w*asec**2
  vec_star=np.diff(k*v/s[:,None]**2,axis=0)[0]
  compact_bound=k*np.linalg.norm(theta[0]-theta[1])/min(s)**2
  b_sis=4*np.pi*(sigma/c)**2*w*asec
  vec_sis=np.diff(b_sis*v/s[:,None],axis=0)[0]
  sis_bound_hi=4*np.pi*((sigma+2*err)/c)**2*w*asec*np.linalg.norm(theta[0]-theta[1])/min(s)
  out.setdefault(str(convention),[]).append(dict(id=id,sep_arcsec=float(np.linalg.norm(pos)),z=z,mstar=m,logmstar_h1=float(b['LOGMSTAR']),err_dex=float(b['LOGMSTAR_IVAR'])**-.5,sigma=sigma,err=err,star_mas=(1e3*vec_star).tolist(),star_bound_mas=1e3*compact_bound,sis_mas=(1e3*vec_sis).tolist(),sis_2sigma_geom_bound_mas=1e3*sis_bound_hi))
for k,rr in out.items():
 print('axes',k)
 for r in rr:print(r)
 print('joint',np.linalg.norm(np.sum([r['star_mas'] for r in rr],axis=0)),np.linalg.norm(np.sum([r['sis_mas'] for r in rr],axis=0)))
Path('neighbor_bend.json').write_text(json.dumps(out,indent=2)+'\n')
