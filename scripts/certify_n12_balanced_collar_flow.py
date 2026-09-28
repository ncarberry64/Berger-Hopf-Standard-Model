"""First-exit test on the certified coupled curve/normal chart.

Reuses the frozen descriptor adjoint; the numerator adjoint is algebraic.
No scientific producer or prefix cell is regenerated.
"""
from reduce_n12_collar_flow_descriptor import (
    ROOT, JET, CANDIDATE, BASE, owner, packet, restore, normal_center, digest,
    encoded, save_arrays, scalar, arb, arb_mat, ctx, np, Path, argparse,
    normal_contraction, delta_and_G, integral_bound,
)
from bhsm.interface.shared_action_taylor import TaylorDomain, Taylor, scalar_taylor_action
from bhsm.interface.input_linear_taylor import InputLinearTaylor
from bhsm.interface.local_state_input_taylor_action import input_linear_taylor_action


def numerator_adjoint(center, s0, rw, J0, components, rho):
    derivative = arb_mat(len(components), 124)
    for row, i in enumerate(components):
        k = i-37
        if k >= 0:
            derivative[row, k] = rw[k]*center[123]/rho[i]
            derivative[row, 62+k] = rw[k]*s0/rho[i]
            derivative[row, 123] = rw[k]*center[k]/rho[i]
    solved = J0.transpose().solve(derivative.transpose()).transpose()
    beta = arb_mat(solved.nrows(), 124, [v.mid() for v in solved.entries()])
    return beta, derivative-beta*J0


