from pathlib import Path
import sys,json,numpy as np
p=Path(__file__).resolve().parents[1];sys.path.insert(0,str(p))
from source_retained_magnetic import wall_data
stored=np.load(Path(__file__).with_name('formed_n0_wall_spin_transfer.npz'));A=stored['action_A'];g=stored['spin_gap_covector']
archive=np.load(p/'native_n0_coupled_static.npz');L=archive['lift84x20'];K=archive['K84']
raw=np.load(p/'incoming_history.npz')['hi_raw_fields'];w=wall_data(raw);Q=w['charge'];Qnorm=np.linalg.norm(Q);q=Q/Qnorm;R=w['R4'];N=w['lapse'];G=w['connection'][2:]
# Angular Higgs is homogeneous; the reduced Abelian coframe uses normalized Q(H).
Q_H=np.array([wall_data(raw+1e-25j*s)['charge'].imag/1e-25 for s in np.eye(268)[260:264]]).T/Qnorm
C=2/R**2*np.c_[np.kron(np.eye(3),q[None]),G@Q_H]
assert np.linalg.norm(q@Q_H)<1e-12
target=np.array([0.,0.,1.]);records={};arrays={'field_covector':C,'spin_gap_covector':g,'target':target}
def B_local(y):
 z=raw.copy(); z[np.arange(80).reshape(4,5,4)[3,2:].ravel()+100]+=y[:12]; z[260:264]+=y[12:]
 u=wall_data(z);return 2/R**2*(u['connection'][2:]@(u['charge']/np.linalg.norm(u['charge'])))
for key,d in [('central',np.eye(4)[3]),('H_aligned',q)]:
 P=np.r_[np.kron(np.eye(3),d[:,None]),np.zeros((4,3))]
 T=np.linalg.solve(A,P); M=C@T; f=np.linalg.solve(M,target); a=T@f; orig_w=np.r_[np.zeros(4),a];Rfull=K@L@orig_w
 finite=(B_local(1e-4*a)-B_local(-1e-4*a))/(2e-4)
 records[key]=dict(rhs_force=f.tolist(),field=(C@a).tolist(),finite_field_difference=finite.tolist(),field_normalization_smallest_singular=float(np.linalg.svd(M,compute_uv=False)[-1]),coordinate_gap_shift=float(g@a),proper_gap_shift=float(g@a/N),spatial_Higgs_correction_norm=float(np.linalg.norm(a[12:])),original_bulk_residual=float(np.linalg.norm(Rfull[archive['interior64']])),wall_force_residual=float(np.linalg.norm((A@a)-P@f)))
 arrays[key+'_wall_response']=a
u=arrays['central_wall_response']-arrays['H_aligned_wall_response'];arrays['field_null_difference']=u
out=dict(scope='same incoming-hi frozen n0 action and formed candidate; externally supplied abstract traction families adjusted to identical local H-aligned reduced angular field in retained units; no actual source, exterior, or g',records=records,field_null_difference_norm=float(np.linalg.norm(C@u)),field_null_difference_gap_coordinate=float(g@u),field_null_difference_gap_proper=float(g@u/N),maximum_linear_field_nonlinear_FD_discrepancy=float(max(np.linalg.norm(np.array(a['finite_field_difference'])-target) for a in records.values())),Higgs_projection_contact_norm=float(np.linalg.norm(C[:,12:])))
np.savez(Path(__file__).with_suffix('.npz'),**arrays);Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
