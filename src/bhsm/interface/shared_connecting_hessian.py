"""Action-owned Hessian differences on shared star-shaped connecting domains.

This supplies an operator bound, not eigenbranch continuation. Physical tubes
and HS images must be included by the caller, and the nonlinear eigenpair
self-inclusion/branch-overlap proof remains a separate obligation.
"""
from flint import arb

from bhsm.interface.shared_action_taylor import Taylor, TaylorDomain
from bhsm.interface.shared_parameter_residual import validate_groups


def integrate_unit_parameter(value, parameter):
    """Integrate a uniform Taylor enclosure over t=(1+theta_parameter)/2.

    All other parameters stay fixed. The affine odd coefficient integrates to
    zero; the uniform remainder keeps its full bound. No tail is differentiated.
    """
    if not isinstance(value, Taylor):
        raise ValueError('a uniform shared Taylor enclosure is required')
    if (parameter, parameter + 1, 'interval') not in value.domain.groups:
        raise ValueError('integration requires a complete scalar interval group')
    coefficients = value.a.entries()
    coefficients[parameter] = arb(0)
    return value.domain.affine(value.c, coefficients, value.r)


def connecting_operands(anchor, center, directions, groups, preconditioner,
                        weights, eigenvector, offset, *, variation):
    """Construct D3S(xa+t*(x-xa))[R^T W^-1 dual, eta, x-xa].

    `directions` already contains the original domain radii. The target is
    center+directions*theta; its entire star with anchor is evaluated anew.
    The unit Euclidean dual ball covers every weighted output coordinate.
    eta is either the anchor eigenvector or the complete weighted input box.
    The Hessian uses raw action coordinates offset:STATE, as in the parent.
    """
    size = len(anchor)
    reduced = size - offset
    if (type(offset) is not int or not 0 <= offset < size
            or len(center) != size or len(directions) != size
            or len(eigenvector) != reduced or len(weights) != reduced + 1
            or len(preconditioner) != reduced + 1
            or any(len(row) != reduced + 1 for row in preconditioner)):
        raise ValueError('complete raw state and bordered reduced operands required')
    count = len(directions[0])
    if count < 1 or any(len(row) != count for row in directions):
        raise ValueError('matching nonempty target affine directions required')
    validate_groups(groups, count)
    operands = [*anchor, *center, *weights, *eigenvector,
                *(v for row in directions for v in row),
                *(v for row in preconditioner for v in row)]
    if any(not arb(v).is_finite() for v in operands):
        raise ValueError('finite operands required')
    if any(not arb(w) > 0 or not arb(w).rad().is_zero() for w in weights):
        raise ValueError('exact positive frozen eigenpair weights required')
    reach = count
    path = count + 1
    dual_start = count + 2
    eta_start = dual_start + reduced + 1
    dimension = eta_start + (reduced if variation else 0)
    new_groups = list(groups) + [(reach, reach + 1, 'interval'),
                                 (path, path + 1, 'interval'),
                                 (dual_start, eta_start, 'euclidean')]
    if variation:
        new_groups.append((eta_start, dimension, 'box'))
    domain = TaylorDomain(new_groups, dimension)
    t_coefficients = [arb(0)] * dimension
    t_coefficients[path] = arb(1) / 2
    t = domain.affine(arb(1) / 2, t_coefficients)
    s_coefficients = [arb(0)] * dimension
    s_coefficients[reach] = arb(1) / 2
    s = domain.affine(arb(1) / 2, s_coefficients)
    displacement = [domain.affine(arb(c) - arb(a),
                    [arb(v) for v in row] + [arb(0)] * (dimension - count))
                    for a, c, row in zip(anchor, center, directions, strict=True)]
    displacement = [s * dx for dx in displacement]
    state = [arb(a) + t * dx for a, dx in zip(anchor, displacement, strict=True)]
    left, eta = [arb(0)] * offset, [arb(0)] * offset
    for j in range(reduced):
        coefficients = [arb(0)] * dimension
        for i in range(reduced + 1):
            coefficients[dual_start + i] = arb(preconditioner[i][j]) / arb(weights[i])
        left.append(domain.affine(0, coefficients))
        if variation:
            coefficients = [arb(0)] * dimension
            coefficients[eta_start + j] = arb(weights[j])
            eta.append(domain.affine(0, coefficients))
        else:
            eta.append(domain.affine(eigenvector[j]))
    return dict(domain=domain, state=state, legs=[left, eta, displacement],
                integration_parameter=path, reach_parameter=reach,
                target_parameter_count=count,
                all_bordered_output_coordinates=True,
                input_kind='WEIGHTED_REDUCED_BOX' if variation else 'ANCHOR_EIGENVECTOR')


def enclose_difference(evaluate, operands):
    """Apply a caller-bound full action oracle and integrate its enclosure."""
    value, inertia_lower = evaluate(operands['state'], operands['legs'])
    if value.domain is not operands['domain']:
        raise ValueError('the action oracle changed the shared parameter domain')
    integrated = integrate_unit_parameter(value, operands['integration_parameter'])
    return dict(model=integrated, weighted_output_norm_upper=integrated.support(),
                inertia_lower=inertia_lower)
