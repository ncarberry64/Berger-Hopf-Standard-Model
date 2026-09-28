"""Evaluate the shared current branch-23 local implicit/clock response.

No ten-sector producer, reset solver, Q66 builder or C2 propagator is called.
The unsplit action derivatives required by the NEW eigenline/hard-response
linearization are evaluated once. They are not another action-sector result.
The temporal/contact/heat internal system is not replaced by this subsystem.
"""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
import solve_n12_gate7_fiber_constrained_center as owner
from checkpoint_n12_gate7_66d_tangent_binding import digest, encoded, restore, bound
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from bhsm.interface.indexed_eigenpair_proposal import indexed_proposal
from bhsm.interface.physical_hs_value import verified_eigenline
from recenter_n12_gate7_current_history_box import recentered_eigenline
from bhsm.interface.current_incoming_formation_family import (
    coefficient_first, local_internal_system, descriptor_clock_first,
    zero_descriptor_clock_germ, matrix,
)
from bhsm.interface.current_action_response_capture import evaluate_shared_rate

BASE = ROOT/'artifacts/flagship_integration'
CANDIDATE = BASE/'gate7_current_reset_connection_20260927/reset_match_complete/candidate.npz'
FRAME = BASE/'gate7_formation_action_basis_20260928/run1'
POINT = BASE/'gate7_current_formation_stationarity_20260927/run1'
LOCAL = BASE/'formation_op_current_20260928/local_run1'


def verified_packet(folder, names):
    report = json.loads((folder/'report.json').read_bytes())
    if digest(folder/'arrays.npz') != report['arrays_SHA256']:
        raise ValueError('saved input changed: '+str(folder))
    with np.load(folder/'arrays.npz') as z:
        return {name: restore(z, name) for name in names}


def scalar(value):
    return dict(midpoint=float(value.mid()), radius_upper=float(value.rad()),
                lower=str(value.lower().fmpq()), upper=str(value.upper().fmpq()))


