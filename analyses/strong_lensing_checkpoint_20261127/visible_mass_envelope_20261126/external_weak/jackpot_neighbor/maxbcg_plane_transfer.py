"""Geometry isolation: move a foreground tide onto the main lens, calibrated at S1.
Uses fixed S3 A/B sky geometry as a fixture at all z, NOT S1/S2 image data.
At each z compare exact foreground + fixed SIS with one shared affine matrix at main plane.
Never fit to the observed third-source closure residual.
"""
from pathlib import Path
from scipy.integrate import quad
import json
import numpy as np
p=Path(__file__).resolve().parent
rows=json.loads((p/'maxbcg_foreground.json').read_text())
z1=.609; zp=.14228; zl=.2219305
theta=np.array([[-3.,-1.91],[1.03,.87]])
D=theta[0]-theta[1]
def chi(z): return 299792.458/70*quad(lambda q:1/np.sqrt(.3*(1+q)**3+.7),0,z)[0]
def w(z,s):return 1-chi(z)/chi(s)
def sis(t):return 1.43*t/np.linalg.norm(t,axis=-1)[:,None]
B=[]
for j in range(len(rows[str(z1)])):
    # Physically one foreground gradient, reduced by each source distance.
    H0=np.array(rows[str(z1)][j]['jacobian'])/w(zp,z1)
    hit=theta-w(zp,zl)*(theta@H0.T)
    def dp(a):
        return a[0]-a[1]
    relative_main=dp(sis(hit)-sis(theta))
    fid=H0* (w(zp,z1)/w(zl,z1))
    # Exact for common affine foreground and same fixed ray fixture:
    # rotation/resampling of main contribution scales with w(zl,zs)
    # and is accounted once; therefore it cancels in transfer difference.
    v={}
    z_train=[z1,2.035]
    joint_ratio=sum(w(zl,z)*w(zp,z) for z in z_train)/sum(w(zl,z)**2 for z in z_train)
    for zs in map(float,rows):
        row=rows[str(zs)][j]
        assert np.max(np.abs(np.array(row['jacobian'])-H0*w(zp,zs)))<1e-10
        ratio=w(zl,zs)/w(zl,z1)
        fore_linear=(H0@D)*w(zp,zs)+relative_main*ratio
        single= (fid@D)*w(zl,zs)+relative_main*ratio
        residual=fore_linear-single
        np.testing.assert_allclose(residual,(H0@D)*(w(zp,zs)-w(zp,z1)*ratio),atol=2e-13)
        v[str(zs)]=dict(weights=[w(zp,zs),w(zl,zs)],relative_error_mas=1e3*np.linalg.norm(residual),relative_error_vector_mas=(1e3*residual).tolist(),joint_inner_equal_weight_error_mas=1e3*np.linalg.norm((H0@D)*(w(zp,zs)-joint_ratio*w(zl,zs))),actual_linear_pair_mas=1e3*np.linalg.norm(fore_linear),two_plane_nonaffine_mas=row['two_plane_nonaffine_mas'])
    assert v[str(z1)]['relative_error_mas']<1e-12
    B.append(dict(mass=rows[str(z1)][j]['mass'],concentration=rows[str(z1)][j]['c'],scores=v))
(p/'maxbcg_plane_transfer.json').write_text(json.dumps(B,indent=2)+'\n')
for j in [4,5,6,7]:
    print(B[j]["mass"],B[j]["concentration"],{z:round(r["relative_error_mas"],4) for z,r in B[j]["scores"].items()})
print("S3 sensitivity range",min(b["scores"]["5.975"]["relative_error_mas"] for b in B),max(b["scores"]["5.975"]["relative_error_mas"] for b in B))
