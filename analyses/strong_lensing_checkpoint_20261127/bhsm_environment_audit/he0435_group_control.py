"""Independent direct-gravity group sensitivity, not a native R1 joint solution."""
import json, math, sys
from pathlib import Path
import numpy as np
from scipy.special import gammainc, gammaincinv
p=Path(__file__).resolve().parent
sys.path.insert(0,str(p/'pinned_extra'))
from r1_background_geometry import D,G,speed,xrad
raw=json.loads((p/'he0435_courbin_astrometry.json').read_text())
positions={i['id']:np.array([i['delta_alpha'],i['delta_delta']]) for i in raw['astrometry']['data']}
observed=(np.array([positions[i] for i in 'ABCD'])-positions['G'])*xrad
g1=np.array([-2.585,-3.637])*xrad
group=np.array([(69.550841-69.5619)*np.cos(np.deg2rad(-12.28745)),(-12.272258+12.28745)])*np.pi/180
group*=67.1*xrad/np.linalg.norm(group)
zl,zp,zs=.4546,.7821,1.693
dl,dp,ds,dls,dlp,dps=[D(i,j) for i,j in [(0,zl),(0,zp),(0,zs),(zl,zs),(zl,zp),(zp,zs)]]
def norm(x):return np.linalg.norm(x,axis=-1)
def control(M,re,n,sig):
 def al(v):
  y=dl*v; r=norm(y)
  f=gammainc(2*n,gammaincinv(2*n,.5)*(r/re)**(1/n))
  m=4*G/speed**2*M*f/r**2
  off=v-group
  return m[...,None]*y+4*np.pi*(sig/speed)**2*off/norm(off)[...,None]
 xx=dp*(observed-g1)-dlp*(al(observed)-al(g1))
 beta=observed-dls/ds*al(observed)-dps/ds*(4*G/speed**2*10**10.9/norm(xx)**2)[:,None]*xx
 rms=math.sqrt(np.mean(norm(beta-beta.mean(axis=0))**2))/xrad
 return rms
cases=[('Zahedy area-circularized stellar profile',10**11.1,.0044*math.sqrt(.82),3.51),('Courbin Kroupa normalization, broader n=4 proxy',1.04e11*3.2,.00844,4.),('Courbin Salpeter normalization, broader n=4 proxy',1.04e11*4.6,.00844,4.)]
rows=[]
for sig in [0,370,470,570]:
 k=(4*np.pi*(sig/speed)**2*dls/ds)/(2*67.1*xrad)
 rows.append({'assumed_group_SIS_sigma_km_s':sig,'kappa_at_galaxy':k,
     'backprojection_RMS_arcsec':{label:control(M,re,n,sig) for label,M,re,n in cases}})
assert all(all(row['backprojection_RMS_arcsec'][label]>0.39 for label,*_ in cases) for row in rows)
print(json.dumps(rows,indent=2))
