"""Compose the descriptor numerator with the same normal residual before support.

The identity delta = delta-beta*F holds on the certified implicit graph for
any fixed beta. The anchor adjoint improves correlation, not the equations.
"""
from contract_n12_collar_shared_speed import (
    ROOT, JET, CANDIDATE, owner, packet, restore, normal_center, digest,
    encoded, save_arrays, scalar, arb, arb_mat, ctx, np, Path, argparse, json,
)
from bhsm.interface.shared_action_taylor import TaylorDomain, scalar_taylor_action
from bhsm.interface.shared_parameter_residual import linear_support
from bhsm.interface.input_linear_anchor_jet import ScalarJet, input_linear_anchor_action
from bhsm.interface.input_linear_taylor import matrix_norm_bound, vector_norm

BASE = ROOT/'artifacts/flagship_integration/reset_prefix_collar_20260928'


def delta_and_G(A, y, n, s, weights, maps):
    qw, rw, _, _ = A.metric_data()
    qw, rw = [[arb(float(v)) for v in a] for a in (qw, rw)]
    psi, hard, b = n[:61], n[62:123], n[123]
    p = [arb(0)]*37+psi
    config = [qw[i]*y[37+i] for i in range(37)]
    da = [arb(0)]*37+[rw[i]*psi[i]/weights[37+i] for i in range(61)]
    dh = [config[i]/weights[i] for i in range(37)]+[rw[i]*hard[i]/weights[37+i] for i in range(61)]
    c = A._contracted_action(y, [p, p, da], maps)
    R = A._contracted_action(y, [p, p, dh], maps)
    G = [s*v for v in config]+[rw[i]*(b*psi[i]+s*hard[i]) for i in range(61)]
    return b*c+s*R, G


def normal_contraction(A, y, n, weights, beta, maps):
    zero = y[0]*0
    dot = lambda a, b: sum((x*z for x, z in zip(a, b, strict=True)), zero)
    pad = lambda a: [arb(0)]*37+list(a)
    v, vn, w, wb = beta[:61], beta[61], beta[62:123], beta[123]
    psi, lam, hard, b = n[:61], n[61], n[62:123], n[123]
    qw, rw, _, _ = A.metric_data()
    qw, rw = [[arb(float(v)) for v in a] for a in (qw, rw)]
    g = [w[i]*rw[i]*qw[i]/weights[i] for i in range(37)]+[arb(0)]*61
    c = pad([w[i]*rw[i]/weights[37+i] for i in range(61)])
    d = [qw[i]*y[37+i]/weights[i] for i in range(37)]+[arb(0)]*61
    result = A._contracted_action(y, [pad(v), pad(psi)], maps)
    result += A._contracted_action(y, [pad(w), pad(hard)], maps)
    result -= A._contracted_action(y, [g], maps)
    result += A._contracted_action(y, [c, d], maps)
    return result-lam*dot(v, psi)+vn*(dot(psi, psi)-1)/2-lam*dot(w, hard)+b*dot(w, psi)+wb*dot(psi, hard)


def integral_bound(model, h):
    """theta=t/h is known; the other shared parameters may vary with time."""
    rest = model.a.entries()
    rest[0] = arb(0)
    return (h*(abs(model.c).upper()+abs(model.a[0, 0]).upper()/2
                +linear_support(rest, model.domain.groups)+model.r)).upper()


