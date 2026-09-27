"""Bind actual native output definitions and isolate the missing joint owner.

Read-only source/packet binding; no physical or historical witness producer.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from bhsm.interface.native_seven_outputs import native_row_indices

BASE = ROOT/'artifacts/flagship_integration'
OWNER = ROOT/'src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py'
PACKETS = {
    'joint_seed': 'BHSM_N12_GATE7_JOINT_HEAT_COTANGENT_REVERSE_SEED.json',
    'force_functional': 'BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json',
    'seam_at_minus_one': 'BHSM_N12_AE2_COVARIANT_SEAM_ENCLOSURE_Z_MINUS_1.json',
    'signed_adjoint': 'BHSM_N12_C2_1222_SIGNED_ADJOINT_ASSEMBLY.json',
    'local': 'gate7_launch_response_20260927/report.json',
    'prior_split': 'gate7_joint_port_20260927/report.json',
}


def digest(path):
    data = path.read_bytes()
    if path.suffix in ('.py', '.json', '.md'):
        data = data.replace(b'\r\n', b'\n')
    return hashlib.sha256(data).hexdigest().upper()


def definition(path, names):
    source = path.read_text(encoding='utf-8'); lines = source.splitlines()
    functions = {n.name: n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)}
    return dict(path=path.relative_to(ROOT).as_posix(), SHA256=digest(path), functions={
        name: dict(start=functions[name].lineno, end=functions[name].end_lineno,
                   text='\n'.join(lines[functions[name].lineno-1:functions[name].end_lineno]))
        for name in names})


def calculate(out):
    docs = {key: json.loads((BASE/name).read_bytes()) for key, name in PACKETS.items()}
    # Confirm the exact numerical owner remains absent in the cited dependency.
    matching = docs['joint_seed']['matching_audit']
    if not all(matching[k] == 'ACTUALLY_MISSING' for k in
               ('actual_complete_joint_operator_value', 'actual_complete_joint_operator_first_jet')):
        raise ValueError('joint owner status changed: bind the new physical realization')
    interface = ROOT/'src/bhsm/interface'
    sources = [definition(OWNER, ['_trace_jacobian_at_order', '_canonical_pair_at_order', '_child_rows_at_order']),
               definition(interface/'aether_constraint_consistent_sobolev_lift_v15_84.py', ['constraint_residual']),
               definition(interface/'aether_sobolev_galerkin_pencil_lift_v15_81.py', ['dimensions']),
               definition(interface/'forward_finite_endpoint_heat_force.py', ['heat_regulator_value_and_force']),
               definition(interface/'aether_forward_c2_signed_coefficient_adjoint.py', ['signed_coefficient_history_adjoint'])]
    formulas = ['T1(qc-qe)', 'T2(qc-qe)', 'T3(qc-qe)', 'Pc1-Pe1', 'Pc2-Pe2',
                'Gamma_c1+DPc1[Xc]-Fc1+Gamma_e1', 'Gamma_c2+DPc2[Xc]-Fc2+Gamma_e2']
    result = dict(
        status='OUTCOME_C_CURRENT_JOINT_OPERATOR_JET_NOT_REALIZED',
        target='ACTION_OWNED_SEVEN_OUTPUT_JOINT_HISTORY_CONTACT_DERIVATIVE',
        output_definition=dict(name='canonical_seven_boundary_balance', formulas=formulas,
            G7_event=['Tqe1','Tqe2','Tqe3','Pe1','Pe2','Gamma_e1','Gamma_e2'],
            G7_child_required=['Tqc1','Tqc2','Tqc3','Pc1','Pc2',
                               'Fc1-DPc1[Xc]-Gamma_c1','Fc2-DPc2[Xc]-Gamma_c2'],
            residual_identity='R7=diag(I5,-I2)*(G7_child_required-G7_event)',
            original_child_rows=32, original_constraint_rows=25,
            zero_based_native_indices=native_row_indices(12),
            event_orientation=[-1,-1,-1,-1,-1,1,1],
            constraints_retained_in='F_joint; not deleted by output selection',
            interpretation='G7 is the unsigned material reaction. The seven balances equate child-required and event outputs. The frozen local response differentiates only the local event arm.'),
        source_definitions=sources,
        packet_binding={key: dict(path=(BASE/name).relative_to(ROOT).as_posix(), SHA256=digest(BASE/name)) for key,name in PACKETS.items()},
        exact_missing_owner=dict(
            name='CURRENT_CENTER_N12_JOINT_GRADED_HEAT_MINUS_ZETA_OPERATOR_JET',
            functional_owner='forward_finite_endpoint_heat_force::heat_regulator_value_and_force',
            reverse_owner='BHSM_N12_GATE7_JOINT_HEAT_COTANGENT_REVERSE_SEED',
            evidence=matching,
            first_unavailable_inputs='Actual P_joint and its action-owned coefficient/geometry first jet at the recentered node-13 joint history',
            derivative_extension='Mixed boundary/history jets needed to differentiate the physical reaction; include DQ[P_b]P_a + Q P_ab and moving-port/lift terms',
            no_new_environment_law=True),
        boundary_of_available_evidence=dict(
            local_native='Frozen native derivative retained; not recomputed',
            local_border='Prior exact cancellation retained; not replayed',
            historical_split='Prior algebra retained; no test-covector replay',
            z_minus_one=docs['seam_at_minus_one']['claim_boundary'],
            signed_adjoint=docs['signed_adjoint']['adjudication']),
        reduction='F_y^T Lambda=G7_y^T; R_joint=G7_xi-Lambda^T F_xi',
        causal_pullback='Apply existing signed coefficient-history recurrence to seven actual output seeds once available; no additional autonomous source',
        owner_accounting={
            'A_local_native': 'LOCAL_ALREADY_INCLUDED',
            'B_upstream_seam': None, 'C_transported_C2': None,
            'D_reset_U_R': None, 'E_W_phys': None, 'F_gauge_contact': None,
            'G_scalar_topographic_contact': None, 'H_pair_contact': None,
            'I_full_descriptor_constraint_normalization': None, 'J_midpoint_history_incidence': None},
        accounting_scope='Null means classification cannot be adjudicated under Outcome C; active internal terms are not zeroed. Prior local125 cancellation is not a classification of I/J for the full joint system.',
        complete_response=None, delta_history=None, rank_complete=None, rank_delta=None,
        rowwise_correction_norms=None, largest_entry_and_location=None, seven_adjoint_residuals=None,
        promoted=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False,
        producers_run=[], historical_test_covectors_run=False, tolerances_changed=False,
        code_SHA256={p.relative_to(ROOT).as_posix(): digest(p) for p in
                     (Path(__file__), interface/'native_seven_outputs.py')})
    out.mkdir(parents=True, exist_ok=False)
    (out/'report.json').write_bytes((json.dumps(result,sort_keys=True,indent=2)+'\n').encode())
    print(result['status'])


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    calculate(parser.parse_args().out)
