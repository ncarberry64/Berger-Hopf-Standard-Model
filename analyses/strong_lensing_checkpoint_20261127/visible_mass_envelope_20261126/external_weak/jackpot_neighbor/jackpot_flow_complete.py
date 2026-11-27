"""Independent coverage check. Freeze the old 5.114-degree axis before new tiles."""
import csv,json,contextlib,io
import numpy as np
from pathlib import Path
from scipy.stats import spearmanr
with contextlib.redirect_stdout(io.StringIO()):
 import jackpot_flow_screen as base
P=Path(__file__).resolve().parent
pa=np.deg2rad(5.114416620935251)
path=next((p for p in [P/'jackpot_desi_tap_noirlab.csv',P/'jackpot_desi_tap_beta.csv'] if p.exists()),None)
if path is None:raise FileNotFoundError('TAP download')
entries={}
for row in csv.DictReader(path.open()):
 try:
  key=int(row['targetid']); quality=float(row['deltachi2'])
  r=[float(row[k]) for k in ['target_ra','target_dec','z']]+[int(row['healpix'])]
  if key not in entries or quality>entries[key][0]:entries[key]=[quality,r]
 except (ValueError,KeyError):
  raise
d=np.array([r for _,r in entries.values()])
def comp(key,t,r,v,pa):
 q=np.array(t)[:,:3].copy()
 q[:,0]=(q[:,0]-base.ra0)*np.cos(np.radians(base.de0))
 q[:,1]-=base.de0
 p=60*np.linalg.norm(q[:,:2],axis=1)
 velocity=base.c*(q[:,2]-base.z0)/(1+base.z0)
 m=(p<=r)&(p>3/60)&(abs(velocity)<=v)
 xy=np.deg2rad(q[m,:2])*base.da; y=velocity[m]
 if len(y)<4:return dict(n=len(y))
 x=xy@np.array([np.sin(pa),np.cos(pa)]); xc=x-x.mean();yc=y-y.mean()
 den=xc@xc
 b=xc@yc/den
 rng=np.random.default_rng(3601); draws=[xc@rng.permutation(yc)/den for i in range(4095)]
 p=(1+sum(k>=b for k in draws))/4096
 stats=base.screen(np.array(t)[:,:3],r,v)
 return dict(n=len(y),north_axis_beta_km_s_Mpc=float(b),frozen_axis_p_one_sided=p,rho=float(spearmanr(x,y).statistic),unfrozen=stats)
old=np.isin(d[:,3],[4352,27562])
both=d[:,:3].tolist()+[x for x in base.s if not any(base.dist(x,y)<1.5 for y in d)]
out={}
for k,t in [('old_DESI',d[old]),('previously_missing',d[~old]),('all_DESI',d),('with_SDSS',both)]:
 out[k]={}
 for r,v in [(40,1500),(30,1500),(40,1000),(40,2500)]:
   y=comp(k,t,r,v,pa);out[k][f'{r}_{v}']=y
   print(k,r,v,y)
(P/'jackpot_flow_complete.json').write_text(json.dumps(dict(raw_rows=len(d),tile_counts={str(int(i)):int(sum(d[:,3]==i)) for i in np.unique(d[:,3])},statistics=out),indent=2)+'\n')
