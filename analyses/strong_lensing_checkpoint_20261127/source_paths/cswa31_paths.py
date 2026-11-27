"""Observed CSWA31 positions, azimuth/footprint, and single-plane geometry-only design.
No BHSM gravity fit, no environment inventory completion, no predictive scoring.
"""
from pathlib import Path
import json,sys
from math import comb
import numpy as np
from scipy.spatial import ConvexHull
from scipy.linalg import helmert
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'bhsm_environment_audit'/'pinned_extra'))
from r1_background_geometry import D,xrad
# Wang et al. 2022 Table 1. RA seconds from 09:21:00; Dec seconds from +18:10:00.
# S5b is -0.54 arcsec in Dec relative to +18:10:00, not +59.46.
data=[
 ('S0',1.4869,[(25.040,12.27),(25.858,7.24),(26.439,13.60),(25.781,24.64)]),
 ('S1',1.4869,[(25.987,7.84),(26.376,12.58)]),
 ('S2',1.4874,[(25.851,34.05),(26.252,31.13),(26.323,31.04)]),
 ('S3',2.763,[(24.159,16.03),(26.517,21.73)]),
 ('S4',3.4280,[(25.105,17.76),(25.531,17.62),(27.395,18.65)]),
 ('S5',4.205,[(24.634,6.47),(25.418,-.54),(27.085,13.39),(25.670,35.81)])]
dec0=18+10/60+17.70/3600
org=np.array([25.738,17.70])
fac=np.array([15*np.cos(np.deg2rad(dec0)),1.])
lens_z=.6828
plane_mpc=D(0,lens_z)
families=[]
for label,z,pts in data:
 xy=(np.array(pts)-org)*fac
 r=np.linalg.norm(xy,axis=1)
 chords=np.linalg.norm(xy[:,None]-xy,axis=-1)
 families.append(dict(feature_family=label,physical_source=('spiral' if label in ('S0','S1') else label),
           redshift=z,images=len(pts),EN_arcsec=xy.tolist(),min_r_arcsec=float(min(r)),max_r_arcsec=float(max(r)),
           max_pair_arcsec=float(chords.max()),distance_weight=D(lens_z,z)/D(0,z),
           use=('test_only' if label in ('S4','S5') else 'development')))
assert sum(f['images'] for f in families)==18
assert len({f['physical_source'] for f in families})==5
def ranks(items):
 # Illustrative sensitivity to coefficients of a single smooth image-plane
 # potential. Terms of degree 0,1 are unobservable in within-feature
 # contrasts. The fit space and geometry assume one thin plane only.
 # Normalization: 20 arcsec axes, binomial-normalized polynomial basis.
 no=[]
 for deg in [2,3,4,5]:
  ij=[(i,s-i) for s in range(2,deg+1) for i in range(s+1)]
  mats=[]
  for a in items:
   x,y=(np.array(a['EN_arcsec'])/20).T
   h=helmert(len(x))
   terms=np.array([np.sqrt(comb(i+j,i))*np.vstack((i*x**(i-1)*y**j if i else np.zeros_like(x), j*x**i*y**(j-1) if j else np.zeros_like(x))).T for i,j in ij]).transpose((1,2,0))
   mats.append((a['distance_weight']*np.einsum('ij,jkc->ikc',h,terms)).reshape(-1,len(ij)))
  m=np.vstack(mats)
  v=np.linalg.svd(m,compute_uv=False)
  rank=int(np.linalg.matrix_rank(m))
  no.append({'potential_degree':deg,'equations':len(m),'columns':len(ij),'rank':rank,
             'condition_nonzero_geometry_only':float(v[0]/v[rank-1])})
 return no
train=[f for f in families if f['use']=='development']
hull=ConvexHull(np.vstack([f['EN_arcsec'] for f in train]))
for f in families:
 xy=np.array(f['EN_arcsec'])
 f['outside_development_sky_hull']=(np.max(xy@hull.equations[:,:2].T+hull.equations[:,2],axis=1)>1e-8).tolist()
out=dict(reference='https://doi.org/10.1051/0004-6361/202243600 Table 1 and Sect. 2; S4 is line-only with model-assisted association, and S5(d) has lower S/N and model corroboration.',
          lens_z=lens_z,kpc_per_arcsec=1000*plane_mpc*xrad,source_families=families,
          design_train=ranks(train),design_all=ranks(families),
          scope='Geometry and coverage only. Local Taylor expansion of projected potential is a one-plane sensitivity diagnostic, not a physical CSWA31 assignment. Other deflection planes, correlated errors and incomplete group density are not solved; no lensing map is fit.')
(P/'cswa31_paths.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
