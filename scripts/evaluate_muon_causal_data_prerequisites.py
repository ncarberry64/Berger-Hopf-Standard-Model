"""Consume saved causal comparison, Gauss and response diagnostics.

No background, packet, parent/child field, spectrum or past limit is solved
again. Physical incoming data remain explicitly uninstantiated.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys,os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from bhsm.interface.muon_comparison_charge_balance import consume_charge_balance
from bhsm.interface.retained_response.finite_time_response import write_npz
BASE=ROOT/'artifacts/muon_causal_data_prerequisites_20261019'
CORES=('COMPARISON_TIME_LIFT_v1','COMPARISON_TIME_LIFT_v2','PREPARED_GAUSS_v1',
 'PREPARED_GAUSS_v2','PREPARED_GAUSS_v3','CHARGE_BALANCE_v1','RESPONSE_DIAGNOSTICS_v1')


def pin(p):return sha256(Path(p).read_bytes()).hexdigest()


def dump(p,v):
    Path(p).write_bytes((json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+'\n').encode())


def load(p):
    with np.load(p,allow_pickle=False) as z:return {k:z[k].copy() for k in z.files}


def verified_inputs():
    pins={}
    for name in CORES:
        p=BASE/'core'/name/'canonical_binding.json';r=json.loads(p.read_bytes())
        if r['application']!=name:raise ValueError('application identity changed')
        for group in ('input_sha256','files_sha256'):
            for rel,h in r[group].items():
                path=Path(rel)
                if path.is_absolute() or '..' in path.parts:raise ValueError('nonrepository input')
                if pin(ROOT/path)!=h:raise ValueError('executed input changed '+rel)
                if rel in pins and pins[rel]!=h:raise ValueError('conflicting input '+rel)
                pins[rel]=h
        pins[p.relative_to(ROOT).as_posix()]=pin(p)
    return pins


def run(output):
    output=Path(output)
    if output.exists():raise FileExistsError('preserve all earlier applications')
    pins=verified_inputs();core=BASE/'core'
    comparison=load(core/'COMPARISON_TIME_LIFT_v2/application.npz')
    gauss=load(core/'PREPARED_GAUSS_v2/application.npz')
    balanced=consume_charge_balance(comparison,gauss)
    saved=load(core/'CHARGE_BALANCE_v1/application.npz')
    arrays={k:v for k,v in balanced.items() if isinstance(v,np.ndarray)}
    if arrays.keys()!=saved.keys():raise ValueError('charge-balance operator set changed')
    for k,v in arrays.items():
        if not np.array_equal(v,saved[k]):raise ValueError('completed charge application changed '+k)
    # Reuse, do not repeat, the comparison/projector/current application.
    original=load(core/'COMPARISON_TIME_LIFT_v1/application.npz')
    comp=json.loads((core/'COMPARISON_TIME_LIFT_v2/result.json').read_bytes())
    for k in comp['completed_causal_projector_current_arrays_reused_bitwise']:
        if not np.array_equal(comparison[k],original[k]):raise ValueError('comparison reuse identity changed '+k)
    for name in ('application.npz','result.json'):
        if (core/'PREPARED_GAUSS_v2'/name).read_bytes()!=(core/'PREPARED_GAUSS_v3'/name).read_bytes():
            raise ValueError('completed Gauss applications are not identical')
    for k in ('original_curvature','original_curvature_source','original_integrability_matrix',
        'original_integrability_matrix_source','pointwise_gauge_compensator',
        'pointwise_gauge_compensator_source','pointwise_original_integrability_rows',
        'pointwise_original_integrability_source_rows','pointwise_integrability_singular_values'):
        arrays[k]=comparison[k]
    for k in ('charge_test_value','charge_test_gradient','charge_test_hessian',
        'physical_required_K0_K1_fm','required_dipole_chart_value','required_dipole_chart_gradient',
        'required_dipole_chart_hessian'):
        arrays['prepared_'+k]=gauss[k]
    example=json.loads((core/'RESPONSE_DIAGNOSTICS_v1/candidate2_plus_homogeneous_particle.json').read_bytes())
    diagnostics=json.loads((core/'RESPONSE_DIAGNOSTICS_v1/result.json').read_bytes())
    parent=ROOT/'artifacts/muon_d5_fermion_event_child_20261019/run_1/result.json'
    pins[parent.relative_to(ROOT).as_posix()]=pin(parent)
    for rel in ('scripts/evaluate_muon_causal_data_prerequisites.py','scripts/verify_muon_causal_data_prerequisites.py'):
        pins[rel]=pin(ROOT/rel)
    output.mkdir(parents=True);write_npz(output/'application.npz',arrays)
    result=dict(schema='bhsm.causal-data-prerequisite-consumption.v1',
        source_parent_head='9a6c7766e8a11b571682cdbd8c4ac73884b76af2',input_sha256=pins,
        arrays=dict(sha256=pin(output/'application.npz'),keys=sorted(arrays)),
        comparison=comp,prepared_Gauss=json.loads((core/'PREPARED_GAUSS_v2/result.json').read_bytes()),
        charge_balance=json.loads((core/'CHARGE_BALANCE_v1/result.json').read_bytes()),
        diagnostics=diagnostics,radial17_consumed_example=example,
        inherited_fermion_freedom=json.loads(parent.read_bytes())['fermion_ranks'],
        retained_parent_h=3660,free_incoming_data=40,remaining_h_after_coordinate_pivot=3620,
        physical_h_selected_rank=0,orientation_families=[2,3],both_collars_share_same_parent_h=True,
        radial17_extra_birth_ports_per_target_branch=112,
        physical_inputs_newly_instantiated=[],
        executed_prerequisites=['original pointwise curvature/Higgs time-gauge integrability',
            'causal comparison and weak-Gauss charge derivative consumed by original continuity/current operator',
            'separate enforced, held-data compatibility and independent original differential diagnostics'],
        preparation_target_only=dict(charge=0,dipole_fm=2000,
            physical_achieved_charge_dipole=None,reference_number_position_variance_fm_squared=20000,
            physical_local_charge_variance=None,not_a_dressed_packet_or_Gauss_solution=True),
        physical_d_in=None,physical_initial_Cauchy_data=None,physical_packet_sections=None,
        collider_to_parent_incidence=None,physical_pair_conversion=None,physical_occupation=None,
        physical_state_combination_child_check=None,physical_Gauss_residual=None,
        physical_Cauchy_norm_residual=None,full_formation_residual=None,
        physical_guard=2e-10,physical_admission=False,complete_physical_derivative=False,
        historical_nonpasses_retained=True,once_only_local_native_accounting_unchanged=True,
        no_background_packet_field_or_native_solve_repeated=True,
        NEXT_OPERAND='execute the same-action Gauss-dressed comparison/prepared-state realization and actual collider-to-parent Cauchy incidence; compute odd-sector transition sections/normalized readouts from the interacting pair state, then consume their determined data in the saved parent and child family; no free-RHS coordinate change selects that state')
    dump(output/'result.json',result)
    return dict(arrays_sha256=result['arrays']['sha256'],result_sha256=pin(output/'result.json'),
        physical_causal_data_instantiated=False,physical_admission=False)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    print(json.dumps(run(a.output),sort_keys=True,indent=2))
