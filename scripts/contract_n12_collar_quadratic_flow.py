"""Retain the common longitudinal square in the first curve-tube output."""
from reduce_n12_collar_flow_descriptor import (
    ROOT, JET, CANDIDATE, BASE, owner, packet, restore, normal_center, digest,
    encoded, save_arrays, scalar, arb, arb_mat, ctx, np, Path, argparse, json,
    normal_contraction, delta_and_G,
)
from bhsm.interface.shared_action_taylor import scalar_taylor_action
from bhsm.interface.longitudinal_quadratic_taylor import LongitudinalQuadraticDomain
from bhsm.interface.shared_parameter_residual import linear_support


def calculate(out, component):
    ctx.prec = 512
    if out.exists():
        raise ValueError('new output directory required')
    paths = dict(tube=BASE/'flow55_box1', descriptor=BASE/'flow55_descriptor1', numerator=BASE/'flow55_numerator1', jet=JET)
    packs, records = {}, {}
    for key, path in paths.items():
        records[key], packs[key] = packet(path)
        for source, expected in records[key]['source_SHA256'].items():
            if digest(ROOT/source) != expected:
                raise ValueError('source changed: '+source)
    tube, descriptor, numerator, jet = [packs[k] for k in ('tube', 'descriptor', 'numerator', 'jet')]
    components = [int(float(v)) for v in restore(numerator, 'components').entries()]
    if component not in components:
        raise ValueError('choose a component in the source common-output space')
    index = components.index(component)
    with np.load(CANDIDATE) as z:
        state = [arb(float(v)) for v in z['joint_state_raw'][:98]]
        weights = [arb(float(v)) for v in z['state_weights']]
    U, Dn, J0 = [restore(jet, k) for k in ('fixed_s_direction', 'local_internal_first', 'local_internal_jacobian')]
    s0 = restore(jet, 'current_descriptor')[0, 0]
    center = normal_center(J0, s0)
    h = restore(tube, 'step')[0, 0]
    rho = restore(tube, 'curve_action_radii').entries()
    posterior = restore(descriptor, 'normal_posterior')[0, 0]
    factor = records['tube']['normal_refinement'][-1]['factor']
    nr = [factor*r for r in restore(tube, 'normal_radii').entries()]
    if not sum(restore(descriptor, 'normal_certificate_YZ').entries(), arb(0)) < 1:
        raise ArithmeticError('source normal inclusion failed')
    domain = LongitudinalQuadraticDomain([(0, 1, 'interval'), (1, 99, 'box'), (99, 223, 'euclidean')], 223)
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
    A = owner.action
    maps = [A._dense_mapping(A._integrand(state, i, 0).maps) for i in range(A.POINTS)]
    bd = restore(descriptor, 'descriptor_adjoint').entries()
    bgm = restore(numerator, 'numerator_adjoint')
    bg = [bgm[index, j] for j in range(124)]
    with scalar_taylor_action(A):
        delta, G = delta_and_G(A, y, n, s, weights, maps)
        print('Quadratic descriptor value completed', flush=True)
        delta -= normal_contraction(A, y, n, weights, bd, maps)
        print('Quadratic descriptor normal contraction completed', flush=True)
        result = G[component]/rho[component]-normal_contraction(A, y, n, weights, bg, maps)
    positive = bool(delta.enclosure()>0)
    arrays = {}
    encode = lambda v: arb_mat(1, 226, [v.c]+v.a.entries()+[v.q, v.r])
    arrays['descriptor_model'] = encode(delta)
    arrays['numerator_model'] = encode(result)
    report = dict(status='LONGITUDINAL_QUADRATIC_COLLAR_OUTPUT', component=component,
        descriptor_positive=positive, descriptor_enclosure=scalar(delta.enclosure()),
        common_square='theta_0^2 only; all other mixed products remain outwardly bounded',
        source_domain_unchanged=True, actual_flow_tube_included=False, prefix_overlap_certified=False,
        prefix_cells_rebuilt=0, Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    if positive:
        flow = result/delta-U[component, 0]/rho[component]
        rest = flow.a.entries(); rest[0] = arb(0)
        coefficient = h*(abs(flow.c).upper()+abs(flow.a[0, 0]).upper()/2+abs(flow.q).upper()/3
                          +linear_support(rest, domain.groups))
        tail = h*flow.r
        ratio = (coefficient+tail).upper()
        arrays['flow_defect_model'] = encode(flow)
        arrays['integral_coefficient_tail'] = arb_mat([[coefficient, tail, ratio]])
        report.update(first_exit_ratio=scalar(ratio), coefficient_integral=scalar(coefficient),
            remainder_integral=scalar(tail), this_component_passes=bool(ratio<1),
            original_affine_ratio=records['numerator']['maximum_first_exit_ratio'])
        print('Quadratic component', component, 'first-exit ratio', float(ratio), flush=True)
    out.mkdir(parents=True)
    save_arrays(out/'arrays.npz', arrays)
    files = [Path(__file__), ROOT/'scripts/reduce_n12_collar_flow_descriptor.py',
             CANDIDATE, Path(A.__file__), ROOT/'src/bhsm/interface/longitudinal_quadratic_taylor.py',
             ROOT/'src/bhsm/interface/shared_action_taylor.py', ROOT/'src/bhsm/interface/shared_parameter_residual.py']
    for path in paths.values():
        files.extend([path/'arrays.npz', path/'report.json'])
    report['source_SHA256'] = {p.relative_to(ROOT).as_posix(): digest(p) for p in files}
    report['arrays_SHA256'] = digest(out/'arrays.npz')
    (out/'report.json').write_bytes(encoded(report))
    for p in packs.values():
        p.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--component', type=int, default=82)
    args = parser.parse_args()
    calculate(args.out, args.component)
