import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
from hashlib import sha256
import sys,json,numpy as np
R=Path('C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001')
O=Path(__file__).parent/'COMPARISON_TIME_LIFT_v2'
sys.path[:0]=[str(R/'src'),str(R)]
from bhsm.interface.muon_incoming_curvature_time_lift import execute_covariant_electron_comparison
from bhsm.interface.retained_response.finite_time_response import write_npz
def pin(p):return sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def mx(x):return float(np.max(abs(x)))
if O.exists():raise FileExistsError('preserve completed applications')
O.mkdir()
old=Path(__file__).parent/'COMPARISON_TIME_LIFT_v1'
old_arrays=old/'application.npz'
if pin(old_arrays)!='33b196153347e2a75971104e92a164d5e42813a767d9be27d82ebd89241fdd82':raise ValueError('exact completed comparison required')
source=R/'artifacts/muon_stationary_native_reference_load_20261019/run_5/native_reference_load.npz'
if pin(source)!='1663a7d19350412cae236345974e9c48f07ace8f54b29752bd5e2956a8221753':raise ValueError('exact completed151 reference required')
with np.load(old_arrays,allow_pickle=False) as z:a0={k:z[k].copy() for k in z.files}
with np.load(source,allow_pickle=False) as z:
    if not all(np.array_equal(a0[k],z[q]) for k,q in (
        ('input_iterate151','input_iterate151'),('input_theta22','actual_theta'),
        ('input_theta_gradient22x151','actual_theta_gradient'))):
        raise ValueError('completed comparison/source identities differ')
owner=R/'src/bhsm/interface/muon_incoming_curvature_time_lift.py'
v1_snapshot=old/'executed_source_owner.py'
if pin(v1_snapshot)!='4b4d7d2be23703fac3e9dd0f83aa710b1b5097f007f8b414f35fa8403740d090':raise ValueError('preserve original v1 owner evidence')
prep=R/'artifacts/muon_ideal_collider_preparation_20261016/BHSM_IDEAL_COLLIDER_PREPARATION_V1.json'
if pin(prep)!='dcc4ad850ea38dcd405637d24b306efe8789ab08e144f559d7cc294cd72e8f0f':raise ValueError('adopted preparation changed')
pins={str(p):pin(p) for p in (source,old_arrays,old/'result.json',v1_snapshot,prep,owner,Path(__file__))}
dump(O/'BEFORE.json',dict(classification='VERSIONED_POINTWISE_CURVATURE_TIME_LIFT_AND_COVARIANT_CHARGE_APPLICATION',
    input_sha256=pins,held='same151 iterate, stationary coefficient family, completed v1 causal/projector/current arrays reused bitwise',
    new_equations=['D_mu lambda=0 => [F_mu_nu,lambda]=0; lambda_H H=0',
        'F_ij=(2 epsilon_ijk A_k+[Ai,Aj])/R^2; F_0i=[At/ell,Ai]/R',
        'ordinary_Qdot+i[h,Q]=D_tau Q+i[W,Q]; h=W-iOmega'],
    superseding_scope='v1 time-lift rank applies only to spatially constant lambda; this version tests nonconstant covariantly parallel lambda through curvature integrability',
    not_executed='no new spectrum, background/past solve, dressed state, physical packet or collider incidence'))
a=execute_covariant_electron_comparison(a0['input_theta22'],a0['input_theta_gradient22x151'],comparison_data=a0)
arrays={k:v for k,v in a.items() if isinstance(v,np.ndarray)}
write_npz(O/'application.npz',arrays)
reused=('H','H_source','electron_positive','electron_negative','electron_positive_source',
    'original_current_pair_operator_blocks','original_current_pair_operator_source')
if not all(np.array_equal(a[k],a0[k]) for k in reused):raise ValueError('completed coefficient/projector/current arrays changed')
checks={k:mx(a[k]) for k in ('pointwise_original_integrability_rows',
    'pointwise_original_integrability_source_rows','covariant_Higgs_charge_rate_identity_rows',
    'original_charge_clock_forms_identity_rows','original_charge_clock_forms_source_identity_rows')}
