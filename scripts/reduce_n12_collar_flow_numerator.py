"""Shared physical numerator minus its full normal-residual contraction."""
from reduce_n12_collar_flow_descriptor import (
    ROOT, JET, CANDIDATE, BASE, owner, packet, restore, normal_center, digest,
    encoded, save_arrays, scalar, arb, arb_mat, ctx, np, Path, argparse, json,
    ScalarJet, TaylorDomain, normal_contraction, integral_bound,
)
from bhsm.interface.shared_action_taylor import Taylor
from bhsm.interface.input_linear_taylor import InputLinearTaylor, vector_norm
from bhsm.interface.local_state_input_taylor_action import input_linear_taylor_action


def calculate(source, out):
    ctx.prec = 512
    if out.exists():
        raise ValueError('new output directory required')
    dr, dpack = packet(source)
    for path, expected in dr['source_SHA256'].items():
        if digest(ROOT/path) != expected:
            raise ValueError('descriptor source changed: '+path)
    tube_path = next(ROOT/p for p in dr['source_SHA256'] if p.endswith('/arrays.npz') and '/flow55_box1/' in p)
    tr, tube = packet(tube_path.parent)
    jr, jet = packet(JET)
    with np.load(CANDIDATE) as z:
        state = [arb(float(v)) for v in z['joint_state_raw'][:98]]
        weights = [arb(float(v)) for v in z['state_weights']]
    U, Dn, J0 = [restore(jet, k) for k in ('fixed_s_direction', 'local_internal_first', 'local_internal_jacobian')]
    s0 = restore(jet, 'current_descriptor')[0, 0]
    center = normal_center(J0, s0)
    h = restore(tube, 'step')[0, 0]
    rho = restore(tube, 'curve_action_radii').entries()
    posterior = restore(dpack, 'normal_posterior')[0, 0]
    factor = tr['normal_refinement'][-1]['factor']
    nr = [factor*r for r in restore(tube, 'normal_radii').entries()]
    if not sum(restore(dpack, 'normal_certificate_YZ').entries(), arb(0)) < 1:
        raise ArithmeticError('source normal inclusion failed')
    prior_ratios = restore(dpack, 'flow_first_exit_ratios')
    components = [i for i in range(98) if not prior_ratios[i, 0] < 1]
    if not components or any(i<37 for i in components):
        raise ValueError('this continuation expects the failed velocity/material outputs')
    domain = TaylorDomain([(0, 1, 'interval'), (1, 99, 'box'), (99, 223, 'euclidean')], 223)
    y, n = [], []
    for i, v in enumerate(state):
        a = [arb(0)]*223
        a[0], a[1+i] = U[i, 0]*h/weights[i], rho[i]/weights[i]
        y.append(domain.affine(v, a))
    for i, v in enumerate(center):
        a = [arb(0)]*223
        a[0], a[99+i] = Dn[i, 0]*h, posterior*nr[i]
        n.append(domain.affine(v, a))
    s = domain.affine(s0, [h]+[arb(0)]*222)
    dv = restore(dpack, 'reduced_descriptor_numerator')
    delta = Taylor(domain, dv[0, 0], arb_mat(1, 223, [dv[0, j] for j in range(1, 224)]), dv[0, 224].upper())
    if not delta.enclosure()>0:
        raise ArithmeticError('source descriptor numerator is not positive')
    A = owner.action
    _, rw, _, _ = A.metric_data()
    rw = [arb(float(v)) for v in rw]
    nn = [ScalarJet(v, arb_mat(1, 124, [arb(i == j) for j in range(124)])) for i, v in enumerate(center)]
    anchor = [rw[i-37]*(nn[123]*nn[i-37]+s0*nn[62+i-37])/rho[i] for i in components]
    gradient = arb_mat(len(components), 124, [v for row in anchor for v in row.a.entries()])
    solved = J0.transpose().solve(gradient.transpose()).transpose()
    beta = arb_mat(solved.nrows(), solved.ncols(), [v.mid() for v in solved.entries()])
    adjoint_defect = gradient-beta*J0
    count = len(components)
    beta_leg = [InputLinearTaylor(domain, arb_mat(1, count, [beta[i, j] for i in range(count)]),
                  arb_mat(223, count)) for j in range(124)]
    unit = [InputLinearTaylor(domain, arb_mat(1, count, [arb(i == j) for j in range(count)]),
              arb_mat(223, count)) for i in range(count)]
    maps = [A._dense_mapping(A._integrand(state, i, 0).maps) for i in range(A.POINTS)]
    print('Composing', count, 'physical numerator residuals in one output space', flush=True)
    with input_linear_taylor_action(A):
        normal = normal_contraction(A, y, n, weights, beta_leg, maps)
    G = [rw[i-37]*(n[123]*n[i-37]+s*n[62+i-37])/rho[i] for i in components]
    value = sum((u*v for u, v in zip(unit, G, strict=True)), 0)
    reduced = value-normal
    output = reduced/delta
    const = InputLinearTaylor(domain, arb_mat(1, count, [U[i, 0]/rho[i] for i in components]), arb_mat(223, count))
    difference = output-const
    arrays = dict(components=np.array(components, dtype=np.int64),
        numerator_adjoint=beta, numerator_adjoint_defect=adjoint_defect,
        numerator_constant=reduced.c, numerator_linear=reduced.a,
        numerator_remainder=arb_mat([[reduced.r]]),
        rate_defect_constant=difference.c, rate_defect_linear=difference.a,
        rate_defect_remainder=arb_mat([[difference.r]]))
    # Restrict the common output model to each required coordinate. The
    # common Euclidean remainder bounds every such coordinate restriction.
    ratios = list(prior_ratios.entries())
    for j, i in enumerate(components):
        model = Taylor(domain, difference.c[0, j],
            arb_mat(1, 223, [difference.a[k, j] for k in range(223)]), difference.r)
        ratios[i] = integral_bound(model, h)
    arrays['flow_first_exit_ratios'] = arb_mat(98, 1, ratios)
    passed = all(v<1 for v in ratios)
    report = dict(status='FIRST_COLLAR_FLOW_SEGMENT_ENCLOSED' if passed else 'COMPOSED_COLLAR_FIRST_EXIT_FAILED',
        actual_flow_tube_included=passed, prefix_overlap_certified=False,
        corrected_components=components, maximum_first_exit_ratio=scalar(max(ratios)),
        raw_normal_linear=scalar(vector_norm([value.a[k, j] for k in range(99, 223) for j in range(count)])),
        reduced_normal_linear=scalar(vector_norm([reduced.a[k, j] for k in range(99, 223) for j in range(count)])),
        shared_output_remainder=scalar(difference.r),
        first_failing_coordinate=next((i for i, v in enumerate(ratios) if not v<1), None),
        prefix_cells_rebuilt=0, Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    out.mkdir(parents=True)
    # save_arrays expects Arb matrices, not bare integer arrays.
    arrays['components'] = arb_mat(count, 1, [arb(i) for i in components])
    save_arrays(out/'arrays.npz', arrays)
    paths = [Path(__file__), ROOT/'scripts/reduce_n12_collar_flow_descriptor.py',
             source/'arrays.npz', source/'report.json', tube_path, tube_path.parent/'report.json',
             CANDIDATE, JET/'arrays.npz', JET/'report.json', Path(A.__file__),
             *[ROOT/('src/bhsm/interface/'+name+'.py') for name in (
                'shared_action_taylor', 'shared_parameter_residual', 'input_linear_taylor',
                'local_input_taylor_action_fast', 'local_state_input_taylor_action',
                'input_linear_anchor_jet', 'coupled_action_output_adjoint')]]
    report['source_SHA256'] = {p.relative_to(ROOT).as_posix(): digest(p) for p in paths}
    report['arrays_SHA256'] = digest(out/'arrays.npz')
    (out/'report.json').write_bytes(encoded(report))
    print(report['status'], float(max(ratios)), flush=True)
    jet.close(); tube.close(); dpack.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=BASE/'flow55_descriptor1')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    calculate(args.source, args.out)
