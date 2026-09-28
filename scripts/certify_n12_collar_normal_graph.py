"""Parameter-uniform normal inclusion over the first affine collar predictor.

The residual is composed with one frozen Newton inverse before support.
The Jacobian enclosure is deliberately independent of this residual bound.
Only a successful pair of Banach inequalities certifies the implicit graph;
neither inequality certifies an ODE trajectory or prefix overlap.
"""
from contract_n12_collar_shared_speed import (
    ROOT, JET, CANDIDATE, owner, packet, restore, normal_center, digest,
    encoded, save_arrays, scalar, arb, arb_mat, ctx, np, Path, argparse, json,
    shared_speed, coefficient_packet,
)
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.input_linear_taylor import InputLinearTaylor, matrix_norm_bound
from bhsm.interface.local_input_taylor_action_fast import input_linear_taylor_action


def jacobian(H, n):
    psi, lam, hard, b = n[:61], n[61], n[62:123], n[123]
    J = arb_mat(124, 124)
    for i in range(61):
        J[i, 61], J[61, i] = -psi[i], psi[i]
        J[62+i, i], J[62+i, 61], J[62+i, 123] = b, -hard[i], psi[i]
        J[123, i], J[123, 62+i] = hard[i], psi[i]
        for j in range(61):
            J[i, j] = J[62+i, 62+j] = H[i, j]-(lam if i == j else 0)
    return J


def composed_residual(A, y, n, weights, inverse_scaled, maps):
    """Return <u, diag(r)^-1 R F(y,n)> for arbitrary Euclidean unit u."""
    domain = y[0].domain
    zero = domain.affine(0)
    covectors = [InputLinearTaylor(domain,
        arb_mat(1, 124, [inverse_scaled[i, j] for i in range(124)]),
        arb_mat(1, 124)) for j in range(124)]
    v, vn, w, wb = covectors[:61], covectors[61], covectors[62:123], covectors[123]
    psi, lam, hard, b = n[:61], n[61], n[62:123], n[123]
    qw, rw, _, _ = A.metric_data()
    qw, rw = [[arb(float(a)) for a in vec] for vec in (qw, rw)]
    pad = lambda a: [zero]*37+list(a)
    dot = lambda a, b: sum((x*y for x, y in zip(a, b, strict=True)), zero)
    g = [w[i]*rw[i]*qw[i]/weights[i] for i in range(37)]+[zero]*61
    c = pad([w[i]*rw[i]/weights[37+i] for i in range(61)])
    d = [qw[i]*y[37+i]/weights[i] for i in range(37)]+[zero]*61
    with input_linear_taylor_action(A):
        residual = A._contracted_action(y, [pad(v), pad(psi)], maps)
        residual += A._contracted_action(y, [pad(w), pad(hard)], maps)
        residual -= A._contracted_action(y, [g], maps)
        residual += A._contracted_action(y, [c, d], maps)
    residual += -dot(v, psi)*lam+vn*((dot(psi, psi)-1)/2)
    residual += -dot(w, hard)*lam+dot(w, psi)*b+wb*dot(psi, hard)
    return residual


def correlated_jacobian(A, y, n, radii, scaled, maps):
    """Compose the complete preconditioned normal Jacobian before support.

    One arbitrary output covector retains all 124 rows. The 61 fixed Hessian
    columns are normal-system columns, not new physical history directions.
    Each scalar tail controls a whole column's Euclidean norm.
    """
    domain = y[0].domain
    zero = domain.affine(0)
    entries = [[domain.affine(arb(i == j)) for j in range(124)] for i in range(124)]
    tails = []
    # Hessian dependence is only in two repeated 61x61 diagonal blocks.
    for j in range(61):
        legs = [zero]*37
        for k in range(61):
            coefficients = ([scaled[i, k]*radii[j] for i in range(124)]
                +[scaled[i, 62+k]*radii[62+j] for i in range(124)])
            legs.append(InputLinearTaylor(domain, arb_mat(1, 248, coefficients), arb_mat(1, 248)))
        axis = [arb(i == 37+j) for i in range(98)]
        with input_linear_taylor_action(A):
            result = A._contracted_action(y, [legs, axis], maps)
        for i in range(124):
            entries[i][j] -= domain.affine(result.c[0, i], [result.a[0, i]])
            entries[i][62+j] -= domain.affine(result.c[0, 124+i], [result.a[0, 124+i]])
        # Joint dual Euclidean tail bounds the pair of columns; its square
        # contributes once to a Frobenius bound for the assembled tail.
        tails.append(result.r)
        if j % 10 == 0:
            print('Shared normal Jacobian columns:', j+1, '/61', flush=True)
    for i in range(124):
        for j in range(61):
            entries[i][j] -= radii[j]*(-scaled[i, j]*n[61]+scaled[i, 61]*n[j]
                +scaled[i, 62+j]*n[123]+scaled[i, 123]*n[62+j])
            entries[i][62+j] -= radii[62+j]*(-scaled[i, 62+j]*n[61]+scaled[i, 123]*n[j])
        entries[i][61] += radii[61]*sum((scaled[i, j]*n[j]+scaled[i, 62+j]*n[62+j]
                                        for j in range(61)), zero)
        entries[i][123] -= radii[123]*sum((scaled[i, 62+j]*n[j] for j in range(61)), zero)
    constant = arb_mat(124, 124, [v.c for row in entries for v in row])
    linear = arb_mat(124, 124, [v.a[0, 0] for row in entries for v in row])
    algebraic_tail = sum((v.r**2 for row in entries for v in row), arb(0)).sqrt().upper()
    action_tail = sum((v**2 for v in tails), arb(0)).sqrt().upper()
    total = (matrix_norm_bound(constant)+matrix_norm_bound(linear)+algebraic_tail+action_tail).upper()
    return total, dict(jacobian_constant=constant, jacobian_linear=linear,
        jacobian_tail_bounds=arb_mat([[algebraic_tail, action_tail]]))