record=dict(classification='EXECUTED_POINTWISE_U2_SYMMETRY_INTEGRABILITY_AND_NONZERO_COVARIANT_CHARGE_CONTACT',
    input_sha256=pins,arrays=dict(sha256=pin(O/'application.npz')),
    supersedes='only the overbroad physical time-lift interpretation of COMPARISON_TIME_LIFT_v1 constant-compensator rank; exact v1 source/results remain historical unchanged',
    actual_original_equations='Lie_K A-D lambda=0 and Lie_K H+lambda_H H=0, K=ell^-1 partial_t; ordinary Lie_K fields=0 on this stationary comparison gives D lambda=0 and lambda_H H=0',
    pointwise_integrability='[F_mu_nu,lambda]=0 and lambda_H H=0 without assuming lambda spatially constant; pointwise rank4 implies lambda0, whose parallel continuation is0 on the connected comparison component',
    original_frame='RIGHT Maurer [Ei,Ej]=-2epsilon_ijk Ek; Ai are unit-S3 coefficients, proper ei=Ei/R and proper time ell^-1 partial_t',
    curvature_order=['F01','F02','F03','F23','F31','F12'],
    pointwise_time_gauge_rank=int(a['pointwise_time_gauge_rank']),
    pointwise_integrability_singular_values=a['pointwise_integrability_singular_values'].tolist(),
    pointwise_original_row_pivots=a['pointwise_original_row_pivots'].tolist(),
    pointwise_pivot_condition=float(a['pointwise_pivot_condition']),
    pointwise_gauge_compensator=a['pointwise_gauge_compensator'].tolist(),
    pointwise_remaining_U2_gauge_freedom=int(a['pointwise_remaining_gauge_generators'].shape[1]),
    gauge_compensator_source='C Dlambda+(DC)lambda=0 with same full-rank original pivot; lambda and Dlambda0 throughout declared stationary coefficient family only',
    original_checks=checks,completed_causal_projector_current_arrays_reused_bitwise=list(reused),
    original_charge_equation='E_Q=ordinary_Qdot+i[h,Q]=D_tau Q+i[W,Q]; D_tau Q=ordinary_Qdot+[Omega,Q], ordinary_Qdot0 ONLY on stationary comparison',
    original_charge_source='D E_Q=[DOmega,Q]+[Omega,DQ]+i[DW,Q]+i[W,DQ], with proper-clock and all151 field/geometry variations retained',
    covariant_Higgs_time_rate_max=mx(a['covariant_Higgs_time_rate']),
    covariant_charge_time_rate_max=mx(a['covariant_charge_time_rate']),
    original_covariant_charge_stationarity_max=mx(a['original_covariant_charge_stationarity_rows']),
    original_covariant_charge_stationarity_source_max=mx(a['original_covariant_charge_stationarity_source_rows']),
    charged_sector_verdict='nonzero bare electron6 charge-stationarity is the explicit operator contribution the coupled gauge/Higgs/dressed transition must balance; no charged4 projection, physical no-go or nonuniqueness inference',
    physical_time_scope='the represented U2 lift for the stipulated proper material observer is fixed; preparation-clock incidence, full interacting stationarity and past/domain completion are not established',
    source_scope='complete151 declared static comparison coefficient pullback; not the complete physical moving-background/domain derivative',
    physical_d_in=None,physical_initial_Cauchy_data=None,physical_packet_sections=None,
    collider_to_parent_incidence=None,full_gauss_dressing_solved=False,
    physical_incoming_selector_completed=False,full_stationary_past_solved=False,
    exact_pair_state_changed=False,local_native_accounting_changed=False,
    physical_guard=2e-10,physical_admission=False,
    error_scope='finite original pointwise integrability/source and charge-clock identities; nonzero charge contact retained as unresolved coupled obligation, no continuum/full-domain bound',
    NEXT_OPERAND='consume E_Q with the same-background prepared Gauss/dressing equations, then construct the actual same-domain collider/Cauchy incidence and interacting prepared-state mode amplitudes')
dump(O/'result.json',record)
(O/'executed_source_owner.py').write_bytes(owner.read_bytes())
(O/'executed_driver.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps(record,sort_keys=True,indent=2),flush=True)
