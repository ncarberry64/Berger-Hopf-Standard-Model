"""Joint eigenpair/preconditioner transport with physical curvature left explicit."""
from flint import arb, arb_mat
from bhsm.interface.shared_action_taylor import TaylorDomain


def weighted_matrix_norm(matrix, weights):
    """Outward induced weighted infinity norm."""
    n = len(weights)
    if matrix.nrows() != n or matrix.ncols() != n or not all(w > 0 for w in weights):
        raise ValueError('matching square matrix and positive weights required')
    return max((sum((abs(matrix[i, j]).upper()*weights[j] for j in range(n)), arb(0))
                / weights[i]).upper() for i in range(n))


def interpolated_defect(R0, R1, J0, J1, weights):
    """I-R(s)J(s) = (1-s)D0+sD1+s(1-s)(R1-R0)(J1-J0).

    J(s) here is the affine interpolant, not the actual physical Jacobian.
    """
    n = len(weights)
    identity = arb_mat([[int(i == j) for j in range(n)] for i in range(n)])
    D0, D1 = identity-R0*J0, identity-R1*J1
    cross = (R1-R0)*(J1-J0)
    bound = (max(weighted_matrix_norm(D0, weights), weighted_matrix_norm(D1, weights))
             + weighted_matrix_norm(cross, weights)/4).upper()
    return dict(D0=D0, D1=D1, cross=cross, surrogate_defect_upper=bound)


def transport_operands(anchor, end, p0, p1, R0, R1, weights, offset,
                       target_center, target_directions, target_groups,
                       target_fraction, *, curvature, variation):
    """Keep line position, eigenpair and preconditioner in the same namespace.

    Curvature: all-output D4S[preconditioned dual, eta, dx, dx]/8.
    Tube: all-output D3S[preconditioned dual, eta, tube displacement].
    The tube domain includes every spoke from the center line to the target
    offset family; the action is evaluated on it rather than extrapolated.
    """
    size, reduced = len(anchor), len(p0)-1
    if size-offset != reduced or len(p1) != reduced+1 or len(weights) != reduced+1:
        raise ValueError('matching raw state and bordered eigenpair required')
    n = 0 if curvature else len(target_directions[0])
    groups = [] if curvature else list(target_groups)
    s_index, t_index, dual_start = n, n+1, n+2
    eta_start = dual_start+reduced+1
    dimension = eta_start+(reduced if variation else 0)
    groups += [(s_index, s_index+1, 'interval'), (t_index, t_index+1, 'interval'),
               (dual_start, eta_start, 'euclidean')]
    if variation:
        groups.append((eta_start, dimension, 'box'))
    d = TaylorDomain(groups, dimension)
    def unit(index):
        co = [arb(0)]*dimension
        co[index] = arb(1)
        return d.affine(0, co)
    s, t = (1+unit(s_index))/2, (1+unit(t_index))/2
    dx = [b-a for a, b in zip(anchor, end, strict=True)]
    if curvature:
        state = [a+t*v for a, v in zip(anchor, dx, strict=True)]
        displacement = dx
    else:
        displacement = [d.affine(c-a-target_fraction*v,
                        list(row)+[arb(0)]*(dimension-n))
                        for c, a, v, row in zip(target_center, anchor, dx,
                                                target_directions, strict=True)]
        state = [a+s*v+t*delta for a, v, delta in zip(anchor, dx, displacement, strict=True)]
    dual = [unit(dual_start+i) for i in range(reduced+1)]
    left, eta = [arb(0)]*offset, [arb(0)]*offset
    for j in range(reduced):
        left.append(sum((dual[i]*(R0[i, j]+s*(R1[i, j]-R0[i, j]))/weights[i]
                         for i in range(reduced+1)), d.affine(0)))
        eta.append(weights[j]*unit(eta_start+j) if variation
                   else p0[j]+s*(p1[j]-p0[j]))
    legs = [left, eta, displacement, displacement] if curvature else [left, eta, displacement]
    return dict(domain=d, state=state, legs=legs,
                bound_factor=arb(1)/8 if curvature else arb(1),
                line_parameter=s_index, path_parameter=t_index)