def refine_normal_radius(Y, constant, linear, normal_tail, action_tail):
    """Uniform radius rescaling for a Jacobian affine in normal variables.

    Under r -> g*r, the normalized residual is Y/g. The constant,
    theta-linear and action-tail matrices are unchanged; only the normal
    correction tail scales by g. No new action evaluations are needed.
    """
    fixed = matrix_norm_bound(constant)+matrix_norm_bound(linear)+action_tail
    attempts = []
    for factor in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024):
        residual = (Y/factor).upper()
        contraction = (fixed+factor*normal_tail).upper()
        attempts.append(dict(factor=factor, residual=float(residual), contraction=float(contraction)))
        if residual+contraction < 1:
            return factor, residual, contraction, attempts
    return 1, Y, (fixed+normal_tail).upper(), attempts


def calculate(out, exponent, correlated=False):
    ctx.prec = 512
    if out.exists():
        raise ValueError('new output directory required')
    jr, data = packet(JET)
    sources = {k.replace('\\', '/'): v for k, v in jr['source_SHA256'].items()}
    A = owner.action
    for path in (CANDIDATE, Path(A.__file__)):
        if sources[path.relative_to(ROOT).as_posix()] != digest(path):
            raise ValueError('frozen current source binding changed')
    with np.load(CANDIDATE) as z:
        state = [arb(float(v)) for v in z['joint_state_raw'][:98]]
        weights = [arb(float(v)) for v in z['state_weights']]
        reference = [arb(float(v)) for v in z['branch_reference']]
    J0 = restore(data, 'local_internal_jacobian')
    s0 = restore(data, 'current_descriptor')[0, 0]
    center = normal_center(J0, s0)
    Dn, U = [restore(data, key) for key in ('local_internal_first', 'fixed_s_direction')]
    h = arb(2)**(-exponent)
    domain = TaylorDomain([(0, 1, 'interval')], 1)
    y = [domain.affine(v, [U[i, 0]*h/weights[i]]) for i, v in enumerate(state)]
    n = [domain.affine(v, [Dn[i, 0]*h]) for i, v in enumerate(center)]
    # Proof radii, not physical-domain tolerances. The normalization uses a
    # single Euclidean ball in these scaled 124 normal coordinates.
    radii = []
    for start, stop in ((0, 61), (61, 62), (62, 123), (123, 124)):
        size = sum((Dn[i, 0]**2 for i in range(start, stop)), arb(0)).sqrt()
        radius = (size*h/1024+arb(2)**-400).upper()
        radii.extend([radius]*(stop-start))
    R = arb_mat(124, 124, [v.mid() for v in J0.inv().entries()])
    scaled = arb_mat(124, 124, [R[i, j]/radii[i] for i in range(124) for j in range(124)])
    maps = [A._dense_mapping(A._integrand(state, i, 0).maps) for i in range(A.POINTS)]
    residual = composed_residual(A, y, n, weights, scaled, maps)
    Y = residual.support()
    print('Signed scaled normal residual bound:', float(Y), flush=True)
    raw_box = np.array([v.enclosure() for v in y], dtype=object)
    normal_box = [v.enclosure()+arb(0, r) for v, r in zip(n, radii, strict=True)]
    if correlated:
        corrected = [domain.affine(v.c, v.a.entries(), r) for v, r in zip(n, radii, strict=True)]
        Z, derivative_arrays = correlated_jacobian(A, y, corrected, radii, scaled, maps)
        derivative_kind = 'Common theta; complete preconditioned Hessian columns before support; full normal correction ball enclosed'
    else:
        with owner.sparse.use_optimized_mixed(A), owner.factored.use_ball_factored_integrand(A, raw_box):
            action = A._arb_action_jets(raw_box)
        H = arb_mat(action.hessian_arb[37:, 37:].tolist())
        J = jacobian(H, normal_box)
        defect = arb_mat([[arb(i == j) for j in range(124)] for i in range(124)])-R*J
        scaled_defect = arb_mat(124, 124,
            [defect[i, j]*radii[j]/radii[i] for i in range(124) for j in range(124)])
        Z = matrix_norm_bound(scaled_defect)
        derivative_arrays = dict(scaled_jacobian_defect=scaled_defect)
        derivative_kind = 'Independent full normal Jacobian on an enclosing Cartesian domain'
    refinement = []
    if correlated:
        tail = derivative_arrays['jacobian_tail_bounds']
        factor, Y, Z, refinement = refine_normal_radius(Y,
            derivative_arrays['jacobian_constant'], derivative_arrays['jacobian_linear'],
            tail[0, 0], tail[0, 1])
        if factor != 1:
            radii = [r*factor for r in radii]
            residual = residual/factor
            normal_box = [v.enclosure()+arb(0, r) for v, r in zip(n, radii, strict=True)]
            derivative_arrays['jacobian_tail_bounds'] = arb_mat([[tail[0, 0]*factor, tail[0, 1]]])
    passed = bool(Z<1 and Y+Z<1)
    arrays = dict(step=arb_mat([[h]]), proof_radii=arb_mat(124, 1, radii),
        preconditioner=R, raw_state_domain=arb_mat(98, 1, list(raw_box)),
        normal_predictor_center=arb_mat(124, 1, center), normal_first=Dn,
        normal_domain=arb_mat(124, 1, normal_box),
        residual_constant=residual.c, residual_linear=residual.a,
        residual_remainder=arb_mat([[residual.r]]),
        **derivative_arrays, YZ=arb_mat([[Y, Z]]))
    speed_report = None
    orientation = None
    anchor_contained = None
    if passed:
        posterior = (Y/(1-Z)).upper()
        enclosed = [domain.affine(v.c, v.a.entries(), posterior*r)
                    for v, r in zip(n, radii, strict=True)]
        models = shared_speed(A, y, enclosed, domain.affine(s0, [h]), weights, maps)
        arrays['normal_posterior_scaled_radius'] = arb_mat([[posterior]])
        arrays.update({'enclosed_'+key: coefficient_packet(value) for key, value in models.items()})
        speed_report = dict(enclosure=scalar(models['speed'].enclosure()),
            positive=bool(models['speed'].enclosure()>0), normal_posterior_scaled_radius=scalar(posterior))
        orientation = sum((reference[i]*enclosed[i].enclosure() for i in range(61)), arb(0))
        anchor_distance = sum(((2*center[i].rad()/radii[i])**2 for i in range(124)), arb(0)).sqrt()
        anchor_contained = bool(anchor_distance < 1)
        if not orientation > 0 or not anchor_contained:
            raise ArithmeticError('uniform graph does not bind the frozen oriented anchor')
        arrays['positive_reference_overlap'] = arb_mat([[orientation]])
        arrays['anchor_scaled_distance'] = arb_mat([[anchor_distance]])
    out.mkdir(parents=True)
    save_arrays(out/'arrays.npz', arrays)
    paths = [Path(__file__), ROOT/'scripts/contract_n12_collar_shared_speed.py',
        CANDIDATE, JET/'arrays.npz', JET/'report.json', Path(A.__file__),
        *[ROOT/('src/bhsm/interface/'+name+'.py') for name in (
            'shared_action_taylor', 'shared_parameter_residual', 'input_linear_taylor',
            'local_input_taylor_action_fast', 'ball_factored_arb_integrand', 'factored_arb_integrand')]]
    report = dict(status='AFFINE_COLLAR_NORMAL_GRAPH_CERTIFIED' if passed else 'AFFINE_COLLAR_NORMAL_INCLUSION_FAILED',
        exponent=exponent, residual_bound=scalar(Y), contraction_bound=scalar(Z),
        inclusion_sum=scalar(Y+Z), actual_normal_graph_included=passed,
        domain='affine raw state predictor, theta in [-1,1]; scaled Euclidean normal ball',
        residual_composed_before_support=True, derivative_bound=derivative_kind,
        implicit_graph_descriptor_speed=speed_report,
        normal_proof_radius_refinement=refinement,
        frozen_anchor_contained=anchor_contained,
        positive_reference_overlap=scalar(orientation) if orientation is not None else None,
        selected_zero_based_index=24 if passed else None,
        branch_authority='Frozen normalized index-24 anchor plus unique connected normal graph; no eigenvalue crossing on an invertible normal Jacobian' if passed else None,
        actual_flow_tube_included=False, prefix_overlap_certified=False,
        physical_direction_columns_generated=0, prefix_cells_rebuilt=0,
        source_SHA256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
        arrays_SHA256=digest(out/'arrays.npz'), Gate7_closed=False, FULL_BHSM_COMPLETE=False)
    (out/'report.json').write_bytes(encoded(report))
    data.close()
    print(report['status'], 'Y=', float(Y), 'Z=', float(Z), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--exponent', type=int, default=75)
    parser.add_argument('--correlated-jacobian', action='store_true')
    args = parser.parse_args()
    calculate(args.out, args.exponent, args.correlated_jacobian)
