"""Certify the missing signed Rayleigh covector from a frozen eigenpair.

Only point and tube D3 contractions are new. No Hessian/eigenpair or history producer
is rerun. The fiber graph point (Y13, lambda(Y13)) is not a shooting root.
"""
import argparse
import io
import json
from pathlib import Path
import sys

import numpy as np
from flint import arb, arb_mat, ctx, fmpq

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'src')]
import certify_n12_gate7_accepted_replay_center_outward_74d as action
from bhsm.interface import ball_factored_arb_integrand as factored
from bhsm.interface import sparse_arb_mixed_jets as sparse
from checkpoint_n12_gate7_66d_tangent_binding import amat, bound, digest, encoded
from audit_n12_gate7_history_jet_prerequisites import BASE, FIBER, FIXED, DF, interval


def calculate():
    ctx.prec = 512
    sources = {}

    def bind(p, expected=None):
        sha = digest(p)
        if expected is not None and sha != expected:
            raise ValueError('changed source: ' + str(p))
        sources[str(p.resolve())] = sha

    bind(FIBER)
    owner = json.loads(FIBER.read_bytes())
    name = next(k for k in owner['source_SHA256'] if k.endswith('endpoint_013\\record.json'))
    record_path = Path(name)
    bind(record_path, owner['source_SHA256'][name])
    record = json.loads(record_path.read_bytes())
    proof = record['report']['point_eigenpair_proof']
    if not (proof['validation_passed'] and proof['normalized_eigenpair_enclosed']
            and proof['positive_stored_reference_overlap']
            and proof['selected_zero_based_index_verified'] == 24):
        raise ValueError('normalized oriented selected eigenpair required')
    bind(FIXED, owner['source_SHA256'][FIXED.relative_to(ROOT).as_posix()])
    with np.load(FIXED) as z:
        state = np.array([arb(float(v)) for v in z['projected_states'][13]], dtype=object)
        weights = z['state_weights']
        diagnostic = z['descriptor_gradient_action_diagnostic'][13]
    point_path = record_path.with_name('eigenpair.npz')
    bind(point_path, owner['source_SHA256'][str(point_path)])
    with np.load(point_path) as z:
        if not all(fmpq(str(a)) == b.fmpq() and fmpq(str(r)) == 0 for a, r, b in
                   zip(z['center_state_mid_q'], z['center_state_rad_q'], state, strict=True)):
            raise ValueError('point/state mismatch')
        def balls(key):
            return np.array([arb(str(c)) + arb(0, arb(str(r))) for c, r in
                             zip(z[key+'_mid_q'], z[key+'_rad_q'], strict=True)], dtype=object)
        tube_state = balls('raw_segment_hull')
        tube_eigenpair = balls('eigenpair_box')
    if not (record['report']['validation_passed'] and record['report']['uniform_action_eigenpair_enclosed']
            and record['report']['positive_original_reference_overlap']):
        raise ValueError('uniform oriented selected-line witness required')
    witness = [arb(m) + arb(0, arb(r)) for m, r in
               zip(proof['target_midpoints_rational'], proof['target_radii_rational'], strict=True)]
    psi = np.array([arb(0)] * 37 + witness[:61], dtype=object)
    directions = np.full((98, 98), arb(0), dtype=object)
    for j in range(98):
        directions[j, j] = 1 / arb(float(weights[j]))
    # The maps are fixed affine geometry. Build them at derivative order zero;
    # do not assemble g/H or resolve the selected line to obtain them.
    maps = [action._dense_mapping(action._integrand(state, n, 0).maps)
            for n in range(action.POINTS)]
    with sparse.use_optimized_mixed(action), factored.use_ball_factored_integrand(action, state):
        gradient = np.asarray(action._contracted_action(
            state, [psi[:, None], psi[:, None], directions], maps), dtype=object).reshape(1, 98)
    tube_psi = np.array([arb(0)] * 37 + list(tube_eigenpair[:61]), dtype=object)
    with sparse.use_optimized_mixed(action), factored.use_ball_factored_integrand(action, tube_state):
        tube_gradient = np.asarray(action._contracted_action(
            tube_state, [tube_psi[:, None], tube_psi[:, None], directions], maps), dtype=object).reshape(1, 98)
    if not all(a.contains(b) for a, b in zip(tube_gradient.flat, gradient.flat, strict=True)):
        raise ValueError('uniform covector must contain point covector')
    if not all(v.is_finite() for v in gradient.flat):
        raise ArithmeticError('finite covector required')
    g = arb_mat(1, 98, list(gradient.flat))
    # Independent saved uniform contraction checks the state/action scaling.
    df_record = DF / 'record.json'
    bind(df_record)
    bind(DF / 'derivative.npz', json.loads(df_record.read_bytes())['data_SHA256'])
    with np.load(DF / 'derivative.npz') as z:
        cp_uniform = arb(str(z['descriptor_contractions_mid_q'][0])) + arb(0, arb(str(z['descriptor_contractions_rad_q'][0])))
    weighted_psi = arb_mat(98, 1, [arb(float(weights[i])) * psi[i] for i in range(98)])
    cp_point = (g * weighted_psi)[0, 0]
    if not cp_uniform.contains(cp_point):
        raise ValueError('point covector contradicts the saved uniform Dlambda[Psi] contraction')
    comparison = bound(g - amat(diagnostic[None, :]))
    radii = np.array([[v.rad().upper() for v in gradient.flat]], dtype=object)
    uncertainty = bound(arb_mat(1, 98, list(radii.flat)))
    # A reproducible coordinate witness for a relevant nonzero derivative.
    index = int(np.argmax([float(abs(v.mid())) for v in gradient.flat]))
    derivative = gradient[0, index]
    if derivative.contains(0):
        raise ArithmeticError('coordinate transversality not resolved')
    physical = BASE / 'BHSM_N12_GATE7_CORRELATED_DESCRIPTOR_AUGMENTED_JACOBIANS.npz'
    bind(physical, owner['source_SHA256'][physical.relative_to(ROOT).as_posix()])
    with np.load(physical) as z:
        B = amat(z['endpoint_physical_tangent_action'][13])
    history_path = BASE / 'gate7_full_shooting_owner_20260926/arrays.npz'
    history_report = history_path.with_name('report.json')
    bind(history_report)
    bind(history_path, json.loads(history_report.read_bytes())['arrays_SHA256'])
    with np.load(history_path) as z:
        V = amat(z['left_child_history'])
    fiber_row = g * B / arb(1e-7)
    gV = fiber_row * arb_mat(73, 66, [V[i,j] for i in range(73) for j in range(66)])
    delta = gV - arb_mat(1, 66, [V[73,j] for j in range(66)])
    appended = BASE / 'gate7_appended_fiber_center_20260926'
    bind(appended / 'report.json')
    bind(appended / 'arrays.npz', json.loads((appended / 'report.json').read_bytes())['arrays_SHA256'])
    with np.load(appended / 'arrays.npz') as z:
        old_delta = amat(z['left_history_descriptor_adjustment'])
    delta_difference = bound(delta - old_delta)
    for module in (action, factored, sparse):
        bind(Path(module.__file__).resolve())
    for name in ('src/bhsm/interface/factored_arb_integrand.py',
                 'src/bhsm/interface/physical_arb_inputs.py',
                 'src/bhsm/interface/aether_forward_c2_descriptor_cover.py',
                 'src/bhsm/interface/aether_n3_exact_full_local_action_jet_v17_60.py',
                 'scripts/checkpoint_n12_gate7_66d_tangent_binding.py',
                 'scripts/audit_n12_gate7_history_jet_prerequisites.py'):
        bind(ROOT / name)
    bind(Path(__file__).resolve())
    report = dict(
        status='POINT_AND_AFFINE_TUBE_FIBER_COVECTORS_CERTIFIED_HISTORY_JET_OPEN',
        base_commit='eef4149c7d0df292eb40731df2e35490dfafa18c', source_SHA256=sources,
        formula='g(v)=D3 A(Y13)[(0,psi),(0,psi),W_state^-1 v]',
        branch_index=24, orientation='positive frozen-reference overlap; Euclidean-unit raw 61-line',
        coordinate_domain='98 weighted action-state coordinates; no independent descriptor direction',
        graph_center=dict(Y13_unchanged=True, s_star=interval(witness[61]),
            fiber_relation='s_star is the SAME selected eigenvalue object; lambda(Y13)-s_star=0 by graph definition.',
            shooting_root_certified=False, constraints_root_certified=False,
            previous_descriptor_replaced_in_frozen_files=False),
        covector_radius_Frobenius_upper=uncertainty,
        affine_tube_covector_radius_Frobenius_upper=bound(arb_mat(1,98,[v.rad().upper() for v in tube_gradient.flat])),
        affine_tube_coordinate86=interval(tube_gradient[0,86]),
        affine_tube_coordinate86_positive=bool(tube_gradient[0,86]>0),
        affine_tube_scope='Uniform on the SAME certified affine state-domain and selected-line family in endpoint_013/eigenpair.npz. Not a root enclosure or a certificate that a recentered history lies in that affine domain.',
        uniform_point_containment=True,
        point_cpsi=interval(cp_point), point_cpsi_contained_in_saved_uniform_contraction=True,
        old_diagnostic_covector_difference_upper=comparison,
        nonzero_derivative=dict(action_coordinate_zero_based=index, enclosure=interval(derivative),
                               sign=1 if derivative>0 else -1),
        left_history_fiber_defect_upper=bound(delta),
        owner_candidate_left_fiber_derivative_residual_upper=delta_difference,
        comparison_scope='Enclosed g at the old Y13 applied to stored columns as a diagnostic. No transfer of those columns to a fiber-consistent shooting history is asserted.',
        new_scientific_work='Two 98-output D3 contractions, at exact stored Y13 and over the saved affine endpoint state domain, with certified eigenline uncertainty.',
        hessian_or_eigenpair_producer_rerun=False, finite_difference_used=False,
        uniform_recentered_covector_certified=False, full_history_jet_certified=False,
        Layer_C_rebound=False, tolerances_changed=False, Gate7_closed=False,
        FULL_BHSM_COMPLETE=False)
    arrays = {}
    for key, value in (('gradient_action', gradient), ('affine_tube_gradient_action', tube_gradient),
                       ('left_history_fiber_defect_proof', np.array(delta.entries(), dtype=object).reshape(1,66))):
        arrays[key+'_mid_q'] = np.array([str(v.mid().fmpq()) for v in value.flat]).reshape(value.shape)
        arrays[key+'_rad_q'] = np.array([str(v.rad().upper().fmpq()) for v in value.flat]).reshape(value.shape)
    return report, arrays


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--out', type=Path, required=True)
    args=parser.parse_args(); report, arrays=calculate()
    args.out.mkdir(parents=True, exist_ok=False)
    buffer=io.BytesIO(); np.savez_compressed(buffer, **arrays)
    (args.out/'arrays.npz').write_bytes(buffer.getvalue())
    report['arrays_SHA256']=digest(args.out/'arrays.npz')
    (args.out/'report.json').write_bytes(encoded(report))
    print(report['status']); print(json.dumps({k:report[k] for k in
        ('covector_radius_Frobenius_upper', 'old_diagnostic_covector_difference_upper',
         'nonzero_derivative', 'owner_candidate_left_fiber_derivative_residual_upper')}, indent=2))


if __name__ == '__main__':
    main()
