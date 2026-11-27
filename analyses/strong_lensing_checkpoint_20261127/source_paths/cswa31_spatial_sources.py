"""Triage spatially distinct sightlines from redshift catalogue; not a weak shear measurement."""
import json,numpy as np
from pathlib import Path
P=Path(__file__).resolve().parent
cat=[]
for line in (P/'cswa31_muse_raw.tsv').read_text().splitlines():
 t=line.split()
 if len(t)==6 and t[0].isdigit():
  k,i,a,b,z,q=map(float,t);cat.append((int(i),a,b,z,q))
o=next(x for x in cat if x[0]==354)
b=3600*np.array([np.cos(np.deg2rad(o[2])),1.0])
def row(r):
 a=(np.array(r[1:3])-o[1:3])*b
 return dict(id=r[0],z=r[3],qf=r[4],EN_arcsec=a.tolist(),r_arcsec=float(np.linalg.norm(a)),sector=('N' if a[1]>=0 else 'S')+('E' if a[0]>=0 else 'W'))
def pair(x,y):
 a=np.array(y['EN_arcsec'])-x['EN_arcsec']
 return dict(ids=[x['id'],y['id']],arcsec=float(np.linalg.norm(a)),redshift_difference=y['z']-x['z'])
cand=[row(r) for r in cat if r[-1]>=3 and .85<r[-2]<1.4869]
zpair=pair(*[r for r in cand if r['id'] in (653,697)])
bins={}
for low,high in [(.85,1.35),(1.35,1.4869),(1.4869,2.0),(2,6)]:
 x=[row(r) for r in cat if r[-1]>=3 and low<r[-2]<high]
 bins[f'{low}--{high}']=dict(count=len(x),quadrants={s:sum(y['sector']==s for y in x) for s in ['NE','NW','SE','SW']},rows=x)
out=dict(scope='Secure catalogue detections only. Some entries can be repeat images or group deflectors, not independent sources and not a calibrated shear sample. z1.24 pair not established as lensed or paired.',
 bins=bins,z124_pair=zpair)
(P/'cswa31_spatial_sources.json').write_text(json.dumps(out,indent=2)+'\n')
for key,v in bins.items():
 print(key,v['count'],v['quadrants'])
for x in bins['0.85--1.35']['rows']:print(x)
print(zpair)
