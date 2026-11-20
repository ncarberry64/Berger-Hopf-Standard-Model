from pathlib import Path
import numpy as np,json
p=Path(__file__).resolve().parents[1];o=Path(__file__).parent
z=np.load(o/'formed_n0_wall_spin_transfer.npz'); A=z['action_A']; g=z['spin_gap_covector']; t=np.linalg.solve(A.T,g)
w=np.load(o/'formed_n0_equal_local_field_test.npz');C=w['field_covector']; F=np.linalg.solve(A.T,C.T).T
a=np.load(p/'native_n0_coupled_static.npz');K=a['K84'];L=a['lift84x20'];I=a['interior64'];b=a['boundary20']
wall=K@L[:,4:]; R_temporal=wall[b[:4]]@np.linalg.inv(A)
# Rows of vanishing temporal traction use same saved K84, not exterior action constraints.
# Ignore strengths demonstrably at floating noise; report rank sensitivity explicitly.
def dual(E,ell=t,cut=1e-11):
 U,s,V=np.linalg.svd(E,full_matrices=True);ids=np.where(s>cut*max(s[0],1e-300))[0]
 dual=(U[:,ids]/s[ids])@(V[ids]@ell); N=V[len(ids):]; n=N.T@(N@ell)
 return dict(rank=int(len(ids)),singular_values=s.tolist(),dual_residual_norm=float(np.linalg.norm(n)),readout_norm=float(np.linalg.norm(ell)),relative=float(np.linalg.norm(n)/np.linalg.norm(ell))),n,dual
cases={'curvature_only':F,'curvature_and_scalar_zero_rhs':np.r_[F,np.eye(16)[12:]],'curvature_and_temporal_zero_reaction':np.r_[F,R_temporal], 'curvature_and_scalar_zero_rhs_and_temporal_zero_reaction':np.r_[F,np.eye(16)[12:],R_temporal]}
rows={};save={'field_force_map':F,'spin_force_dual':t,'temporal_wall_force_rows':R_temporal}; names=[f'A{i+1}_{k}' for i in range(3) for k in ['SU2_1','SU2_2','SU2_3','U1']]+[f'H_{i}' for i in range(4)]
for label,E in cases.items():
 r,n,l=dual(E,cut=1e-14);dn=n/np.linalg.norm(n);v=np.linalg.solve(A,dn);full=K@L@np.r_[np.zeros(4),v]
 r.update(null_unit_force=dn.tolist(),null_unit_state_norm=float(np.linalg.norm(v)),null_gap=float(g@v),null_constraint_norm=float(np.linalg.norm(E@dn)),max_original_interior_force=float(np.max(abs(full[I]))),related_temporal_wall_reaction=float(np.linalg.norm(full[b[:4]])),major_coordinates=sorted([(k,float(x)) for k,x in zip(names,dn)],key=lambda x:-abs(x[1]))[:5],rank_at_thresholds=[dual(E,cut=cut)[0]['rank'] for cut in [1e-9,1e-11,1e-13,1e-15]])
 rows[label]=r;save[label+'_visible_null_force_unit']=dn;save[label+'_dual']=l
delta_w=w['field_null_difference']; f=A@delta_w
r,n,l=dual(F)
out=dict(scope='Actual saved incoming-hi K84; time trace held; same C and g as full-three-axis field test. Original finite bulk Gauss retained; imposed zero temporal wall reaction is a further diagnostic not action-selected exterior.',cases=rows,physical_dimension=float(len(t)),actual_two_carrier_difference_force_norm=float(np.linalg.norm(f)),actual_two_carrier_recovered_spin_gap=float(n@f),difference_curvature_norm=float(np.linalg.norm(F@f)),alignment=float(n@f/(np.linalg.norm(n)*np.linalg.norm(f))),temporal_force_operator_norm=float(np.linalg.norm(R_temporal,2)),dual_amplification_time_trace_gauge_fixing='curvature map and covectors use same canonical fixed coordinate norm, not physical units')
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');np.savez(Path(__file__).with_suffix('.npz'),**save);print(json.dumps(out,indent=2))
