"""First-exit test after composing the curve remainder with its normal graph."""
from reduce_n12_collar_flow_descriptor import (
    ROOT, JET, CANDIDATE, BASE, owner, packet, restore, normal_center, digest,
    encoded, save_arrays, scalar, arb, arb_mat, ctx, np, Path, argparse, json,
    normal_contraction, delta_and_G, integral_bound,
)
from bhsm.interface.shared_action_taylor import TaylorDomain, Taylor, scalar_taylor_action
from bhsm.interface.input_linear_taylor import InputLinearTaylor
from bhsm.interface.local_state_input_taylor_action import input_linear_taylor_action


def calculate(lift_path, out):
    ctx.prec = 512
    if out.exists():
        raise ValueError('new output directory required')
    paths = dict(lift=lift_path, descriptor=BASE/'flow55_descriptor1', numerator=BASE/'flow55_numerator1', jet=JET)
    records, packs = {}, {}
    for key, path in paths.items():
        records[key], packs[key] = packet(path)
        for source, expected in records[key]['source_SHA256'].items():
            if digest(ROOT/source) != expected:
                raise ValueError('current source changed: '+source)
    lift, descriptor, numerator, jet = [packs[k] for k in ('lift', 'descriptor', 'numerator', 'jet')]
    if not records['lift']['old_normal_ball_contains_new_predictor']:
        raise ArithmeticError('new predictor is outside the certified old graph domain')
    if not sum(restore(lift, 'old_normal_YZ').entries(), arb(0))<1:
        raise ArithmeticError('old uniform normal inclusion failed')
    with np.load(CANDIDATE) as z:
        state = [arb(float(v)) for v in z['joint_state_raw'][:98]]
        weights = [arb(float(v)) for v in z['state_weights']]
    U, Dn, J0 = [restore(jet, k) for k in ('fixed_s_direction', 'local_internal_first', 'local_internal_jacobian')]
    s0 = restore(jet, 'current_descriptor')[0, 0]
    center = normal_center(J0, s0)
    h = restore(lift, 'step')[0, 0]
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
    A = owner.action
    maps = [A._dense_mapping(A._integrand(state, i, 0).maps) for i in range(A.POINTS)]
    bd = restore(descriptor, 'descriptor_adjoint').entries()
    with scalar_taylor_action(A):
        delta, G = delta_and_G(A, y, n, s, weights, maps)
        delta -= normal_contraction(A, y, n, weights, bd, maps)
    print('Composed curve descriptor positive:', bool(delta.enclosure()>0), flush=True)
    encode = lambda v: arb_mat(1, 225, [v.c]+v.a.entries()+[v.r])
    arrays = dict(descriptor_model=encode(delta))
    report = dict(status='COMPOSED_CURVE_FLOW_OUTPUT', descriptor_positive=bool(delta.enclosure()>0),
        descriptor_enclosure=scalar(delta.enclosure()), source_normal_graph_reused=True,
        actual_flow_tube_included=False, first_variation_transported=False,
        prefix_overlap_certified=False, positive_operator_history_certified=False,
        prefix_cells_rebuilt=0, Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    if delta.enclosure()>0:
        defects = [G[i]/delta-U[i, 0] for i in range(98)]
        ratios = [(integral_bound(v, h)/rho[i]).upper() for i, v in enumerate(defects)]
        previous_components = [int(float(v)) for v in restore(numerator, 'components').entries()]
        failed = [i for i in previous_components if not ratios[i]<1]
        print('Numerator components still requiring residual composition:', len(failed), flush=True)
        if failed:
            matrix = restore(numerator, 'numerator_adjoint')
            rows = [previous_components.index(i) for i in failed]
            count = len(rows)
            beta = [InputLinearTaylor(domain, arb_mat(1, count, [matrix[row, j] for row in rows]),
                                      arb_mat(223, count)) for j in range(124)]
            units = [InputLinearTaylor(domain, arb_mat(1, count, [arb(i == j) for j in range(count)]),
                                       arb_mat(223, count)) for i in range(count)]
            with input_linear_taylor_action(A):
                normal = normal_contraction(A, y, n, weights, beta, maps)
            value = sum((u*G[i]/rho[i] for u, i in zip(units, failed, strict=True)), 0)
            reduced = (value-normal)/delta
            for j, i in enumerate(failed):
                model = Taylor(domain, reduced.c[0, j]-U[i, 0]/rho[i],
                    arb_mat(1, 223, [reduced.a[k, j] for k in range(223)]), reduced.r)
                ratios[i] = integral_bound(model, h)
            arrays.update(numerator_output_components=arb_mat(count, 1, [arb(i) for i in failed]),
                numerator_rate_constant=reduced.c, numerator_rate_linear=reduced.a,
                numerator_rate_remainder=arb_mat([[reduced.r]]))
        arrays['flow_first_exit_ratios'] = arb_mat(98, 1, ratios)
        passed = all(v<1 for v in ratios)
        report.update(status='FIRST_COLLAR_FLOW_SEGMENT_ENCLOSED' if passed else 'COMPOSED_CURVE_FIRST_EXIT_FAILED',
            actual_flow_tube_included=passed, maximum_first_exit_ratio=scalar(max(ratios)),
            first_failing_coordinate=next((i for i, v in enumerate(ratios) if not v<1), None))
        if passed:
            arrays['endpoint_action'] = arb_mat(99, 1,
                [state[i]*weights[i]+h*U[i, 0]+arb(0, (rho[i]*ratios[i]).upper()) for i in range(98)]+[s0+h])
        print(report['status'], float(max(ratios)), flush=True)
    out.mkdir(parents=True)
    save_arrays(out/'arrays.npz', arrays)
    files = [Path(__file__), ROOT/'scripts/reduce_n12_collar_flow_descriptor.py', CANDIDATE, Path(A.__file__),
             *[ROOT/('src/bhsm/interface/'+name+'.py') for name in (
                 'shared_action_taylor', 'shared_parameter_residual', 'input_linear_taylor',
                 'local_input_taylor_action_fast', 'local_state_input_taylor_action')]]
    for path in paths.values():
        files.extend([path/'arrays.npz', path/'report.json'])
    report['source_SHA256'] = {p.relative_to(ROOT).as_posix(): digest(p) for p in files}
    report['arrays_SHA256'] = digest(out/'arrays.npz')
    (out/'report.json').write_bytes(encoded(report))
    for p in packs.values():
        p.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--lift', type=Path, default=BASE/'flow55_curve_normal1')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    calculate(args.lift, args.out)
