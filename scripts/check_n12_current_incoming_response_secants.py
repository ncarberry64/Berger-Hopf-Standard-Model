"""Independent current-state secants for the local implicit response only."""
import argparse
from pathlib import Path
import numpy as np
from flint import arb, arb_mat, ctx
import build_n12_current_incoming_response as build
from bhsm.interface.current_action_response_capture import evaluate_shared_rate
from bhsm.interface.current_incoming_formation_family import coefficient_first, zero_descriptor_clock_germ


def sample(state, weights, reference):
    A = build.owner.action
    checks = []
    original = A._eigenline
    def proposal(hessian, midpoint, ref):
        return build.indexed_proposal(hessian[37:, 37:], 23, ref)
    A._eigenline = build.recentered_eigenline(proposal)
    try:
        with build.owner.sparse.use_optimized_mixed(A), build.owner.factored.use_ball_factored_integrand(A, state):
            with build.verified_eigenline(A, checks, expected_index=23, normalize_proposal_center=True):
                _, internal = evaluate_shared_rate(A, state, arb(0), weights, reference, None)
    finally:
        A._eigenline = original
    values, _ = coefficient_first(state, arb_mat(98, 1))
    a, _ = zero_descriptor_clock_germ(lapse=values['lapse'], log_lapse_first=arb_mat(1, 1),
        cpsi=internal['cpsi'], bpsi=internal['bpsi'], cpsi_first=arb_mat(1, 1), bpsi_first=arb_mat(1, 1))
    return dict(local_internal=arb_mat(124, 1,
                    list(internal['psi'])+[internal['eigenvalue']]+list(internal['hard'])+[internal['bpsi']]),
                duration_coefficient=arb_mat([[a]]),
                radius_history_coefficient=arb_mat([[a*values['proper_log_radius_rate']]])), checks[0]


def calculate(packet, out):
    ctx.prec = 512
    packet, out = packet.resolve(), out.resolve()
    if out.exists():
        raise ValueError('new secant output directory required')
    names = ['local_internal_internal_first', 'formal_zero_descriptor_duration_coefficient_first_66',
             'formal_radius_history_coefficient_first_66']
    first = build.verified_packet(packet, names)
    Q = build.verified_packet(build.FRAME, ['Q66_current_raw'])['Q66_current_raw']
    with np.load(build.CANDIDATE) as z:
        state = np.array([arb(float(v)) for v in z['joint_state_raw'][98:196]], dtype=object)
        weights, reference = z['state_weights'].copy(), z['branch_reference'].copy()
    selected = int(np.argmax([float(abs(v).mid()) for v in first[names[1]].entries()]))
    direction = np.array([Q[i, selected] for i in range(98)], dtype=object)
    targets = {key: arb_mat(value.nrows(), 1, [value[i, selected] for i in range(value.nrows())])
               for key, value in zip(('local_internal', 'duration_coefficient', 'radius_history_coefficient'), first.values())}
    arrays, records = {}, []
    for exponent in (24, 25):
        step = arb(2)**-exponent
        print('Current incoming secant, Q column', selected, 'step 2^-'+str(exponent), flush=True)
        plus, check_plus = sample(state+step*direction, weights, reference)
        minus, check_minus = sample(state-step*direction, weights, reference)
        errors = {}
        for key in targets:
            secant = (plus[key]-minus[key])/(2*step)
            error = secant-targets[key]
            arrays[f'{key}_secant_{exponent}'] = secant
            arrays[f'{key}_error_{exponent}'] = error
            scale = build.bound(targets[key])['approximate_upper']
            errors[key] = dict(absolute=build.bound(error), relative_upper=build.bound(error)['approximate_upper']/scale)
        records.append(dict(step='1/'+str(2**exponent), errors=errors,
                            positive_sample_eigenpair=check_plus, negative_sample_eigenpair=check_minus))
    for key in targets:
        earlier = records[0]['errors'][key]['relative_upper']
        later = records[1]['errors'][key]['relative_upper']
        if not (later < 1e-7 and later < .3*earlier):
            raise ArithmeticError('local first response failed secant convergence: '+key)
    out.mkdir(parents=True)
    build.save_arrays(out/'arrays.npz', arrays)
    report = dict(status='CURRENT_LOCAL_INTERNAL_AND_CLOCK_GERM_SECANTS_CHECKED',
        scope='Numerical directional checks, not a neighborhood or history certificate',
        selected_Q66_column_zero_based=selected, records=records,
        physical_reduced_action_checked=False,
        arrays_SHA256=build.digest(out/'arrays.npz'),
        source_SHA256={p.relative_to(build.ROOT).as_posix(): build.digest(p) for p in (
            Path(__file__), Path(build.__file__), packet/'arrays.npz', packet/'report.json',
            build.FRAME/'arrays.npz', build.CANDIDATE,
            build.ROOT/'src/bhsm/interface/current_action_response_capture.py',
            build.ROOT/'src/bhsm/interface/current_incoming_formation_family.py',
            Path(build.owner.action.__file__),
        )})
    (out/'report.json').write_bytes(build.encoded(report))
    print({key: [r['errors'][key]['relative_upper'] for r in records] for key in targets}, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--packet', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    calculate(args.packet, args.out)
