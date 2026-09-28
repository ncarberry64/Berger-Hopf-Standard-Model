"""Lift the actual state-curve remainder through the same implicit normal graph.

These are coefficients of one local proof remainder, not new launch/history
directions. The frozen tube Jacobian bound supplies the uniform correction.
"""
from reduce_n12_collar_flow_descriptor import (
    ROOT, JET, CANDIDATE, BASE, owner, packet, restore, normal_center, digest,
    encoded, save_arrays, scalar, arb, arb_mat, ctx, np, Path, argparse, json,
    normal_contraction, ScalarJet, input_linear_anchor_action,
)
from bhsm.interface.input_linear_anchor_jet import InputLinearJet
from bhsm.interface.input_linear_taylor import InputLinearTaylor, matrix_norm_bound, vector_norm
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.local_state_input_taylor_action import input_linear_taylor_action


def box_image_bound(matrix):
    rows = [sum((abs(matrix[i, j]).upper() for j in range(matrix.ncols())), arb(0)).upper()
            for i in range(matrix.nrows())]
    row_bound = vector_norm(rows)
    column_bound = sum((vector_norm([matrix[i, j] for i in range(matrix.nrows())])
                        for j in range(matrix.ncols())), arb(0)).upper()
    return min(row_bound, column_bound)


def calculate(out):
    ctx.prec = 512
    if out.exists():
        raise ValueError('new output directory required')
    source = BASE/'flow55_box1'
    tr, tube = packet(source)
    dr, descriptor = packet(BASE/'flow55_descriptor1')
    jr, jet = packet(JET)
    for record in (tr, dr, jr):
        for path, expected in record['source_SHA256'].items():
            if digest(ROOT/path) != expected:
                raise ValueError('frozen input changed: '+path)
    with np.load(CANDIDATE) as z:
        state = [arb(float(v)) for v in z['joint_state_raw'][:98]]
        weights = [arb(float(v)) for v in z['state_weights']]
    U, Dn, J0 = [restore(jet, k) for k in ('fixed_s_direction', 'local_internal_first', 'local_internal_jacobian')]
    s0 = restore(jet, 'current_descriptor')[0, 0]
    center = normal_center(J0, s0)
    h = restore(tube, 'step')[0, 0]
    rho = restore(tube, 'curve_action_radii').entries()
    factor = tr['normal_refinement'][-1]['factor']
    radii = [factor*r for r in restore(tube, 'normal_radii').entries()]
    YZ = restore(descriptor, 'normal_certificate_YZ')
    if not sum(YZ.entries(), arb(0)) < 1:
        raise ArithmeticError('source full tube normal graph is not certified')
    Z = YZ[0, 1]
    R = arb_mat(124, 124, [v.mid() for v in J0.inv().entries()])
    scaled = arb_mat(124, 124, [R[i, j]/radii[i] for i in range(124) for j in range(124)])
    A = owner.action
    maps = [A._dense_mapping(A._integrand(state, i, 0).maps) for i in range(A.POINTS)]
    py = [ScalarJet(v, arb_mat(1, 98, [rho[i]/weights[i] if i == j else arb(0) for j in range(98)]))
          for i, v in enumerate(state)]
    pn = [ScalarJet(v, arb_mat(1, 98)) for v in center]
    beta = [InputLinearJet(arb_mat(1, 124, [scaled[i, j] for i in range(124)]), arb_mat(98, 124))
            for j in range(124)]
    print('Contracting current curve-normal first response', flush=True)
    with input_linear_anchor_action(A):
        partial = normal_contraction(A, py, pn, weights, beta, maps)
    P = scaled*J0
    P = arb_mat(124, 124, [P[i, j]*radii[j] for i in range(124) for j in range(124)])
    response = -P.solve(partial.a.transpose())
    response_replay = P*response+partial.a.transpose()
    if not all(v.contains(0) for v in response_replay.entries()):
        raise ArithmeticError('implicit curve response replay failed')
    size = box_image_bound(response)
    print('Curve response inside old normal proof ball:', float(size), flush=True)
    arrays = dict(curve_normal_response_scaled=response, source_partial_scaled=partial.a.transpose(),
        source_partial_value=partial.c, source_preconditioned_normal=P,
        response_replay=response_replay, response_box_bound=arb_mat([[size]]),
        old_normal_radii=arb_mat(124, 1, radii), old_normal_YZ=YZ,
        curve_action_radii=arb_mat(98, 1, rho), step=arb_mat([[h]]))
    report = dict(status='CURRENT_CURVE_NORMAL_FIRST_RESPONSE_EVALUATED',
        proof_parameter_count=98, physical_history_columns_generated=0,
        old_normal_ball_contains_new_predictor=bool(size<1), response_box_bound=scalar(size),
        actual_flow_tube_included=False, prefix_overlap_certified=False,
        prefix_cells_rebuilt=0, Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    if size<1:
        domain = TaylorDomain([(0, 1, 'interval'), (1, 99, 'box')], 99)
        y, n = [], []
        for i, v in enumerate(state):
            a = [arb(0)]*99
            a[0], a[1+i] = U[i, 0]*h/weights[i], rho[i]/weights[i]
            y.append(domain.affine(v, a))
        for i, v in enumerate(center):
            a = [Dn[i, 0]*h]+[radii[i]*response[i, j] for j in range(98)]
            n.append(domain.affine(v, a))
        beta = [InputLinearTaylor(domain, arb_mat(1, 124, [scaled[i, j] for i in range(124)]),
                                  arb_mat(99, 124)) for j in range(124)]
        print('Bounding the composed current curve-normal residual', flush=True)
        with input_linear_taylor_action(A):
            residual = normal_contraction(A, y, n, weights, beta, maps)
        Y = residual.support()
        posterior = (Y/(1-Z)).upper()
        arrays.update(new_residual_constant=residual.c, new_residual_linear=residual.a,
            new_residual_remainder=arb_mat([[residual.r]]), new_normal_posterior=arb_mat([[posterior]]))
        report.update(status='CURRENT_CURVE_NORMAL_GRAPH_COMPOSED', new_residual_bound=scalar(Y),
            new_normal_posterior=scalar(posterior),
            reused_uniform_normal_jacobian_bound=True,
            correction_argument='Both the true normal root and the new predictor lie in the old convex proof ball; the old Z gives distance <= new_Y/(1-Z)')
        print('New normal correction radius:', float(posterior), flush=True)
    out.mkdir(parents=True)
    save_arrays(out/'arrays.npz', arrays)
    paths = [Path(__file__), ROOT/'scripts/reduce_n12_collar_flow_descriptor.py',
             source/'arrays.npz', source/'report.json', BASE/'flow55_descriptor1/arrays.npz',
             BASE/'flow55_descriptor1/report.json', CANDIDATE, JET/'arrays.npz', JET/'report.json', Path(A.__file__),
             *[ROOT/('src/bhsm/interface/'+name+'.py') for name in (
                'shared_action_taylor', 'input_linear_taylor', 'input_linear_anchor_jet',
                'coupled_action_output_adjoint', 'local_input_taylor_action_fast', 'local_state_input_taylor_action')]]
    report['source_SHA256'] = {p.relative_to(ROOT).as_posix(): digest(p) for p in paths}
    report['arrays_SHA256'] = digest(out/'arrays.npz')
    (out/'report.json').write_bytes(encoded(report))
    jet.close(); tube.close(); descriptor.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    calculate(parser.parse_args().out)