def calculate(source, out):
    ctx.prec = 512
    if out.exists():
        raise ValueError('new output directory required')
    fr, frozen = packet(source)
    for path, expected in fr['source_SHA256'].items():
        if digest(ROOT/path) != expected:
            raise ValueError('flow-tube source changed: '+path)
    jr, data = packet(JET)
    with np.load(CANDIDATE) as z:
        state = [arb(float(v)) for v in z['joint_state_raw'][:98]]
        weights = [arb(float(v)) for v in z['state_weights']]
        reference = [arb(float(v)) for v in z['branch_reference']]
    J0 = restore(data, 'local_internal_jacobian')
    s0 = restore(data, 'current_descriptor')[0, 0]
    center = normal_center(J0, s0)
    U, Dn = [restore(data, k) for k in ('fixed_s_direction', 'local_internal_first')]
    h = restore(frozen, 'step')[0, 0]
    rho = restore(frozen, 'curve_action_radii').entries()
    # Replay the source's proved radius rescaling from its exact array data.
    factor = fr['normal_refinement'][-1]['factor']
    nr = [factor*v for v in restore(frozen, 'normal_radii').entries()]
    Y = (vector_norm(restore(frozen, 'residual_constant').entries())
         +vector_norm(restore(frozen, 'residual_linear').entries())
         +restore(frozen, 'residual_remainder')[0, 0])/factor
    tails = restore(frozen, 'jacobian_tail_bounds')
    Z = (matrix_norm_bound(restore(frozen, 'jacobian_constant'))
         +matrix_norm_bound(restore(frozen, 'jacobian_linear'))
         +factor*tails[0, 0]+tails[0, 1])
    if not Y+Z < 1:
        raise ArithmeticError('source does not prove the full state-tube normal graph')
    posterior = (Y/(1-Z)).upper()
    A = owner.action
    maps = [A._dense_mapping(A._integrand(state, i, 0).maps) for i in range(A.POINTS)]
    ny = [ScalarJet(v, arb_mat(1, 124)) for v in state]
    nn = [ScalarJet(v, arb_mat(1, 124, [arb(i == j) for j in range(124)])) for i, v in enumerate(center)]
    with input_linear_anchor_action(A):
        anchor, Ganchor = delta_and_G(A, ny, nn, ScalarJet(s0, arb_mat(1, 124)), weights, maps)
    solved = J0.transpose().solve(anchor.a.transpose()).transpose()
    beta = arb_mat(1, 124, [v.mid() for v in solved.entries()])
    defect = anchor.a-beta*J0
    print('Descriptor anchor adjoint defect:', float(vector_norm(defect.entries())), flush=True)
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
    with scalar_taylor_action(A):
        delta, G = delta_and_G(A, y, n, s, weights, maps)
        print('Shared descriptor numerator evaluated', flush=True)
        normal = normal_contraction(A, y, n, weights, beta.entries(), maps)
    reduced = delta-normal
    positive = bool(reduced.enclosure()>0)
    encode = lambda v: arb_mat(1, 225, [v.c]+v.a.entries()+[v.r])
    arrays = dict(descriptor_numerator=encode(delta), normal_contraction=encode(normal),
        reduced_descriptor_numerator=encode(reduced), descriptor_adjoint=beta,
        anchor_adjoint_defect=defect, normal_certificate_YZ=arb_mat([[Y, Z]]),
        normal_posterior=arb_mat([[posterior]]))
    report = dict(status='COLLAR_DESCRIPTOR_COMPOSED_WITH_NORMAL_GRAPH',
        source_normal_graph_reverified=True, descriptor_positive=positive,
        raw_descriptor=scalar(delta.enclosure()), reduced_descriptor=scalar(reduced.enclosure()),
        normal_linear_before=scalar(vector_norm([delta.a[0, i] for i in range(99, 223)])),
        normal_linear_after=scalar(vector_norm([reduced.a[0, i] for i in range(99, 223)])),
        actual_flow_tube_included=False, prefix_overlap_certified=False,
        prefix_cells_rebuilt=0, Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    if positive:
        defects = [G[i]/reduced-U[i, 0] for i in range(98)]
        ratios = [(integral_bound(v, h)/rho[i]).upper() for i, v in enumerate(defects)]
        arrays['flow_first_exit_ratios'] = arb_mat(98, 1, ratios)
        arrays['fixed_s_curve_defect_models'] = arb_mat(98, 225,
            [a for v in defects for a in [v.c]+v.a.entries()+[v.r]])
        report['maximum_first_exit_ratio'] = scalar(max(ratios))
        report['first_failing_coordinate'] = next((i for i, v in enumerate(ratios) if not v<1), None)
        report['actual_flow_tube_included'] = all(v<1 for v in ratios)
        print('Maximum first-exit ratio:', float(max(ratios)), flush=True)
    overlap = sum((reference[i]*n[i].enclosure() for i in range(61)), arb(0))
    if not overlap>0:
        raise ArithmeticError('current orientation unresolved')
    report['positive_reference_overlap'] = scalar(overlap)
    out.mkdir(parents=True)
    save_arrays(out/'arrays.npz', arrays)
    paths = [Path(__file__), CANDIDATE, JET/'arrays.npz', JET/'report.json',
             source/'arrays.npz', source/'report.json', Path(A.__file__),
             *[ROOT/('src/bhsm/interface/'+name+'.py') for name in (
                'shared_action_taylor', 'shared_parameter_residual',
                'input_linear_anchor_jet', 'coupled_action_output_adjoint')]]
    report['source_SHA256'] = {p.relative_to(ROOT).as_posix(): digest(p) for p in paths}
    report['arrays_SHA256'] = digest(out/'arrays.npz')
    (out/'report.json').write_bytes(encoded(report))
    data.close(); frozen.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=BASE/'flow55_box1')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    calculate(args.source, args.out)
