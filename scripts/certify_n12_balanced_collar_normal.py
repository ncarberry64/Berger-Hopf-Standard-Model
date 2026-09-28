"""Uniform normal inclusion on a coupled curve corridor, with streamed columns.

Only one Hessian column pair is resident. Common curve coefficients of the
action and algebraic normal terms are added before their box support.
"""
from bind_n12_collar_curve_normal_response import (
    ROOT, JET, CANDIDATE, BASE, owner, packet, restore, normal_center, digest,
    encoded, save_arrays, scalar, arb, arb_mat, ctx, np, Path, argparse,
    normal_contraction, InputLinearTaylor, matrix_norm_bound, vector_norm,
    TaylorDomain, input_linear_taylor_action, box_image_bound,
)


def algebraic_column(domain, n, radii, scaled, j):
    """Column of I-D^-1 R F_n D excluding the two action-Hessian blocks."""
    zero = domain.affine(0)
    result = []
    for i in range(124):
        v = domain.affine(arb(i == j))
        if j < 61:
            v -= radii[j]*(-scaled[i, j]*n[61]+scaled[i, 61]*n[j]
                +scaled[i, 62+j]*n[123]+scaled[i, 123]*n[62+j])
        elif j == 61:
            v += radii[j]*sum((scaled[i, k]*n[k]+scaled[i, 62+k]*n[62+k]
                               for k in range(61)), zero)
        elif j < 123:
            k = j-62
            v -= radii[j]*(-scaled[i, j]*n[61]+scaled[i, 123]*n[k])
        else:
            v -= radii[j]*sum((scaled[i, 62+k]*n[k] for k in range(61)), zero)
        result.append(v)
    return result


def stream_jacobian(A, y, n, radii, scaled, maps):
    domain = y[0].domain
    dimension = domain.dimension
    zero = domain.affine(0)
    C, L = arb_mat(124, 124), arb_mat(124, 124)
    curve_squares, normal_squares, action_squares = arb(0), arb(0), arb(0)
    column_bounds = []

    def consume(j, entries):
        nonlocal curve_squares, normal_squares
        curve_column, normal_column = arb(0), arb(0)
        for i, v in enumerate(entries):
            C[i, j], L[i, j] = v.c, v.a[0, 0]
            # These are genuine box parameters, so the entrywise l1 support
            # followed by Frobenius is an outward operator bound.
            width = sum((abs(v.a[0, k]).upper() for k in range(1, dimension)), arb(0)).upper()
            curve_column += width**2
            normal_column += v.r**2
        curve_squares += curve_column
        normal_squares += normal_column
        column_bounds.append((j, curve_column.sqrt().upper(), normal_column.sqrt().upper()))

    for j in range(61):
        legs = [zero]*37
        for k in range(61):
            coeff = ([scaled[i, k]*radii[j] for i in range(124)]
                     +[scaled[i, 62+k]*radii[62+j] for i in range(124)])
            legs.append(InputLinearTaylor(domain, arb_mat(1, 248, coeff), arb_mat(dimension, 248)))
        with input_linear_taylor_action(A):
            H = A._contracted_action(y, [legs, [arb(i == 37+j) for i in range(98)]], maps)
        for column, offset in ((j, 0), (62+j, 124)):
            entries = algebraic_column(domain, n, radii, scaled, column)
            for i in range(124):
                entries[i] -= domain.affine(H.c[0, offset+i],
                    [H.a[k, offset+i] for k in range(dimension)])
            consume(column, entries)
        # One dual Euclidean remainder for the pair of columns, counted once.
        action_squares += H.r**2
        if j % 10 == 0 or j == 60:
            print('Coupled normal Jacobian:', j+1, '/61', flush=True)
    for j in (61, 123):
        consume(j, algebraic_column(domain, n, radii, scaled, j))
    tails = [curve_squares.sqrt().upper(), normal_squares.sqrt().upper(), action_squares.sqrt().upper()]
    return dict(jacobian_constant=C, jacobian_theta=L,
                jacobian_tail_bounds=arb_mat([tails]),
                jacobian_column_bounds=arb_mat([[arb(j), c, n] for j, c, n in sorted(column_bounds)]))


