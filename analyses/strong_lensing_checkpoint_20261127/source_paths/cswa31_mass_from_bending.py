"""GR-equivalent aperture mass from measured image positions in a circular control."""
from pathlib import Path
import json,sys,numpy as np
from scipy.integrate import quad
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'bhsm_environment_audit'/'pinned_extra'))
from r1_background_geometry import D,G,speed,xrad
obs=json.loads((P/'cswa31_paths.json').read_text())
z=obs['lens_z'];dl=D(0,z)
def F(z1,z2):
 return speed/70/(1+z2)*quad(lambda x:1/np.sqrt(.3*(1+x)**3+.7),z1,z2,epsabs=1e-13)[0]
def fordata(g):
 if g['feature_family'] not in ('S0','S3','S5'):return None
 x=np.array(g['EN_arcsec']);n=x/np.linalg.norm(x,axis=1)[:,None]
 X,N=[a-a.mean(0) for a in [x,n]]
 b=np.sum(X*N)/np.sum(N*N)
 s=x-b*n
 zs=g['redshift']
 def est(D):
   M=speed**2/G/4*D(0,z)*D(0,zs)/D(z,zs)*(xrad*b)**2
   return [1000*D(0,z)*xrad*b,M]
 return dict(family=g['feature_family'],redshift=zs,z_offset_deg=None,angular_Einstein_SIS_arcsec=float(b),
     rms_source_arcsec=float(np.sqrt(np.mean(np.sum((s-s.mean(0))**2,axis=1)))),
     aperture_and_mass_frozen_distance=est(D),aperture_and_mass_flat_LCDM70=est(F))
rows=[y for g in obs['source_families'] if (y:=fordata(g)) is not None]
data=dict(formula='M(<D_l theta_E) = c²/(4G)*D_l D_s/D_ls*theta_E² for an isolated circular thin lens. Fit centered SIS alpha_reduced=b*theta/|theta|, eliminating one common source per image family. High-redshift rows ignore additional deflectors, are only one-plane equivalent controls and not accepted mass measurements. Never combine them as exact enclosed masses.',
    source='Wang et al. 2022 Table 1; comparison Grillo et al. 2013 arXiv:1305.5844; no masses fit to external dynamics.',
    results=rows)
(P/'cswa31_mass_from_bending.json').write_text(json.dumps(data,indent=2)+'\n')
for x in rows:print(x)
