"""Enclose the first actual fixed-s collar segment, retaining common normals.

This is a local first-exit test, not a new prefix integration campaign.
All candidate radii must pass the existing normal and flow inequalities.
"""
from contract_n12_collar_shared_speed import (
    ROOT, JET, CANDIDATE, owner, packet, restore, normal_center, digest,
    encoded, save_arrays, scalar, arb, arb_mat, ctx, np, Path, argparse, json,
    shared_speed, coefficient_packet,
)
from certify_n12_collar_normal_graph import composed_residual, correlated_jacobian, refine_normal_radius
from bhsm.interface.shared_action_taylor import TaylorDomain


def calculate(out, exponent, curve_factor):
    ctx.prec = 512
    if out.exists():
        raise ValueError('new output directory required')
    if curve_factor <= 0:
        raise ValueError('positive curve proposal factor required')
    jr, data = packet(JET)
    sources = {k.replace('\\', '/'): v for k, v in jr['source_SHA256'].items()}
    A = owner.action
    for path in (CANDIDATE, Path(A.__file__)):
        if sources[path.relative_to(ROOT).as_posix()] != digest(path):
            raise ValueError('frozen current source binding changed')
    with np.load(CANDIDATE) as z:
        state = [arb(float(v)) for v in z['joint_state_raw'][:98]]
        weights = [arb(float(v)) for v in z['state_weights']]
    J0 = restore(data, 'local_internal_jacobian')
    s0 = restore(data, 'current_descriptor')[0, 0]
    center = normal_center(J0, s0)
    Dn, U, curvature = [restore(data, key) for key in (
        'local_internal_first', 'fixed_s_direction', 'fixed_s_curve_second')]
    h = arb(2)**(-exponent)
    domain = TaylorDomain([(0, 1, 'interval')], 1)
    # This is only a proposal. The point curvature does not certify this
    # radius; the first-exit inequality below must certify the full domain.
    curve_radius = [(curve_factor*h*h*(abs(curvature[i, 0]).upper()+arb(1))).upper()
                    for i in range(98)]
    y = [domain.affine(v, [U[i, 0]*h/weights[i]], curve_radius[i]/weights[i])
         for i, v in enumerate(state)]
    n = [domain.affine(v, [Dn[i, 0]*h]) for i, v in enumerate(center)]
    radii = []
    for start, stop in ((0, 61), (61, 62), (62, 123), (123, 124)):
        size = sum((Dn[i, 0]**2 for i in range(start, stop)), arb(0)).sqrt()
        radii.extend([(size*h/64+arb(2)**-400).upper()]*(stop-start))
    R = arb_mat(124, 124, [v.mid() for v in J0.inv().entries()])
    scaled = arb_mat(124, 124, [R[i, j]/radii[i] for i in range(124) for j in range(124)])
    maps = [A._dense_mapping(A._integrand(state, i, 0).maps) for i in range(A.POINTS)]
    residual = composed_residual(A, y, n, weights, scaled, maps)
    Y = residual.support()
    arrays = dict(step=arb_mat([[h]]), curve_action_radii=arb_mat(98, 1, curve_radius),
        normal_radii=arb_mat(124, 1, radii), residual_constant=residual.c,
        residual_linear=residual.a, residual_remainder=arb_mat([[residual.r]]))
    report = dict(status='COLLAR_FLOW_TUBE_NORMAL_RESIDUAL_SCREEN', exponent=exponent,
        curve_proposal_factor=curve_factor, scaled_normal_residual=scalar(Y),
        normal_residual_components=dict(constant=scalar(residual.constant_bound()),
            common_linear=scalar(residual.linear_bound()), nonlinear_tail=scalar(residual.r)),
        first_failing_location='First current-reset fixed-s segment',
        actual_flow_tube_included=False, prefix_overlap_certified=False,
        physical_direction_columns_generated=0, prefix_cells_rebuilt=0,
        physical_failure_claim=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    print('Curve tube normal residual:', float(Y), flush=True)
    # Avoid the 61-column contraction if even the residual alone is beyond
    # the already tested proof-radius refinement range.
    if Y >= 1024:
        report['first_failing_operand'] = 'Preconditioned normal residual: independent state-curve remainder support'
    else:
        corrected = [domain.affine(v.c, v.a.entries(), r) for v, r in zip(n, radii, strict=True)]
        _, derivative = correlated_jacobian(A, y, corrected, radii, scaled, maps)
        tail = derivative['jacobian_tail_bounds']
        g, Y, Z, refinement = refine_normal_radius(Y, derivative['jacobian_constant'],
            derivative['jacobian_linear'], tail[0, 0], tail[0, 1])
        report.update(normal_refinement=refinement, Y=scalar(Y), Z=scalar(Z))
        arrays.update(derivative)
        if Y+Z >= 1:
            report['first_failing_operand'] = 'Uniform normal self-map/contraction on state-curve tube'
        else:
            radii = [g*r for r in radii]
            posterior = (Y/(1-Z)).upper()
            enclosed = [domain.affine(v.c, v.a.entries(), posterior*r)
                        for v, r in zip(n, radii, strict=True)]
            models = shared_speed(A, y, enclosed, domain.affine(s0, [h]), weights, maps)
            arrays.update({'enclosed_'+key: coefficient_packet(value) for key, value in models.items()})
            report['positive_descriptor_speed'] = bool(models['speed'].enclosure()>0)
            if not report['positive_descriptor_speed']:
                report['first_failing_operand'] = 'Descriptor speed on the complete state-curve tube'
            else:
                qw, rw, _, _ = A.metric_data()
                qw, rw = [[arb(float(v)) for v in a] for a in (qw, rw)]
                s = domain.affine(s0, [h])
                psi, hard, b = enclosed[:61], enclosed[62:123], enclosed[123]
                G = [s*qw[i]*y[37+i] for i in range(37)]
                G += [rw[i]*(b*psi[i]+s*hard[i]) for i in range(61)]
                defects = [G[i]/models['delta']-U[i, 0] for i in range(98)]
                # Integrate the signed constant/linear model before support.
                # A uniform remainder integrates to at most h times its bound.
                ratios = [(h*(abs(v.c).upper()+abs(v.a[0, 0]).upper()/2+v.r)/r).upper()
                          for v, r in zip(defects, curve_radius, strict=True)]
                arrays['flow_first_exit_ratios'] = arb_mat(98, 1, ratios)
                report['maximum_first_exit_ratio'] = scalar(max(ratios))
                report['actual_flow_tube_included'] = all(v<1 for v in ratios)
                report['first_failing_operand'] = None if report['actual_flow_tube_included'] else 'Curve first-exit remainder'
                report['status'] = 'FIRST_COLLAR_FLOW_SEGMENT_ENCLOSED' if report['actual_flow_tube_included'] else 'COLLAR_FLOW_FIRST_EXIT_FAILED'
    out.mkdir(parents=True)
    save_arrays(out/'arrays.npz', arrays)
    paths = [Path(__file__), ROOT/'scripts/contract_n12_collar_shared_speed.py',
             ROOT/'scripts/certify_n12_collar_normal_graph.py', CANDIDATE,
             JET/'arrays.npz', JET/'report.json', Path(A.__file__),
             *[ROOT/('src/bhsm/interface/'+name+'.py') for name in (
                 'shared_action_taylor', 'input_linear_taylor', 'local_input_taylor_action_fast')]]
    report['source_SHA256'] = {p.relative_to(ROOT).as_posix(): digest(p) for p in paths}
    report['arrays_SHA256'] = digest(out/'arrays.npz')
    (out/'report.json').write_bytes(encoded(report))
    print(report['status'], report['first_failing_operand'], flush=True)
    data.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--exponent', type=int, default=55)
    parser.add_argument('--curve-factor', type=int, default=16)
    args = parser.parse_args()
    calculate(args.out, args.exponent, args.curve_factor)