def calculate(out, normal):
    ctx.prec = 512
    if out.exists():
        raise ValueError('new output directory required')
    paths = dict(normal=normal, descriptor=BASE/'flow55_descriptor1', jet=JET)
    records, packs = {}, {}
    for key, path in paths.items():
        records[key], packs[key] = packet(path)
        for source, expected in records[key]['source_SHA256'].items():
            if digest(ROOT/source) != expected:
                raise ValueError('frozen source changed: '+source)
    cert, descriptor, jet = [packs[k] for k in ('normal', 'descriptor', 'jet')]
    if not records['normal']['normal_graph_certified'] or not sum(restore(cert, 'YZ').entries(), arb(0))<1:
        raise ArithmeticError('uniform normal graph certificate required')
    with np.load(CANDIDATE) as z:
        state = [arb(float(v)) for v in z['joint_state_raw'][:98]]
        weights = [arb(float(v)) for v in z['state_weights']]
    U, Dn, J0 = [restore(jet, k) for k in ('fixed_s_direction', 'local_internal_first', 'local_internal_jacobian')]
    s0 = restore(jet, 'current_descriptor')[0, 0]
    center = normal_center(J0, s0)
    h = restore(cert, 'step')[0, 0]
    rho, nr = [restore(cert, k).entries() for k in ('curve_action_radii', 'normal_radii')]
    response = restore(cert, 'curve_normal_response')
    posterior = restore(cert, 'posterior')[0, 0].upper()
    domain = TaylorDomain([(0, 1, 'interval'), (1, 99, 'box'), (99, 223, 'euclidean')], 223)
    y, n = [], []
    for i, v in enumerate(state):
        a = [arb(0)]*223
        a[0], a[1+i] = U[i, 0]*h/weights[i], rho[i]/weights[i]
        y.append(domain.affine(v, a))
    for i, v in enumerate(center):
        a = [Dn[i, 0]*h]+[response[i, j] for j in range(98)]+[arb(0)]*124
        a[99+i] = posterior*nr[i]
        n.append(domain.affine(v, a))
    s = domain.affine(s0, [h]+[arb(0)]*222)
    A = owner.action
    maps = [A._dense_mapping(A._integrand(state, i, 0).maps) for i in range(A.POINTS)]
    bd = restore(descriptor, 'descriptor_adjoint').entries()
    with scalar_taylor_action(A):
        delta, G = delta_and_G(A, y, n, s, weights, maps)
        delta -= normal_contraction(A, y, n, weights, bd, maps)
    print('Balanced descriptor positive:', bool(delta.enclosure()>0), flush=True)
    encode = lambda v: [v.c]+v.a.entries()+[v.r]
    arrays = dict(descriptor_model=arb_mat([encode(delta)]), chart_step=arb_mat([[h]]))
    report = dict(status='BALANCED_CURVE_DESCRIPTOR_NOT_POSITIVE', descriptor_positive=bool(delta.enclosure()>0),
        descriptor_enclosure=scalar(delta.enclosure()), actual_flow_tube_included=False,
        first_variation_transported=False, prefix_overlap_certified=False,
        positive_operator_history_certified=False, prefix_cells_rebuilt=0,
        Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    if delta.enclosure()>0:
        rates = [v/delta for v in G]
        ratios = [(integral_bound(v-U[i, 0], h)/rho[i]).upper() for i, v in enumerate(rates)]
        failed = [i for i in range(37, 98) if not ratios[i]<1]
        rw = [arb(float(v)) for v in A.metric_data()[1]]
        print('Balanced numerator components requiring composition:', len(failed), flush=True)
        beta, replay = numerator_adjoint(center, s0, rw, J0, failed, rho) if failed else (arb_mat(0, 124), arb_mat(0, 124))
        # Groups of at most eight prevent a whole-output Euclidean tail from
        # unnecessarily widening every coordinate. All terms within each
        # contraction retain the same state/normal parameter identities.
        for start in range(0, len(failed), 8):
            selected = failed[start:start+8]
            count = len(selected)
            covectors = [InputLinearTaylor(domain, arb_mat(1, count,
                [beta[start+i, j] for i in range(count)]), arb_mat(223, count)) for j in range(124)]
            units = [InputLinearTaylor(domain, arb_mat(1, count,
                [arb(i == j) for j in range(count)]), arb_mat(223, count)) for i in range(count)]
            with input_linear_taylor_action(A):
                residual = normal_contraction(A, y, n, weights, covectors, maps)
            reduced = (sum((u*G[i]/rho[i] for u, i in zip(units, selected, strict=True)), 0)-residual)/delta
            for j, i in enumerate(selected):
                rates[i] = Taylor(domain, reduced.c[0, j]*rho[i],
                    arb_mat(1, 223, [reduced.a[k, j]*rho[i] for k in range(223)]), reduced.r*rho[i])
                ratios[i] = (integral_bound(rates[i]-U[i, 0], h)/rho[i]).upper()
            print('Reduced numerator group:', start+count, '/', len(failed), flush=True)
        f = arb(1)
        while not all(f*v<1 for v in ratios):
            f /= 2
        T = f*h
        arrays.update(rate_models=arb_mat([encode(v) for v in rates]),
            full_chart_first_exit_ratios=arb_mat(98, 1, ratios),
            first_exit_ratios=arb_mat(98, 1, [f*v for v in ratios]),
            step=arb_mat([[T]]), fraction=arb_mat([[f]]),
            numerator_adjoint=beta, numerator_adjoint_replay=replay,
            numerator_components=arb_mat(len(failed), 1, [arb(i) for i in failed]),
            curve_action_radii=arb_mat(98, 1, rho),
            endpoint_action=arb_mat(99, 1,
                [state[i]*weights[i]+T*U[i, 0]+arb(0, (rho[i]*f*ratios[i]).upper()) for i in range(98)]+[s0+T]))
        report.update(status='BALANCED_COLLAR_FLOW_SEGMENT_ENCLOSED', actual_flow_tube_included=True,
            chart_step=scalar(h), step=scalar(T), exact_time_fraction=scalar(f),
            full_chart_maximum_first_exit_ratio=scalar(max(ratios)),
            maximum_first_exit_ratio=scalar(max(f*v for v in ratios)),
            physical_radii_changed=False, normal_graph_recomputed=False)
        print(report['status'], 'step=', float(T), 'fraction=', float(f), 'full ratio=', float(max(ratios)), flush=True)
    out.mkdir(parents=True)
    save_arrays(out/'arrays.npz', arrays)
    files = [Path(__file__), CANDIDATE, Path(A.__file__), ROOT/'scripts/reduce_n12_collar_flow_descriptor.py',
        *[ROOT/('src/bhsm/interface/'+name+'.py') for name in (
            'shared_action_taylor', 'input_linear_taylor', 'local_input_taylor_action_fast', 'local_state_input_taylor_action')]]
    for path in paths.values():
        files.extend([path/'arrays.npz', path/'report.json'])
    report.update(source_SHA256={p.relative_to(ROOT).as_posix(): digest(p) for p in files},
                  arrays_SHA256=digest(out/'arrays.npz'))
    (out/'report.json').write_bytes(encoded(report))
    for p in packs.values():
        p.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--normal', type=Path, default=BASE/'balanced45_normal1')
    args = parser.parse_args()
    calculate(args.out, args.normal)
