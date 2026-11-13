"""Recover port identities and execute one finite forcing-column control.

Frozen Gate7 producers and all physical/history solvers are never invoked.
Cached matrices are inspected for identities/shapes, not re-evaluated.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))
from control_muon_interface_forcing import execute_control
from bhsm.interface.ae4_stratified_dirac_zeta_induced_owner import native_spectral_length_contract


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf8')


def git(where, *args):
    return subprocess.check_output(['git', '-c', 'gc.auto=0', '-c', 'maintenance.auto=false', *args], cwd=where, text=True).strip()


def identity(path):
    raw = path.read_bytes()
    return dict(path=str(path.resolve()), sha256=hashlib.sha256(raw).hexdigest(),
                canonical_LF_sha256=hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest()
                if path.suffix in ('.py', '.json', '.md') else None)


def run(output, history):
    if output.exists():
        raise FileExistsError('Fresh output required; preserve earlier scientific caches')
    output.mkdir(parents=True)
    start = time.perf_counter()
    base = history / 'artifacts/flagship_integration'
    cache_names = dict(geometric_material='gate7_geometric_material_port_20260927',
                       joint_port='gate7_joint_port_20260927',
                       residual_jet='gate7_coupled_fiber_center_20260927/jet',
                       launch='gate7_launch_response_20260927')
    paths = {name: ROOT / relative for name, relative in dict(
        replay='scripts/replay_muon_native_interface_bulk_forcing.py',
        control='scripts/control_muon_interface_forcing.py',
        adapter='src/bhsm/interface/muon_native_interface_bulk_forcing.py',
        tests='tests/test_muon_native_interface_bulk_forcing.py',
        recovered_port='src/bhsm/interface/joint_boundary_port_reduction.py',
        recovered_heat='src/bhsm/interface/heat_zeta_mixed_boundary_launch.py',
        recovered_material='src/bhsm/interface/geometric_material_port.py',
        current_owner='src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',
        current_branch_jets='src/bhsm/interface/muon_native_support_loss_cutoff.py',
        frozen_local='artifacts/muon_source_jet_20261002/frozen_local.json').items()}
    for name, relative in dict(residual_producer='scripts/solve_n12_gate7_fiber_constrained_center.py',
                               port_producer='scripts/derive_n12_gate7_joint_port_reduction.py',
                               material_producer='scripts/bind_n12_gate7_geometric_material_port.py',
                               signed_owner_ledger='scripts/evaluate_n12_gate7_current_contractions.py',
                               trace_source='src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py').items():
        paths[name] = history / relative
    cache_roles = {}
    selected = dict(geometric_material=('trace_action_3x98_mid_q', 'local_required_material_4x73_mid_q'),
                    joint_port=('local125_forcing_mid_q', 'local125_port_normal_derivative_mid_q'),
                    residual_jet=('J125_mid_q',),
                    launch=('launch_action_mid_q', 'corrected_state_action_mid_q', 'native_event_7x98_mid_q'))
    for name, folder in cache_names.items():
        arrays = base / folder / 'arrays.npz'; report_path = base / folder / 'report.json'
        paths[name + '_arrays'] = arrays; paths[name + '_report'] = report_path
        report = json.loads(report_path.read_text(encoding='utf8'))
        with np.load(arrays, allow_pickle=False) as z:
            shapes = {key: list(z[key].shape) for key in selected[name]}
        cache_roles[name] = dict(shapes=shapes, saved_status=report['status'],
                                 saved_arrays_sha256=report['arrays_SHA256'], physical_operator_replayed=False)
        if identity(arrays)['sha256'].upper() != report['arrays_SHA256'].upper():
            raise ValueError('Required cache identity changed: ' + name)
        if name == 'geometric_material':
            cache_roles[name].update(rows=report['rows'], no_double_counting=report['no_double_counting'],
                                     seven_action_seed_requirement_retired=report['seven_action_seed_requirement_retired'])
    recovered = {}
    for name in ('joint_boundary_port_reduction.py', 'heat_zeta_mixed_boundary_launch.py', 'geometric_material_port.py'):
        original = history / 'src/bhsm/interface' / name
        copied = ROOT / 'src/bhsm/interface' / name
        if original.read_bytes() != copied.read_bytes():
            raise ValueError('Recovered helper differs from scientific source: ' + name)
        paths['original_' + name] = original
        recovered[name] = dict(sha256=identity(original)['sha256'], copied_byte_identical=True,
                               last_source_commit=git(history, 'log', '-1', '--format=%H', '--', 'src/bhsm/interface/' + name))
    save(output / 'input_hashes.json', {name: identity(path) for name, path in paths.items()})
    save(output / 'starting_revision.json', dict(HEAD=git(ROOT, 'rev-parse', 'HEAD'),
        branch=git(ROOT, 'branch', '--show-current'), working_tree_status=git(ROOT, 'status', '--short'),
        scientific_reference='524ed90689bd5923c249bba2e699abf627e703cd',
        read_only_history_HEAD=git(history, 'rev-parse', 'HEAD'), read_only_history_branch=git(history, 'branch', '--show-current')))
    (output / 'starting_worktree.diff').write_text(git(ROOT, 'diff', '--binary') + '\n', encoding='utf8')
    save(output / 'recovered_helpers.json', recovered)
    save(output / 'cache_roles.json', cache_roles)
    identification = dict(
        actual_cached_residual='F_local=[C_left/s_left; C_right/s_right; T_test HS_13; (lambda_left-s_descriptor,left)/1e-7]',
        HS_13='z1-z0-h*(f0+4*fmid+f1)/6, h=1/4',
        row_count={'left_constraints': 25, 'right_constraints': 25, 'flow_matching': 74, 'descriptor': 1},
        recovered_F_n='J125 (125x125), local corrected interval-13 constraint/flow/descriptor derivative',
        recovered_F_p='local125_forcing (125x73), launch forcing; not F_b',
        recovered_g_n='local125_port_normal_derivative (7x125), output derivative; not F_b',
        required_identification='F_local=C E_owner in common internal coordinates and inherited domains',
        source_partial='D_s F_local=C h_psi+(D_s C)E_owner at fixed internal coordinates',
        internal_partial='F_n=C H_owner+(D_n C)E_owner',
        at_owned_stationarity='E_owner=0 => f_local=C h_psi and F_n=C H_owner; same response if the consumed row/dual map is valid',
        dual_contraction='h_psi^dagger H_owner^-1 h_psi=f_local^dagger C^-dagger F_n^-1 f_local; row transformations are not form congruences',
        signed_action_ledger='Gamma_attached-Gamma_SM_zeta+Gamma_heat=Gamma_classical+Gamma_heat',
        retained_caveat='The attached-action flow is not assumed stationary for L_classical after vacuum subtraction',
        same_current_AE4_support_loss_base_proved=False, row_or_consumed_dual_map_C=None,
        physical_seven_port_source_map_provided=False,
        scope='Examined concrete producers and retained cache roles; no assertion of absence from all scientific records')
    save(output / 'row_identification.json', identification)
    # Execute the new finite control exactly once; never invoke the old producers.
    control, arrays = execute_control()
    if not control['all_checks_pass']:
        raise ArithmeticError('New finite control failed')
    save(output / 'control.json', control)
    save(output / 'control_exact_arrays.json', {name: [[str(v) for v in row] for row in matrix.tolist()]
                                               for name, matrix in arrays.items()})
    ownership = dict(
        geometric_trace=dict(status='RECOVERED_LOCAL_GEOMETRIC_MAP', note='T Dq + explicit shape/frame; not three action seeds'),
        material_momentum_flux=dict(status='RECOVERED_LOCAL_DYNAMIC_MAP', note='DP, DF-DG-D2P[X,u]-DP[DXu]; no static replacement'),
        reset_contact_Wentzell_scalar_constraint=dict(status='RETAINED_SIGNED_DEPENDENCIES', note='Count once when same-owner assembly is supplied; no independent zero-filled additions'),
        same_owner_stationary_forcing=dict(status='UNEVALUATED', value=None),
        surface_Jacobi=dict(status='UNEVALUATED', value=None),
        kinetic_inertia=dict(status='UNEVALUATED', value=None),
        native_bulk_heat=dict(status='UNEVALUATED', value=None),
        state_variation=dict(status='UNEVALUATED', value=None),
        contact=dict(status='UNEVALUATED', value=None),
        domain_boundary=dict(status='UNEVALUATED', value=None),
        completion_counterterm=dict(status='UNEVALUATED', value=None),
        strong_within_native=dict(status='UNEVALUATED_SUBSET_OF_NATIVE', value=None))
    next_operand = dict(
        name='same-owner normal-source Euler column in the existing seven-port coordinates',
        symbol='h_psi=D_b E_owner[b_psi], b_psi=B_boundary[xi_psi]',
        defining_weak_equation='<eta,h_psi>=D_Phi D_X S_bulk^owner[eta,xi_psi] for allowed zero-trace eta',
        input_space='action-selected support-loss normal direction, mapped to 3 trace + 2 momentum + 2 dynamic-flux coordinates',
        output_space='owned internal Euler/constraint dual (or its one consumed local-row/dual image)',
        concrete_producer='same-owner bulk/interface variation with moving-seam trace, canonical momentum, conormal and momentum-rate pullback',
        concrete_consumer='solve_bulk_forcing_column: F_n delta=-f_local, then owned-dual impedance contraction',
        assembly_stop='No supplied physical normal-to-state/material column or C E_owner identification; cached F_p and g_n cannot form F_b b_psi',
        not_required='all seven physical directions, all 73 launches, full 7x73 materialization or Gate7 closure',
        value=None, physical_missing_postulate_not_asserted=True)
    physical = dict(xi_psi=None, b_psi=[None] * 7, F_n_same_owner=None, f_psi=None,
                    deltaPhi_psi=None, owned_residual_norm=None, z_psi=None,
                    r=None, i=None, c=None, R_ind=None, a_mu=None, g_mu=None)
    result = dict(classification='SEVEN_PORT_OWNER_RECONCILIATION_AND_ONE_COLUMN_CONTROL__NO_NATIVE_EVALUATION',
                  physical=physical, next_operand=next_operand, ownership=ownership,
                  owner_contract=native_spectral_length_contract(),
                  frozen_local=json.loads(paths['frozen_local'].read_text(encoding='utf8')),
                  execution=dict(new_finite_control_runs=1, historical_producer_runs=0,
                                 physical_forcing_columns=0, physical_response_solves=0,
                                 physical_transfer_directions=0, full_7x73_recomputations=0, physical_heat_applications=0),
                  numerical_error_scope=control['error_scope'], same_owner_identification=identification)
    save(output / 'result.json', result)
    save(output / 'checkpoint.json', dict(id='BHSM_MUON_SEVEN_PORT_ONE_COLUMN_20261007',
         completed='existing 3/4 map and one-column algebra recovered; cached F_p/g_n distinguished; row/dual correction derived and tested',
         next_operand=next_operand, native_values_evaluated=False, replay_old_production=False))
    snapshots = output / 'executed_source'; snapshots.mkdir()
    for name in ('adapter', 'replay', 'control', 'tests', 'recovered_port', 'recovered_heat', 'recovered_material'):
        shutil.copy2(paths[name], snapshots / paths[name].name)
    save(output / 'replay_receipt.json', dict(elapsed_seconds=time.perf_counter() - start,
         finite_control_checks=control['checks'], old_producers_invoked=[],
         output_hashes={p.name: identity(p)['sha256'] for p in output.iterdir() if p.is_file()},
         test_history=[dict(passed=11, failed=1, reason='new test passed a string to Arb.contains; corrected explicit scalar conversion'),
                       dict(passed=12, failed=0, command='pytest --noconftest -q tests/test_muon_native_interface_bulk_forcing.py')]))
    print(json.dumps(dict(output=str(output.resolve()), control_passed=control['all_checks_pass'], physical_evaluations=0)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--history-repository', type=Path, default=Path(r'C:\Users\carbe\OneDrive\Documents\CODEX\Berger-Hopf-Standard-Model'))
    args = parser.parse_args()
    run(args.output, args.history_repository)
