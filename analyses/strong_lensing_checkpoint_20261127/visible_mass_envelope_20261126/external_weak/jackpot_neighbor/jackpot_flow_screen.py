"""No lensing input. Test projected dipole in relative redshifts, not a 3D flow measurement."""
import csv,json,contextlib,io
from pathlib import Path
import numpy as np
from scipy.integrate import quad
with contextlib.redirect_stdout(io.StringIO()):
 from catalog import tables
ra0,de0,z0=146.73617048,10.11469530,.2219305
H0=70.;c=299792.458
da=c/H0*quad(lambda z:1/np.sqrt(.3*(1+z)**3+.7),0,z0)[0]/(1+z0)
s=[]
with open('jackpot_sdss_40arcmin_flow.csv') as f:
 for r in csv.DictReader(x for x in f if not x.startswith('#')):
  s.append([float(r[k]) for k in ['ra','dec','z']])
zip_files=[Path(x) for x in ['desi_bright.fits','desi_bright_27562.fits','desi_dark.fits','desi_dark_27562.fits']]+sorted(Path('wide_desi').glob('*.fits'))
desi={}
for p in zip_files:
 t=tables(p)
 z={int(row['TARGETID']):row for row in t['REDSHIFTS']}
 for f in t['FIBERMAP']:
  id=int(f['TARGETID']);q=z[id];zz=float(q['Z'])
  if q['ZWARN']!=0 or q['SPECTYPE'].strip()!=b'GALAXY' or not .18<zz<.265:continue
  r,d=float(f['TARGET_RA']),float(f['TARGET_DEC'])
  if q['DELTACHI2']<9:continue
  quality=(float(q['DELTACHI2']),[r,d,zz])
  if id not in desi or quality[0]>desi[id][0]:desi[id]=quality
d=[v[1] for v in desi.values()]
def dist(x,y):
 return np.hypot((x[0]-y[0])*np.cos(np.radians(de0)),x[1]-y[1])*3600
combo=d+[x for x in s if not any(dist(x,y)<1.5 for y in d)]
with open('jackpot_flow_independent_rows.json','w') as f:json.dump(dict(sdss=s,desi=d,merged=combo),f)
def screen(catalog,R,vmax,drop=False):
 q=np.array(catalog); q[:,0]=(q[:,0]-ra0)*np.cos(np.radians(de0));q[:,1]-=de0
 sep=np.linalg.norm(q[:,:2],axis=1)*60
 v=(q[:,2]-z0)*c/(1+z0)
 m=(sep<=R)&(sep>3/60)&(abs(v)<=vmax)
 if drop:
  cp=np.array([(146.333336- ra0)*np.cos(np.radians(de0)),10.0853504-de0])
  m&=(np.linalg.norm(q[:,:2]-cp,axis=1)*60>3)
 y=v[m]; xy=np.deg2rad(q[m,:2])*da
 if len(y)<5:return dict(n=len(y))
 X=xy-xy.mean(axis=0); Y=y-y.mean()
 pinv=np.linalg.pinv(X); b=pinv@Y
 ss=np.sum(Y**2); r2=np.sum((X@b)**2)/ss
 rng=np.random.default_rng(45231);p=np.stack([rng.permutation(Y) for _ in range(4095)])
 perms=np.sum((p@pinv.T@X.T)**2,axis=1)
 pv=(1+sum(perms>=r2*ss))/4096
 def pos(a):return float(np.degrees(np.arctan2(a[0],a[1]))%360)
 jk=[]
 for i in range(len(y)):
  xx=np.delete(xy,i,axis=0);yy=np.delete(y,i);xx-=xx.mean(axis=0)
  a=np.linalg.lstsq(xx,yy-yy.mean(),rcond=None)[0];jk.append(a.tolist())
 dirs=[pos(t) for t in jk]
 cov=np.linalg.eigh(X.T@X)
 return dict(n=len(y),pa_gradient=pos(b),pa_density_axis_mod180=pos(cov[1][:,1])%180,
    spatial_axis_ratio=np.sqrt(cov[0][0]/cov[0][1]),gradient_km_s_Mpc=np.linalg.norm(b),
    r2=r2,permutation_p=pv,jackknife_pa_difference_max=max(abs((a-pos(b)+180)%360-180) for a in dirs),
    center_km_s=np.median(y),standard_deviation_km_s=np.std(y,ddof=1))
out={}
for cat,a in [('SDSS',s),('DESI',d),('merged',combo)]:
 rows={}
 for R in [20,30,40]:
  for v in [1000,1500,2500]:
   rows[f'{R}_{v}']=screen(a,R,v)
 rows['40_1500_without_xray_region']=screen(a,40,1500,True)
 out[cat]=rows
 print(cat,'all raw',len(a));print(*rows.items(),sep='\n')
Path('jackpot_flow_screen.json').write_text(json.dumps(dict(pixels=[str(t) for t in zip_files],tests=out),indent=2)+'\n')
