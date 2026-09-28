"""One action-sufficient outgoing collar at the current reset trial state.

The event descriptor coordinate is zero, while the selected eigenvalue
defect is retained as an explicit unsolved KKT residual. This is a coupled
trial realization, not a certified physical event or the old C2 prefix.
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
from build_n12_current_incoming_response import CANDIDATE, POINT
from evaluate_n12_gate7_current_contractions import packet, CORE, SHARED, scalar, BASE
from checkpoint_n12_gate7_66d_tangent_binding import restore, bound, digest, encoded
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from recenter_n12_gate7_current_history_box import recentered_eigenline
from bhsm.interface.indexed_eigenpair_proposal import indexed_proposal
from bhsm.interface.physical_hs_value import verified_eigenline
from bhsm.interface.current_action_response_capture import evaluate_shared_rate
from bhsm.interface.current_incoming_formation_family import coefficient_first


def calculate(out):
    ctx.prec = 512
    if out.exists(): raise ValueError('new output directory required')
    cand = json.loads(CANDIDATE.with_name('report.json').read_bytes())
    if digest(CANDIDATE) != cand['candidate_SHA256']:
        raise ValueError('current reset candidate changed')
    pr, p = packet(POINT); cr, c = packet(CORE); sr, incoming = packet(SHARED)
    key = CANDIDATE.relative_to(ROOT).as_posix()
    for packet_report in (pr, sr):
        sources = {k.replace('\\', '/'): v for k, v in packet_report['source_SHA256'].items()}
        if sources.get(key) != digest(CANDIDATE):
            raise ValueError('selected-line and incoming packets use another reset candidate')
    with np.load(CANDIDATE) as z:
        raw = np.array([arb(float(v)) for v in z['joint_state_raw'][:98]], dtype=object)
        weights = z['state_weights'].copy(); ref = z['branch_reference'].copy()
    old_x = restore(c, 'log_radius')[0, 0]
    point_values, _ = coefficient_first(raw, arb_mat(98, 1))
    old_difference = old_x-point_values['log_radius']
    incoming_difference = point_values['log_radius']-restore(incoming, 'log_radius_value')[0, 0]
    # Numerical proof collar only. Its endpoint is NOT a physical stop.
    radius = arb(2)**-72; descriptor_upper = arb(2)**-100; horizon = arb(2)**-76
    box = np.array([v+arb(0, radius/arb(float(weights[i]))) for i, v in enumerate(raw)], dtype=object)
    sbox = descriptor_upper/2+arb(0, descriptor_upper/2)
    checks = []; A = owner.action; original = A._eigenline
    def proposal(hessian, midpoint, reference):
        return indexed_proposal(hessian[37:, 37:], 24, reference)
    A._eigenline = recentered_eigenline(proposal)
    print('Evaluating one NEW current-reset trial collar; no history/Jacobi campaign', flush=True)
    try:
        with owner.sparse.use_optimized_mixed(A), owner.factored.use_ball_factored_integrand(A, box):
            with verified_eigenline(A, checks, expected_index=24, normalize_proposal_center=True):
                rate, internal = evaluate_shared_rate(A, box, sbox, weights, ref, None)
    finally:
        A._eigenline = original
    values, _ = coefficient_first(box, arb_mat(98, 1))
    speed = rate.value[98]
    norm = internal['norm_G']
    if not speed > 0 or not norm > 0:
        raise ArithmeticError('positive outgoing descriptor speed and arc norm required')
    state_excursions = [horizon*abs(rate.value[i]).upper()/radius for i in range(98)]
    descriptor_excursion = horizon*speed.upper()/descriptor_upper
    if not all(v < 1 for v in state_excursions) or not descriptor_excursion < 1:
        raise ArithmeticError('new trial collar leaves its evaluated domain')
    # s(0)=0, s'(r) in speed; proper q=N*s/||G||.
    # Exact integration of the resulting linear-in-r lower/upper bounds.
    duration = (values['lapse']/norm)*speed*horizon**2/2
    if not duration > 0:
        raise ArithmeticError('strictly positive trial proper duration required')
    eigen_defect = restore(p, 'C2_eigenvalue')[0, 0]
    arrays = dict(current_outgoing_raw_state=arb_mat(98, 1, list(raw)),
        raw_state_domain=arb_mat(98, 1, list(box)),
        independent_descriptor_domain=arb_mat([[sbox]]),
        independent_event_descriptor=arb_mat([[0]]),
        selected_event_descriptor_defect=arb_mat([[eigen_defect]]),
        augmented_field_domain=arb_mat(99, 1, list(rate.value)),
        local_eigenvalue_domain=arb_mat([[internal['eigenvalue']]]),
        arc_norm_domain=arb_mat([[norm]]), arc_horizon=arb_mat([[horizon]]),
        proper_duration=arb_mat([[duration]]),
        old_prefix_radius_minus_current=arb_mat([[old_difference]]),
        reset_radius_matching_residual=arb_mat([[incoming_difference]]))
    arrays.update({k+'_domain': arb_mat([[v]]) for k, v in values.items()})
    sources = [Path(__file__), CANDIDATE, CANDIDATE.with_name('report.json'),
        Path(owner.action.__file__), ROOT/'src/bhsm/interface/current_action_response_capture.py',
        ROOT/'src/bhsm/interface/current_incoming_formation_family.py',
        ROOT/'scripts/recenter_n12_gate7_current_history_box.py',
        ROOT/'theory/n12_joint_trial_operator_collar.md']
    for folder in (POINT, CORE, SHARED): sources.extend([folder/'arrays.npz', folder/'report.json'])
    out.mkdir(parents=True)
    save_arrays(out/'arrays.npz', arrays)
    report = dict(status='CURRENT_RESET_COUPLED_TRIAL_C2_COLLAR_ENCLOSED',
        base_commit='964b6a67190628774aa01bed85ccf1686d304edf',
        scope='Off-root coupled trial operator collar; not a physical event/history certificate',
        branch_index=24, independent_event_descriptor=0,
        selected_event_descriptor_defect=scalar(eigen_defect),
        defect_not_zeroed=True, event_root_solved=False,
        old_prefix_log_radius_mismatch=scalar(old_difference),
        current_reset_radius_matching_residual=scalar(incoming_difference),
        physical_amplitude_selected=False, physical_stop_added=False,
        proof_collar_arc_horizon=scalar(horizon), proper_duration=scalar(duration),
        descriptor_speed=scalar(speed), arc_norm=scalar(norm),
        point_coefficients={k: scalar(v) for k, v in point_values.items()},
        coefficient_domain={k: scalar(v) for k, v in values.items()},
        domain_inclusion=dict(state_excursion_upper=max(float(v.upper()) for v in state_excursions),
            descriptor_excursion_upper=float(descriptor_excursion.upper()),
            method='First-exit bound for the enclosed analytic normalized branch field; simple eigenline and nonzero border/norm give local uniqueness'),
        duration_identity='s(0)=0, s(r) in r*speed; T=int_0^h N*s/||G|| dr in (N/||G||)*speed*h^2/2',
        fiber_identity='d(lambda_selected-s)/dr=0 for the retained augmented field; initial nonzero defect stays in the KKT residual',
        eigenpair_proof=checks[0], new_box_evaluations=1,
        new_Jacobi_columns=0, new_history_mesh_cells=0, frozen_objects_recomputed=False,
        full_graded_heat_force=None, q66=None, Gate7_closed=False, FULL_BHSM_COMPLETE=False,
        source_SHA256={path.relative_to(ROOT).as_posix(): digest(path) for path in sources},
        arrays_SHA256=digest(out/'arrays.npz'))
    (out/'report.json').write_bytes(encoded(report))
    for obj in (p, c, incoming): obj.close()
    print(json.dumps({k: report[k] for k in ('status', 'proper_duration', 'descriptor_speed', 'domain_inclusion')}, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--out', type=Path, required=True)
    calculate(parser.parse_args().out)
