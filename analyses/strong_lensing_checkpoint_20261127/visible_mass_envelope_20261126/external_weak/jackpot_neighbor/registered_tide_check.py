"""Registered east/north coordinates, first-order separate neighboring planes."""
import numpy as np
from scipy.integrate import quad
from pathlib import Path
import json
from catalog import tables,lens
h=.7;c=299792.458;G=4.300917270e-6;asr=206264.806247
t=tables(Path('fastspec.fits'))
theta=np.array([[-3.,-1.91],[1.03,.87]])
diff=theta[0]-theta[1]
def chi(z):return c/70*quad(lambda zz:1/np.sqrt(.3*(1+zz)**3+.7),0,z)[0]
out={}
for zs in [.609,2.035,5.975]:
 for model in ['stars','SIS']:
  J=np.zeros((2,2)); full=np.zeros(2)
  for tt in [39628027746848157,39628027746848720]:
   a,=t['METADATA'][t['METADATA']['TARGETID']==tt];b,=t['SPECPHOT'][t['SPECPHOT']['TARGETID']==tt]
   x,y=3600*np.array([(a['RA']-lens[0])*np.cos(np.radians(lens[1])),a['DEC']-lens[1]])
   p=np.array([x,y]);R=np.linalg.norm(p);n=p/R
   z=a['Z'];w=1-chi(z)/chi(zs);dl=chi(z)/(1+z)*1000
   v=theta-p;s=np.linalg.norm(v,axis=1)[:,None]
   if model=='stars':
    coeff=4*G*10**float(b['LOGMSTAR'])/h**2/(c*c*dl)*w*asr**2
    alpha=coeff*v/s**2
    J+=coeff/R**2*(np.eye(2)-2*np.outer(n,n))
   else:
    coeff=4*np.pi*(float(b['VDISP'])/c)**2*w*asr
    alpha=coeff*v/s
    J+=coeff/R*(np.eye(2)-np.outer(n,n))
   full+=alpha[0]-alpha[1]
  convergence=np.trace(J)/2
  shear=J-convergence*np.eye(2)
  # S1/S2 use the identical A/B angular pair as a geometry fixture ONLY,
  # to isolate source-distance effects. They are not observations at those redshifts.
  row=dict(kappa=convergence,shear=[shear[0,0],shear[0,1]],full_mas=(full*1e3).tolist(),kappa_mas=(convergence*diff*1e3).tolist(),higher_order_mas=((full-J@diff)*1e3).tolist(),higher_order_norm_mas=np.linalg.norm(full-J@diff)*1e3)
  out[str(zs)+model]=row
  print(zs,model,row)
Path('registered_tide_check.json').write_text(json.dumps(out,indent=2)+'\n')
