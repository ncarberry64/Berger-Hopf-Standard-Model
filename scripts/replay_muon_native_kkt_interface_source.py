"""Replay direct same-owner KKT source controls; never launch old campaigns.

All new numerical values are finite controls. The physical packet remains
UNEVALUATED until the audited current owner/source/domain operands exist.
Use a fresh output directory; deterministic science files exclude timings.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import sympy as sp
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from bhsm.interface.muon_native_kkt_interface_source import (
    finite_control_action, solve_owner_kkt, finite_control_branch_jets,
)
from bhsm.interface.muon_native_kkt_downstream import (
    continue_native_kkt_downstream, make_control_downstream_inputs,
)
from bhsm.interface.joint_boundary_port_reduction import moving_port_jet
from bhsm.interface.ae4_stratified_dirac_zeta_induced_owner import native_spectral_length_contract

STARTING_HEAD = 'da155f24a2663d1570d9d78acc9771197fc16670'
SCIENTIFIC_REFERENCE = '524ed90689bd5923c249bba2e699abf627e703cd'
MILESTONE = ROOT / 'artifacts/muon_native_kkt_interface_source_20261007'


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n',
                    encoding='utf8', newline='\n')


def exact(value):
    if isinstance(value, sp.MatrixBase):
        return [[str(x) for x in row] for row in value.tolist()]
    return str(value)


def amat(matrix):
    return arb_mat([[str(x) for x in row] for row in matrix.tolist()])


def source_hash(relative):
    payload = (ROOT / relative).read_bytes().replace(b'\r\n', b'\n')
    return dict(path=relative, canonical_LF_sha256=hashlib.sha256(payload).hexdigest())


def execute_control():
    action = finite_control_action()
    result = solve_owner_kkt(action)
    H, h, delta = result['H_KKT'], result['h_psi'], result['delta_psi']
    # General invertible row mixing, with no row covector used for z.
    C = sp.Matrix([[2, 1, 0], [0, 3, 1], [0, 0, 5]])
    row_delta = -(C * H).LUsolve(C * h)
    owner_z_from_row_response = sp.simplify(result['L_ss'] + (h.T * row_delta)[0])
    naive_row_z = sp.simplify(result['L_ss'] + ((C * h).T * row_delta)[0])
    omit_Rs = result['L_eta_s'].col_join(sp.zeros(len(action.constraints), 1))
    omit_contact = result['S_eta_s'].col_join(result['R_s'])
    # Diagnostic omissions, explicitly WRONG finite controls only.
    omitted_source = H.LUsolve(-omit_Rs)
    omitted_contact = H.LUsolve(-omit_contact)
    eps = sp.Symbol('eps', real=True)
    B = sp.Matrix([sp.Rational(k + 1, 23) for k in range(7)])
    DB = sp.Matrix([sp.Rational(1, k + 31) for k in range(7)])
    lambda_base = sp.Matrix([action.base[l] for l in action.multipliers])
    lambda_response = result['delta_lambda_psi']
    moving = moving_port_jet(amat(B), amat(lambda_base), amat(lambda_response), [amat(DB)])
    moving_exact = sp.diff((B + eps * DB) * (lambda_base + eps * lambda_response), eps).subs(eps, 0)
    jets = finite_control_branch_jets()
    owner_id = hashlib.sha256(json.dumps(dict(owner=action.owner_identity,
        source=action.source_provenance), sort_keys=True).encode()).hexdigest()
    for supplied in jets.values():
        supplied['owner_identity'] = owner_id
    downstream = continue_native_kkt_downstream(**jets, owner_identity=owner_id,
        downstream=make_control_downstream_inputs(owner_id))
    checks = dict(
        direct_KKT_residual_derivative=result['h_psi'] == result['direct_source_derivative'],
        source_dependent_constraint_retained=result['R_s'] != sp.zeros(len(action.constraints), 1),
        multiplier_mixed_contact_retained=result['multiplier_contact'] != sp.zeros(len(action.eta), 1),
        multiplier_source_source_contact_retained=result['multiplier_source_contact'] != 0,
        no_lambda_s_in_fixed_source=not result['h_psi'].free_symbols,
        response_replay=result['replay'] == sp.zeros(H.rows, 1),
        multiplier_response_retained=lambda_response != sp.zeros(len(action.multipliers), 1),
        direct_full_action_equals_schur=result['direct_minus_schur'] == 0,
        Arb_owned_response_residual_contains_zero=all(x.contains(0) for x in result['arb_replay'].entries()),
        row_equivalence_preserves_response=row_delta == delta,
        owner_impedance_invariant_under_row_mixing=owner_z_from_row_response == result['z_psi'],
        naive_row_contraction_changes_impedance=naive_row_z != result['z_psi'],
        dropping_R_s_changes_response=omitted_source != delta,
        dropping_multiplier_mixed_contact_changes_response=omitted_contact != delta,
        exactly_seven_kinematic_coordinates=action.b_psi.shape == (7, 1),
        moving_port_product_rule_retained=all((moving[k, 0] - arb(str(moving_exact[k]))).contains(0) for k in range(7)),
        moving_port_DB_nonzero=DB * lambda_base != sp.zeros(7, 1),
        total_impedance_branch_value_replays=sp.Rational(jets['owner_z']['value']) == result['z_psi'],
        supplied_finite_chain_reaches_Pauli=all(stage['status'] == 'EVALUATED_SUPPLIED_OWNER_OPERANDS'
                                               for stage in downstream['stages'].values()),
        finite_photon_response_replay=downstream['stages']['native_photon_response']['value']['residual_norm'] < 1e-15,
        no_control_promoted_to_physical=downstream['physical_promotion'] is False,
    )
    if not all(checks.values()):
        raise ArithmeticError('new direct-action finite control failed: ' + str(checks))
    exact_names = ('E_base', 'L_etaeta', 'R_eta', 'S_eta_s', 'R_eta_s', 'R_s',
                   'multiplier_contact', 'S_ss', 'R_ss', 'multiplier_source_contact',
                   'L_ss', 'H_KKT', 'h_psi', 'delta_psi', 'delta_eta_psi',
                   'delta_lambda_psi', 'replay', 'z_psi', 'direct_quadratic', 'direct_minus_schur')
    return dict(
        classification='EXACT_RATIONAL_AND_ARB_FINITE_ACTION_CONTROL__NOT_PHYSICAL_BHSM',
        owner_identity=dict(action.owner_identity),
        xi_psi_provenance=action.source_provenance,
        b_psi=exact(action.b_psi),
        canonical_port_order=['trace_1', 'trace_2', 'trace_3', 'momentum_1', 'momentum_2', 'dynamic_flux_1', 'dynamic_flux_2'],
        KKT_base={str(k): str(v) for k, v in action.base.items()},
        multipliers=[str(action.base[l]) for l in action.multipliers],
        action_sectors=[dict(name=t.name, sign=t.sign, expression=str(t.expression), zero_provenance=t.zero_provenance)
                        for t in action.action_sectors],
        constraints=[str(x) for x in action.constraints],
        fixed_source_coordinates=list(result['fixed_coordinates']),
        exact={name: exact(result[name]) for name in exact_names},
        Arb=dict(precision_bits=ctx.prec, response=[str(x) for x in result['arb_delta'].entries()],
                 owned_residual=[str(x) for x in result['arb_replay'].entries()],
                 z=str(result['arb_z']), direct_minus_schur=str(result['arb_direct_minus_schur'])),
        row_mixing=dict(C=exact(C), response=exact(row_delta),
                        owner_z=exact(owner_z_from_row_response), incorrect_naive_row_z=exact(naive_row_z)),
        moving_port=dict(B=exact(B), DB=exact(DB), lambda_base=exact(lambda_base),
                         lambda_response=exact(lambda_response), derivative=exact(moving_exact)),
        same_control_action_total_branch_jets=jets,
        downstream=downstream, checks=checks, all_checks_pass=all(checks.values()),
        error_scope='Exact rational finite-action identities plus 256-bit Arb rounding enclosures; downstream supplied-jet arithmetic is binary64 without an enclosure. No physical, continuum, discretization, domain, heat-tail or transfer error bound.',
    )


def run(output):
    if output.exists():
        raise FileExistsError('fresh output directory required; preserve prior scientific artifacts')
    ctx.prec = 256
    control = execute_control()
    audit = json.loads((MILESTONE / 'owner_audit.json').read_text(encoding='utf8'))
    physical = dict(audit['missing_physical_operands'])
    physical.update(owned_residual=dict(status='UNEVALUATED', value=None),
                    direct_vs_schur=dict(status='UNEVALUATED', value=None))
    downstream = continue_native_kkt_downstream(owner_z=None, owner_identity=None)
    sources = (
        'src/bhsm/interface/muon_native_kkt_interface_source.py',
        'src/bhsm/interface/muon_native_kkt_downstream.py',
        'scripts/replay_muon_native_kkt_interface_source.py',
        'tests/test_muon_native_kkt_interface_source.py',
        'tests/test_muon_native_kkt_downstream.py',
        'src/bhsm/interface/geometric_material_port.py',
        'src/bhsm/interface/joint_boundary_port_reduction.py',
        'src/bhsm/interface/muon_native_support_loss_cutoff.py',
        'artifacts/muon_native_kkt_interface_source_20261007/owner_audit.json',
    )
    provenance_paths = tuple(p['path'] for p in audit['audited_producers'])
    hashes = {p: source_hash(p) for p in sorted(set(sources + provenance_paths)) if (ROOT / p).exists()}
    result = dict(
        classification='DIRECT_OWNER_ACTION_KKT_SOURCE_IMPLEMENTED_AND_CONTROLLED__PHYSICAL_SOURCE_UNEVALUATED',
        starting_HEAD=STARTING_HEAD, scientific_reference=SCIENTIFIC_REFERENCE,
        executed_HEAD=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        branch='codex/muon-parent-maxwell-density-review',
        owner_action_version=audit['current_owner']['action_version'],
        owner_action_domain_identity=dict(action='BHSM-AE-4.0.0', domain=None, pairing=None, stationary_branch=None),
        owner_contract=native_spectral_length_contract(), physical=physical,
        physical_signed_sector_ledger=audit['signed_action_sectors'], downstream=downstream,
        scientific_error_scope='Physical operands and their error estimates remain UNEVALUATED. Finite control rounding is not an uncertainty for BHSM or its muon Pauli coefficient.',
        next_consumed_operand=dict(
            producer='Current same-owner weak-action pullback along action-selected xi_psi at AE4 support loss',
            fixed_coordinates=['eta', 'lambda'],
            required=['xi_psi', 'b_psi(3+2+2)', 'stationary owner base', 'lambda',
                      'L_etaeta', 'R_eta', 'S_eta_s', 'R_eta_s', 'R_s', 'L_ss'],
            source='h_psi=[S_eta_s+R_eta_s^dagger lambda;R_s]',
            solve='H_KKT delta_psi=-h_psi',
            impedance='z_psi=L_ss+h_psi^dagger delta_psi',
            further_inputs='Same-branch surface Jacobi, inertia and total v,J,vJ jets; native heat/domain/completion and response operands',
        ),
        execution=dict(physical_source_columns=0, physical_response_solves=0, physical_heat_evaluations=0,
                       finite_source_columns=1, same_column_exact_and_Arb_replays=True,
                       historical_producers_invoked=[], full_Gate7_campaigns=0, launch_73_recomputations=0,
                       cached_F_p_consumed=False, cached_g_n_consumed=False,
                       local_QED_changed=False, primitive_photon_refinement_runs=0),
    )
    output.mkdir(parents=True)
    save(output / 'control.json', control)
    save(output / 'result.json', result)
    save(output / 'input_hashes.json', hashes)
    print(json.dumps(dict(output=str(output), finite_checks_pass=control['all_checks_pass'], physical_evaluations=0)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    run(parser.parse_args().output)
