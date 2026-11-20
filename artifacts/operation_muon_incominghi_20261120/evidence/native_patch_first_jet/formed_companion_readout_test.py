from pathlib import Path
import numpy as np,sys
p=Path(__file__).resolve().parents[1]
s=p/'native_patch_first_jet';sys.path.insert(0,str(p))
from source_retained_magnetic import wall_data
from source_action_magnetic_kernel import bracket
raw=np.load(p/'incoming_history.npz')['hi_raw_fields']
w=wall_data(raw);q=w['charge']/np.linalg.norm(w['charge']);Z=np.eye(4)[3]-q[3]*q;Z/=np.linalg.norm(Z)
e=np.load(s/'formed_n0_equal_local_field_test.npz'); a=np.load(s/'formed_n0_wall_spin_transfer.npz')
C=e['field_covector']; D=a['action_A'];g=a['spin_gap_covector']
P=lambda d:np.r_[np.kron(np.eye(3),d[:,None]),np.zeros((4,3))]
F=np.linalg.solve(D,np.c_[P(np.eye(4)[3]),P(q)])
y=g@F
orth=np.r_[np.zeros(8),Z,np.zeros(4)]
A=w['connection'][2:];R=w['R4']; QH=np.array([wall_data(raw+1e-25j*h)['charge'].imag/1e-25 for h in np.eye(268)[260:264]]).T/np.linalg.norm(w['charge'])
Dcurv=np.array([(q@(2*r[:12].reshape(3,4)[2]+(bracket(r[:12].reshape(3,4)[0],A[1])+bracket(A[0],r[:12].reshape(3,4)[1])).real)+(2*A[2]+bracket(A[0],A[1]).real)@QH@r[12:])/R**2 for r in np.eye(16)])
for name,X in [('curl only',C),('curl and orthogonal axial connection',np.r_[C,orth[None]]),('curl and full axial projected curvature',np.r_[C,Dcurv[None]])]:
 H=X@F
 k=np.linalg.lstsq(H.T,y,rcond=None)[0]
 r=y-k@H
 print(name, np.linalg.norm(r), np.linalg.norm(r)/np.linalg.norm(y), np.linalg.svd(H,compute_uv=False), k)
 kf=np.linalg.lstsq(X.T,g,rcond=None)[0];print("full16 trace residual", np.linalg.norm(g-kf@X)/np.linalg.norm(g))
