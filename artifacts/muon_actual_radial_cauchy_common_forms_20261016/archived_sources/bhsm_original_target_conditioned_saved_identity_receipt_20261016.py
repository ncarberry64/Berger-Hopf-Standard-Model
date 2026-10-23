"""Saved-only representation receipt for the new original-target finite cell.

No action, derivative, primal integration or physical terminal solve is run.
"""
from pathlib import Path
from hashlib import sha256
import json
import sys
import numpy as np

ROOT=Path('C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001')
WORK=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from flint import ctx,acb_mat
from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
from bhsm.interface.muon_stored_fiber_canonical_tangent import _rows
from bhsm.interface.muon_changing_weak_birth_action import affine_parent_master_map
ctx.prec=256
pins={}

def read(p):
    p=Path(p);pins[str(p)]=sha256(p.read_bytes()).hexdigest()
    if p.suffix=='.json':return json.loads(p.read_bytes())
    with np.load(p,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}

def exact(z,k):return _matrix(z[k+'_high'])+_matrix(z[k+'_low'])

run=WORK/'outputs/bhsm_original_target_conditioned_four_canonical_cell_20261016/run_1'
meta=read(run/'result.json')
if meta['source_sha256']!='11fa22b3790a43edc980ea99f0806405a78223adda949c44584b7e6344cbbb39' or not meta['finite_new_response_cell_admitted']:
    raise ValueError('Exact freshly admitted new local cell required')
for filename,entry in meta['archives'].items():
    if sha256((run/filename).read_bytes()).hexdigest()!=entry['sha256']:raise ValueError('Changed actual numeric archive')
z=read(run/'actual_new_target_R7_four_Cauchy_and_full252_return.npz')
primal=read(WORK/'outputs/bhsm_original_target_new_coupled_tail_cell_20261016/run_1/retry_00_new_tail_original526.npz')
for part in ('high','low'):
    if not np.array_equal(z['actual_midpoint_master368_'+part],primal['midpoint_master368_'+part]):raise ValueError('Different accepted full368 midpoint')
for key in ('coordinate_time','coordinate_time_low','step'):
    if not np.array_equal(z[key],primal[key]):raise ValueError('Different exact midpoint clock/step')
family=ROOT/'artifacts/muon_baton_zoo_maximal_current_realization_20261013'
prior=read(family/'actual_new_only_compatible316_matrixfree_retarded_cell7_warm_run_2/actual_new_only_compatible316_response_and_full252_source_return.npz')
birth=read(ROOT/'artifacts/muon_baton_zoo_radial_completion_20261013/action_gauge_degree2_run_1/enlarged_birth_proper_three_columns_and_canonical_seeds.npz')
Q7,S7,Gp=exact(z,'retarded_and_homogeneous_separate316'),exact(z,'parent_source_cotangent'),exact(z,'actual_affine_primal_source_gradient252')
Q4,S4=acb_mat(316,4),acb_mat(252,4)
for i in range(316):
    Q4[i,0]=Q7[i,0]
    for j in range(3):Q4[i,j+1]=Q7[i,j+1]+Q7[i,j+4]
for i in range(252):
    S4[i,0]=S7[i,0]+Gp[i,0]
    for j in range(3):S4[i,j+1]=S7[i,j+1]+S7[i,j+4]
time=_matrix([[z['coordinate_time'].item()]])[0,0]+_matrix([[z['coordinate_time_low'].item()]])[0,0]
h=_matrix([[z['step'].item()]])[0,0];J0=affine_parent_master_map(0)
J=_matrix(J0)+time*_matrix(affine_parent_master_map(1)-J0)
increment=h*J.transpose()*S4
parent=acb_mat(252,7);columns=J*exact(birth,'fixed_position_parent_phase')
for i in range(252):
    for j in range(3):parent[i,j+1]=columns[i,j]
initial=exact(prior,'retarded_and_homogeneous_separate316');stage=exact(z,'stage')
checks=dict(
    four_Cauchy_from_seven=_upper(exact(z,'combined_four_Cauchy316')-Q4),
    four_source_with_primal_offset_once=_upper(exact(z,'all_four_source_cotangent252')-S4),
    final_Cauchy_alias=_upper(exact(z,'final_canonical')-Q7),
    midpoint_position_identity=_upper(_rows(stage,0,158)-(_rows(initial,0,158)+_rows(Q7,0,158))/2),
    original_affine_parent_source=_upper(exact(z,'actual_parent_source252')-parent),
    source_increment_h_Jtranspose_S4=_upper(exact(z,'full252_inherited_source_return_increment')-increment),
    source_return_carry_once=_upper(exact(z,'existing_full252_source_return')-exact(prior,'existing_full252_source_return')-exact(z,'full252_inherited_source_return_increment')))
if max(checks.values())>1e-20:raise ValueError('Saved high/low representation identity failed')
report=dict(classification='SAVED_ONLY_NEW_ORIGINAL_TARGET_FINITE_CELL_REPRESENTATION_RECEIPT',
    source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),input_sha256=pins,
    exact_accepted_midpoint_full368_and_high_low_clock_bit_identities=True,
    representation_identity_upper=checks,representation_guard=1e-20,
    actual_original526_upper=meta['original526_response_upper'],fresh_same_gradient_upper=meta['same_gradient_reproduction_upper'],
    actual_original210_clock_upper=meta['clock_records'][0]['original210_upper'],
    full252_primal_source_offset_upper=_upper(Gp),full252_source_increment_upper=_upper(increment),
    original_prefix_cell7_complete_density_time_derivative_admitted=False,
    no_action_or_history_recomputed=True,representation_checks_are_not_physical_derivative_validation=True,
    physical_outgoing_Y_R=None,physical_C0_Cj=None,full_physical_derivative_pass=False,
    original_coupled_corrections=0,physical_Maxwell226_after_pass=False,physical_muon_magnetic_moment=None)
out=run.parent/'saved_identity_receipt.json';out.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
print(json.dumps(dict(checks=checks,receipt_sha256=sha256(out.read_bytes()).hexdigest()),sort_keys=True))