def calculate(out):
    ctx.prec = 512
    if out.exists():
        raise ValueError('new output directory required')
    candidate_report = json.loads(CANDIDATE.with_name('report.json').read_bytes())
    if digest(CANDIDATE) != candidate_report['candidate_SHA256']:
        raise ValueError('current reset candidate changed')
    frame = verified_packet(FRAME, ['Q66_current', 'Q66_current_raw'])
    point = verified_packet(POINT, ['E1_eigenvalue', 'E1_eigenvalue_J', 'E1_rate'])
    local = verified_packet(LOCAL, ['current_incoming_state_raw', 'local_action_gradient_raw',
                                  'local_action_curvature_66'])
    with np.load(CANDIDATE) as z:
        state = np.array([arb(float(v)) for v in z['joint_state_raw'][98:196]], dtype=object)
        weights, reference = z['state_weights'].copy(), z['branch_reference'].copy()
    if any(not a.contains(b) for a, b in zip(local['current_incoming_state_raw'].entries(), state)):
        raise ValueError('local sectors are not at this incoming state')
    Q, Qraw = frame['Q66_current'], frame['Q66_current_raw']
    s = point['E1_eigenvalue'][0, 0]
    ds = point['E1_eigenvalue_J']*Q
    directions = np.asarray(Q.tolist()+ds.tolist(), dtype=object)
    values, first = coefficient_first(state, Qraw)
    internal, checks = {}, []
    A = owner.action
    original = A._eigenline
    def proposal(hessian, midpoint, ref):
        return indexed_proposal(hessian[37:, 37:], 23, ref)
    A._eigenline = recentered_eigenline(proposal)
    print('Evaluating shared branch-23 eigenline/hard/descriptor first response on Q66', flush=True)
    try:
        with owner.sparse.use_optimized_mixed(A), owner.factored.use_ball_factored_integrand(A, state):
            with verified_eigenline(A, checks, expected_index=23, normalize_proposal_center=True):
                rate, internal = evaluate_shared_rate(A, state, s, weights, reference, directions)
    finally:
        A._eigenline = original
    print('Shared local implicit response evaluated; replaying coupled equations', flush=True)
    system = local_internal_system(internal)
    g_replay = arb_mat(98, 1, list(rate.action_jets.gradient_arb))-local['local_action_gradient_raw']
    H_replay = Qraw.transpose()*matrix(rate.action_jets.hessian_arb)*Qraw-local['local_action_curvature_66']
    lam_replay = arb_mat([[internal['eigenvalue']-s]])
    ds_replay = arb_mat(1, 66, list(internal['deigenvalue']))-ds
    replays = dict(local_gradient=g_replay, frozen_local_curvature=H_replay,
                   saved_selected_eigenvalue=lam_replay, selected_eigenvalue_first=ds_replay,
                   local_internal=system['residual'], local_internal_first=system['first_replay'],
                   local_b_adjoint=system['b_adjoint_replay'],
                   local_b_forward_adjoint=system['b_forward_adjoint_replay'])
    for name, replay in replays.items():
        if not all(v.contains(0) for v in replay.entries()):
            raise ArithmeticError('shared-base replay failed: '+name)
    sf = matrix(internal['scalar_first_dc_dR_db_ddelta'])
    row = lambda i: arb_mat(1, 66, [sf[i, j] for j in range(66)])
    clock, dclock = descriptor_clock_first(
        lapse=values['lapse'], log_lapse_first=first['log_lapse'], descriptor=s,
        descriptor_first=ds, delta=internal['delta'], delta_first=row(3))
    a, da = zero_descriptor_clock_germ(
        lapse=values['lapse'], log_lapse_first=first['log_lapse'],
        cpsi=internal['cpsi'], bpsi=internal['bpsi'], cpsi_first=row(0), bpsi_first=row(2))
    # Product rule BEFORE a norm: lapse, internal response and radius rate
    # remain correlated in the only coefficient consumed by the path germ.
    av = a*values['proper_log_radius_rate']
    dav = da*values['proper_log_radius_rate']+a*first['proper_log_radius_rate']
    arrays = {name+'_value': arb_mat([[v]]) for name, v in values.items()}
    arrays.update({name+'_first_66': v for name, v in first.items()})
    arrays.update({'local_internal_'+name: value for name, value in system.items()})
    arrays.update({name+'_replay': value for name, value in replays.items()})
    arrays.update(current_raw_state=arb_mat(98, 1, list(state)),
                  current_descriptor=arb_mat([[s]]), current_descriptor_first_66=ds,
                  augmented_rate=arb_mat(99, 1, list(rate.value)),
                  augmented_rate_first_66=matrix(rate.derivative),
                  selected_eigenline=arb_mat(61, 1, list(internal['psi'])),
                  selected_eigenvalue=arb_mat([[internal['eigenvalue']]]),
                  hard_response=arb_mat(61, 1, list(internal['hard'])),
                  internal_scalars=arb_mat([[internal[k]] for k in ('cpsi', 'bpsi', 'remainder', 'delta', 'norm_G')]),
                  internal_scalar_first_dc_dR_db_ddelta=sf,
                  descriptor_lookback_proper_clock=arb_mat([[clock]]),
                  descriptor_lookback_proper_clock_first_66=dclock,
                  formal_zero_descriptor_duration_coefficient=arb_mat([[a]]),
                  formal_zero_descriptor_duration_coefficient_first_66=da,
                  formal_radius_history_coefficient=arb_mat([[av]]),
                  formal_radius_history_coefficient_first_66=dav)
    out.mkdir(parents=True)
    save_arrays(out/'arrays.npz', arrays)
    report = dict(
        status='CURRENT_INCOMING_LOCAL_INTERNAL_AND_CLOCK_RESPONSE_EVALUATED_FULL_FAMILY_PENDING',
        scope='Current branch-23 pointwise local implicit subsystem; not a finite incoming history, stationary root, or complete formation internal solve',
        base_commit='6ccc130e', branch_index=23, physical_directions=66,
        local_internal_dimension=124, local_internal_first_shape=[124, 66],
        coefficient_values={k: scalar(v) for k, v in values.items()},
        coefficient_first_norms={k: bound(v) for k, v in first.items()},
        local_internal_scalars={k: scalar(internal[k]) for k in ('cpsi', 'bpsi', 'remainder', 'delta', 'norm_G')},
        eigenpair_proof=checks[0], replays={k: bound(v) for k, v in replays.items()},
        descriptor_consistency=dict(saved_selected_eigenvalue=scalar(s),
            selected_descriptor_contains_zero=s.contains(0),
            previous_supplied_zero_descriptor_is_the_selected_eigenvalue=s.contains(0),
            new_rate_uses_selected_eigenvalue=True,
            lookback_proper_clock=scalar(clock), positive_incoming_clock=bool(clock > 0)),
        clock_response=dict(formal_zero_descriptor_duration_coefficient=scalar(a),
            formal_duration_coefficient_first_norm=bound(da),
            formal_radius_history_coefficient=scalar(av), formal_radius_history_first_norm=bound(dav),
            signed_composition='D(a*v)=v*D a+a*D v, with D a=a*(D log N-D c/c-D b/b)',
            event_germ_at_current_state_is_not_a_certified_event=True,
            finite_amplitude_selected=False, physical_duration=None),
        compression=dict(endpoint_radius_independent_input=False,
            endpoint_radius_first_norm=bound(first['log_radius']),
            endpoint_scalar_potential_first_norm=bound(first['unit_scalar_gauge_potential']),
            endpoint_Weyl_superpotential_first_norm=bound(first['unit_Weyl_superpotential']),
            formal_radius_history_first_is_nonzero=any(not v.contains(0) for v in dav.entries()),
            independent_input_count_after_full_assembly=None,
            no_Q66_column_discarded=True),
        unavailable=dict(current_incoming_launch_first_73=True,
            finite_incoming_coefficient_duration_family=True,
            full_temporal_contact_heat_internal_system=True,
            q66=True, H66=True, B66x73=True),
        ten_local_action_sector_producer_calls=0,
        new_unsplit_local_derivative_calls_for_internal_linearization=1,
        Q66_rebuilt=False, reset_matching_rebuilt=False, C2_prefix_rebuilt=False,
        root_solve_attempted=False, complete=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False,
        source_SHA256={p.relative_to(ROOT).as_posix(): digest(p) for p in [
            Path(__file__), Path(A.__file__), Path(owner.__file__),
            ROOT/'src/bhsm/interface/current_incoming_formation_family.py',
            ROOT/'src/bhsm/interface/current_action_response_capture.py',
            ROOT/'src/bhsm/interface/ball_factored_arb_integrand.py',
            ROOT/'src/bhsm/interface/factored_arb_integrand.py',
            ROOT/'src/bhsm/interface/sparse_arb_mixed_jets.py',
            ROOT/'src/bhsm/interface/physical_hs_value.py',
            ROOT/'src/bhsm/interface/indexed_eigenpair_proposal.py',
            ROOT/'scripts/recenter_n12_gate7_current_history_box.py',
            CANDIDATE, CANDIDATE.with_name('report.json'),
            FRAME/'arrays.npz', FRAME/'report.json', POINT/'arrays.npz', POINT/'report.json',
            LOCAL/'arrays.npz', LOCAL/'report.json',
            BASE/'formation_op_current_20260928/dependencies.json',
        ]}, arrays_SHA256=digest(out/'arrays.npz'))
    (out/'report.json').write_bytes(encoded(report))
    print(json.dumps(dict(status=report['status'],
        replays={k: bound(v)['approximate_upper'] for k, v in replays.items()},
        descriptor=float(s.mid()), lookback_proper_clock=float(clock.mid()),
        formal_duration_coefficient=float(a.mid())), indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    calculate(parser.parse_args().out)
