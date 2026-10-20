import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
from hashlib import sha256
import sys,json,numpy as np
R=Path('C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001');O=Path(__file__).parent/'COMPARISON_TIME_LIFT_v1'
sys.path[:0]=[str(R/'src'),str(R)]
from bhsm.interface.muon_incoming_comparison_time_lift import execute_electron_comparison
from bhsm.interface.retained_response.finite_time_response import write_npz
def pin(p):return sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def mx(x):return float(np.max(abs(x)))
if O.exists():raise FileExistsError('preserve completed applications')
O.mkdir()
source=R/'artifacts/muon_stationary_native_reference_load_20261019/run_5/native_reference_load.npz'
if pin(source)!='1663a7d19350412cae236345974e9c48f07ace8f54b29752bd5e2956a8221753':raise ValueError('exact completed comparison required')
with np.load(source,allow_pickle=False) as z:
 x=z['input_iterate151'].copy();theta=z['actual_theta'].copy();grad=z['actual_theta_gradient'].copy()
coupled=R/'artifacts/muon_coupled_reference_replacement_20261019/run_2/coupled_replacement.npz'
with np.load(coupled,allow_pickle=False) as z:
 if not np.array_equal(x,z['provisional_iterate151']):raise ValueError('coupled/reference comparison identities differ')
prep=R/'artifacts/muon_ideal_collider_preparation_20261016/BHSM_IDEAL_COLLIDER_PREPARATION_V1.json'
if pin(prep)!='dcc4ad850ea38dcd405637d24b306efe8789ab08e144f559d7cc294cd72e8f0f':raise ValueError('adopted preparation changed')
owner=R/'src/bhsm/interface/muon_incoming_comparison_time_lift.py'
pins={str(p):pin(p) for p in (source,coupled,prep,owner,Path(__file__))}
dump(O/'BEFORE.json',dict(input_sha256=pins,classification='NEW_STATIONARY_SYMMETRY_TIME_GAUGE_LIFT_APPLICATION',
 equations=['D_mu lambda=0; lambda_H H=0','h_proper=W-iOmega','[h,Pplus]=0; [h,DPplus]+[Dh,Pplus]=0'],
 held='exact saved provisional comparison151, fullnative0 outputs and all previous nonpasses unchanged',
 not_executed='no new past/background extension, wave operator, physical packet, collider incidence or interacting state'))
a=execute_electron_comparison(theta,grad)
arrays={k:v for k,v in a.items() if isinstance(v,np.ndarray)}
arrays.update(input_iterate151=x,input_theta22=theta,input_theta_gradient22x151=grad)
write_npz(O/'application.npz',arrays)
checks={k:mx(a[k]) for k in ('original_symmetry_rows','original_causal_coefficient_rows','Hermiticity_rows',
 'electron_family_reducing_rows','electron_family_source_reducing_rows','electron_original_projector_commutator_rows',
 'electron_original_projector_source_rows','electron_original_idempotent_source_rows',
 'electron_original_CAR_completeness_rows','electron_original_CAR_opposite_rows','complete_constant_Haar_Cauchy_Gram_rows')}
record=dict(classification='EXECUTED_ORIGINAL_STATIONARY_TIME_GAUGE_LIFT_AND_ELECTRON_BOUNDARY_CURRENT_COMPONENT',
 input_sha256=pins,arrays=dict(sha256=pin(O/'application.npz')),
 original_time_lift_equations='[A_mu,lambda]=0 and lambda_H H=0 with ordinary Lie_K fields=0 ONLY on saved stationary comparison',
 proper_clock='K=ell^-1 partial_t from actual induced metric; full preparation-clock incidence remains open',
 actual_time_gauge_rank=int(a['represented_time_gauge_lift_rank']),gauge_compensator=a['gauge_compensator'].tolist(),
 time_gauge_pivot_condition=float(a['pivot_condition']),time_gauge_singular_values=a['singular_values'].tolist(),
 gauge_compensator_source_provenance='C Dlambda+(DC)lambda=0; C rank4 and lambda0 imply Dlambda0 throughout this stationary family; actual nonstationary Lie-time sources not supplied',
 original_checks=checks,electron_positive_dimension=int(a['electron_positive_dimension']),electron_negative_dimension=int(a['electron_negative_dimension']),
 electron_eigenvalues_action_units=a['electron_eigenvalues'].tolist(),
 charged_four_to_neutral_operator_max=mx(a['electron_charged_to_neutral_rows']),
 charged_four_to_neutral_operator_norm2=float(np.linalg.norm(a['electron_charged_to_neutral_rows'],2)),
 Higgs_charge_evolution_commutator_max=mx(a['electron_charge_evolution_rows']),
 Higgs_charge_evolution_source_max=mx(a['electron_charge_evolution_source_rows']),
 full_local_parallel_charge_max=mx(a['full_local_parallel_charge_rows']),
 current_pair_operator_max=mx(a['original_current_pair_operator_blocks']),current_pair_operator_source_max=mx(a['original_current_pair_operator_source']),
 current_scope='actual original24 vertex operator blocks Pplus V Pminus and151 static-field derivatives; no pair expectation, occupation, transition or beam packet assigned',
 charged_sector_verdict='Higgs-selected charged4 bare fiber is NOT a reducing sector of this comparison; its neutral mixing must enter charge/constraint dressing, not be deleted',
 Cauchy_domain_scope='exact reducing constant-right-body scalar harmonic times full18 on roundS3, complete constant-sector Haar norm; not full lowest shell or collider Cauchy domain',
 physical_unit_scope='saved unit is provisional; positive common energy rescaling does not change sign projectors; no MeV packet energies or physical scale admitted',
 physical_comparison_fully_stationary=False,physical_past_end_or_Omega_minus=None,
 physical_packet_sections=None,physical_d_in=None,physical_initial_Cauchy_data=None,
 collider_to_parent_incidence=None,exact_pair_state_changed=False,physical_homogeneous_state_selected=False,
 full_gauss_dressing_solved=False,local_native_accounting_changed=False,physical_guard=2e-10,physical_admission=False,
 error_scope='finite original time-lift and operator-source identities on exact saved provisional comparison; no stationary-past, complete-domain, continuum or physical-data error bound',
 NEXT_OPERAND='use original charge/dressing and same-domain collider/normal incidence equations to determine admitted comparison and actual prepared modes; full6 electron component and all current/source blocks remain available')
dump(O/'result.json',record)
(O/'executed_source_owner.py').write_bytes(owner.read_bytes());(O/'executed_driver.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps(record,sort_keys=True,indent=2),flush=True)