def calculate(out, proposal):
    ctx.prec = 512
    if out.exists():
        raise ValueError('new output directory required')
    pr, prop = packet(proposal)
    jr, jet = packet(JET)
    for record in (pr, jr):
        for path, expected in record['source_SHA256'].items():
            if digest(ROOT/path) != expected:
                raise ValueError('frozen source changed: '+path)
    with np.load(CANDIDATE) as z:
        state = [arb(float(v)) for v in z['joint_state_raw'][:98]]
        weights = [arb(float(v)) for v in z['state_weights']]
        reference = [arb(float(v)) for v in z['branch_reference']]
    U, Dn, J0 = [restore(jet, k) for k in ('fixed_s_direction', 'local_internal_first', 'local_internal_jacobian')]
    s0 = restore(jet, 'current_descriptor')[0, 0]
    center = normal_center(J0, s0)
    h = restore(prop, 'step')[0, 0]
    rho = restore(prop, 'curve_action_radii').entries()
    response = restore(prop, 'curve_normal_response')
    domain = TaylorDomain([(0, 1, 'interval'), (1, 99, 'box')], 99)
    y, n = [], []
    for i, v in enumerate(state):
        a = [arb(0)]*99
        a[0], a[1+i] = U[i, 0]*h/weights[i], rho[i]/weights[i]
        y.append(domain.affine(v, a))
    for i, v in enumerate(center):
        n.append(domain.affine(v, [Dn[i, 0]*h]+[response[i, j] for j in range(98)]))
    radii = []
    for start, stop in ((0, 61), (61, 62), (62, 123), (123, 124)):
        block = arb_mat(stop-start, 98, [response[i, j] for i in range(start, stop) for j in range(98)])
        size = vector_norm([h*Dn[i, 0] for i in range(start, stop)])+box_image_bound(block)
        radii.extend([(size/64+arb(2)**-400).upper()]*(stop-start))
    R = arb_mat(124, 124, [v.mid() for v in J0.inv().entries()])
    scaled = arb_mat(124, 124, [R[i, j]/radii[i] for i in range(124) for j in range(124)])
    A = owner.action
    maps = [A._dense_mapping(A._integrand(state, i, 0).maps) for i in range(A.POINTS)]
    beta = [InputLinearTaylor(domain, arb_mat(1, 124, [scaled[i, j] for i in range(124)]),
                             arb_mat(99, 124)) for j in range(124)]
    with input_linear_taylor_action(A):
        residual = normal_contraction(A, y, n, weights, beta, maps)
    Y0 = residual.support()
    print('Coupled normal residual:', float(Y0), flush=True)
    corrected = [domain.affine(v.c, v.a.entries(), r) for v, r in zip(n, radii, strict=True)]
    arrays = stream_jacobian(A, y, corrected, radii, scaled, maps)
    tail = arrays['jacobian_tail_bounds']
    fixed = matrix_norm_bound(arrays['jacobian_constant'])+matrix_norm_bound(arrays['jacobian_theta'])+tail[0, 0]+tail[0, 2]
    attempts = []
    factor = 1
    for g in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024):
        Y, Z = (Y0/g).upper(), (fixed+g*tail[0, 1]).upper()
        attempts.append(dict(factor=g, residual=scalar(Y), contraction=scalar(Z)))
        if Y+Z<1:
            factor = g
            break
    else:
        Y, Z = Y0, (fixed+tail[0, 1]).upper()
    passed = bool(Y+Z<1)
    posterior = (Y/(1-Z)).upper() if passed else None
    # If a graph closes, connect it to the normalized oriented frozen root.
    anchor = vector_norm([2*center[i].rad()/(factor*radii[i]) for i in range(124)])
    orientation = sum((reference[i]*(n[i].enclosure()+arb(0, factor*radii[i])) for i in range(61)), arb(0))
    if passed and not (anchor<1 and orientation>0):
        raise ArithmeticError('normal graph does not bind the frozen oriented anchor')
    arrays.update(step=arb_mat([[h]]), curve_action_radii=arb_mat(98, 1, rho),
        curve_normal_response=response, initial_normal_radii=arb_mat(124, 1, radii),
        normal_radii=arb_mat(124, 1, [factor*r for r in radii]),
        residual_constant=residual.c/factor, residual_linear=residual.a/factor,
        residual_remainder=arb_mat([[residual.r/factor]]), YZ=arb_mat([[Y, Z]]),
        anchor_distance=arb_mat([[anchor]]), orientation=arb_mat([[orientation]]))
    if passed:
        arrays['posterior'] = arb_mat([[posterior]])
    out.mkdir(parents=True)
    save_arrays(out/'arrays.npz', arrays)
    files = [Path(__file__), CANDIDATE, Path(A.__file__),
        ROOT/'scripts/bind_n12_collar_curve_normal_response.py',
        ROOT/'scripts/reduce_n12_collar_flow_descriptor.py',
        *[ROOT/('src/bhsm/interface/'+name+'.py') for name in (
            'shared_action_taylor', 'input_linear_taylor', 'local_input_taylor_action_fast',
            'local_state_input_taylor_action')]]
    for path in (proposal, JET):
        files.extend([path/'arrays.npz', path/'report.json'])
    report = dict(status='BALANCED_CURVE_NORMAL_GRAPH_CERTIFIED' if passed else 'BALANCED_CURVE_NORMAL_INCLUSION_FAILED',
        normal_graph_certified=passed, step=scalar(h), Y=scalar(Y), Z=scalar(Z),
        posterior=scalar(posterior) if passed else None, refinement=attempts,
        radius_factor=factor, state_curve_parameter_count=98,
        streamed_column_pairs=61, physical_history_columns_generated=0,
        composition='Hessian and normal algebraic coefficients combined before curve box support',
        actual_flow_tube_included=False, first_variation_transported=False,
        prefix_overlap_certified=False, Gate7_closed=False, FULL_BHSM_COMPLETE=False,
        source_SHA256={p.relative_to(ROOT).as_posix(): digest(p) for p in files},
        arrays_SHA256=digest(out/'arrays.npz'))
    (out/'report.json').write_bytes(encoded(report))
    print(report['status'], 'Y=', float(Y), 'Z=', float(Z), flush=True)
    prop.close(); jet.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--proposal', type=Path, default=BASE/'balanced45_proposal1')
    args = parser.parse_args()
    calculate(args.out, args.proposal)
