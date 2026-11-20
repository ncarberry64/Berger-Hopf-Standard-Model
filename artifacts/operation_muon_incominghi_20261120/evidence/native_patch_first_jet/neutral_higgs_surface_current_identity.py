"""Verify native Higgs axial central wall current is proportional to invariant phase current."""
from pathlib import Path
import sys,numpy as np
p=Path(__file__).resolve().parents[1];sys.path.insert(0,str(p))
from source_retained_magnetic import wall_data
import source_build_higgs_response as hg
import json
raw=np.load(p/'incoming_history.npz')['hi_raw_fields']; W=wall_data(raw)
C=hg.C_ORBIT; b=np.sqrt(10/3); N=W['lapse']; R=W['R4']; k=C*N*R/b
H=raw[260:264].copy(); n=H@H; A=W['connection'][4].copy()
gens=hg.generators()[0]
def J(h,A,dH=None):
 h=h[:2]+1j*h[2:]; D=np.einsum('a,aij,j->i',A,gens,h)
 if dH is not None: D+=dH
 return np.vdot(h,D).imag/np.vdot(h,h).real
s=np.load(p/'native_n0_coupled_static.npz')['KH20']
# Local Hessian order: H4 then [At,A1,A2,A3]×4 internal.
row=s[19,np.r_[np.arange(8,20),np.arange(4)]]
with np.load(p/'native_patch_first_jet'/'formed_n0_equal_local_field_test.npz') as z:
 vecs={n:z[n] for n in ['central_wall_response','H_aligned_wall_response','field_null_difference']}
calc=[]
for j,u in enumerate(np.vstack([np.eye(16),*vecs.values()])):
 x=u[8:12];h=u[12:];eps=1e-5
 Jprime=(J(H+eps*h,A+eps*x)-J(H-eps*h,A-eps*x))/(2*eps)
 predict=k*(n*Jprime+2*(H@h)*J(H,A))
 actual=float(row@u)
 assert abs(predict-actual)<2e-11
 calc.append([float(Jprime),actual,float(predict)])
out={'description':'fixed geometry angular n0 surface current only, not complete junction force','kappa':k,'H2':n,'J_base':J(H,A),'max_current_derivative_error':max(abs(a-b) for _,a,b in calc), 'trial_witnesses':dict(zip(vecs,calc[-3:]))}
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
