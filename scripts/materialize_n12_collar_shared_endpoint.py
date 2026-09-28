"""Integrate the certified common rate model into a shared endpoint enclosure.

Time averages of the curve box and normal Euclidean ball remain in those
same convex groups. They are proof remainder parameters, not physical inputs.
"""
from reduce_n12_collar_flow_descriptor import (
    ROOT, JET, CANDIDATE, BASE, owner, packet, restore, digest, encoded,
    save_arrays, scalar, arb, arb_mat, ctx, np, Path, argparse, json,
    normal_center,
)
from bhsm.interface.shared_action_taylor import TaylorDomain, Taylor
from bhsm.interface.shared_parameter_residual import linear_support


def calculate(out):
    ctx.prec = 512
    if out.exists():
        raise ValueError('new output directory required')
    folders = dict(flow=BASE/'flow55_composed1', lift=BASE/'flow55_curve_normal1',
                   step=BASE/'flow55_partial1', jet=JET)
    records, packs = {}, {}
    for key, path in folders.items():
        records[key], packs[key] = packet(path)
        for source, expected in records[key]['source_SHA256'].items():
            if digest(ROOT/source) != expected:
                raise ValueError('source changed: '+source)
    flow, lift, step, jet = [packs[k] for k in ('flow', 'lift', 'step', 'jet')]
    if not records['step']['actual_flow_tube_included']:
        raise ArithmeticError('a first-exit certificate is required')
    T = restore(step, 'step')[0, 0]
    h = restore(lift, 'step')[0, 0]
    U, Dn, J0 = [restore(jet, k) for k in ('fixed_s_direction', 'local_internal_first', 'local_internal_jacobian')]
    s0 = restore(jet, 'current_descriptor')[0, 0]
    center = normal_center(J0, s0)
    with np.load(CANDIDATE) as z:
        state = [arb(float(v)) for v in z['joint_state_raw'][:98]]
        weights = [arb(float(v)) for v in z['state_weights']]
    rho = restore(lift, 'curve_action_radii').entries()
    nr = restore(lift, 'old_normal_radii').entries()
    response = restore(lift, 'curve_normal_response_scaled')
    posterior = restore(lift, 'new_normal_posterior')[0, 0].upper()
    domain = TaylorDomain([(0, 1, 'interval'), (1, 99, 'box'), (99, 223, 'euclidean')], 223)
    y, n = [], []
    for i, v in enumerate(state):
        a = [arb(0)]*223
        a[0], a[1+i] = U[i, 0]*h/weights[i], rho[i]/weights[i]
        y.append(domain.affine(v, a))
    for i, v in enumerate(center):
        a = [Dn[i, 0]*h]+[nr[i]*response[i, j] for j in range(98)]+[arb(0)]*124
        a[99+i] = posterior*nr[i]
        n.append(domain.affine(v, a))
    s = domain.affine(s0, [h]+[arb(0)]*222)
    saved = restore(flow, 'descriptor_model')
    delta = Taylor(domain, saved[0, 0], arb_mat(1, 223, [saved[0, j] for j in range(1, 224)]), saved[0, 224].upper())
    qw, rw, _, _ = owner.action.metric_data()
    qw, rw = [[arb(float(v)) for v in a] for a in (qw, rw)]
    G = [s*qw[i]*y[37+i] for i in range(37)]
    G += [rw[i]*(n[123]*n[i]+s*n[62+i]) for i in range(61)]
    rates = [v/delta for v in G]
    corrected = [int(float(v)) for v in restore(flow, 'numerator_output_components').entries()]
    c, a, r = [restore(flow, k) for k in ('numerator_rate_constant', 'numerator_rate_linear', 'numerator_rate_remainder')]
    for j, i in enumerate(corrected):
        rates[i] = Taylor(domain, c[0, j]*rho[i],
            arb_mat(1, 223, [a[k, j]*rho[i] for k in range(223)]), (r[0, 0]*rho[i]).upper())
    constant = arb_mat(99, 1)
    affine = arb_mat(99, 222)
    remainder = arb_mat(99, 1)
    replay = arb_mat(98, 1)
    curvature = restore(jet, 'fixed_s_curve_second')
    for i, v in enumerate(rates):
        constant[i, 0] = state[i]*weights[i]+T*v.c+T*T*v.a[0, 0]/(2*h)
        for j in range(222):
            affine[i, j] = T*v.a[0, j+1]
        remainder[i, 0] = (T*v.r).upper()
        replay[i, 0] = v.a[0, 0]/h-curvature[i, 0]
    constant[98, 0] = s0+T
    if not all(v.contains(0) for v in replay.entries()):
        raise ArithmeticError('transported first rate coefficient differs from the frozen curve jet')
    groups = [(0, 98, 'box'), (98, 222, 'euclidean')]
    enclosure = arb_mat(99, 1, [constant[i, 0]+arb(0,
        (linear_support([affine[i, j] for j in range(222)], groups)+remainder[i, 0]).upper()) for i in range(99)])
    out.mkdir(parents=True)
    save_arrays(out/'arrays.npz', dict(endpoint_constant=constant, endpoint_affine=affine,
        endpoint_remainder=remainder, endpoint_enclosure=enclosure,
        rate_first_coefficient_replay=replay, step=arb_mat([[T]])))
    files = [Path(__file__), CANDIDATE, ROOT/'src/bhsm/interface/shared_action_taylor.py',
             ROOT/'src/bhsm/interface/shared_parameter_residual.py']
    for folder in folders.values():
        files.extend([folder/'arrays.npz', folder/'report.json'])
    report = dict(status='CURRENT_COLLAR_SHARED_ENDPOINT_ENCLOSED',
        actual_flow_endpoint_enclosed=True, groups=groups,
        parameter_identity='0:98 time-averaged curve-box parameters; 98:222 time-averaged normal Euclidean parameters',
        physical_input_count_added=0, proof_remainder_parameter_count=222,
        signed_rate_integrated_before_support=True, constant_includes_known_theta_integral=True,
        independent_rate_tail_per_state_coordinate=True,
        first_rate_coefficient_replays_frozen_curve_jet=True,
        first_variation_transported=False, prefix_overlap_certified=False,
        positive_operator_history_certified=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False,
        source_SHA256={p.relative_to(ROOT).as_posix(): digest(p) for p in files},
        arrays_SHA256=digest(out/'arrays.npz'))
    (out/'report.json').write_bytes(encoded(report))
    for p in packs.values():
        p.close()
    print(report['status'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    calculate(parser.parse_args().out)
