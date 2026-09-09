"""Enclose frozen causal-map construction and its global perturbation gain."""
import numpy as np
from flint import arb, arb_mat, ctx

from bhsm.interface import current_green_causal_error as causal
from bhsm.interface.current_green_midpoint_coordinate_error import (
    PRECISION, _float_upper, _real_binary64,
)
from bhsm.interface.resolved_midpoint_coordinate_error import (
    _exact_matrix, _operator_norm_upper,
)


def bound_frozen_map_error(right, test, left, trial, approximate):
    """Bound -R^-1 (T L V)-P for exact supplied binary64 operands.

    This encloses inverse, product, and solve rounding relative to the frozen
    inverse used by the accepted replay. It does not enclose physical errors
    in R, T, L, or V, and does not redefine the preconditioner as P.
    """
    r, t, l, v, p = [_real_binary64(value, name) for name, value in (
        ('right', right), ('test', test), ('left', left),
        ('trial', trial), ('approximate map', approximate))]
    if any(x.ndim != 2 or min(x.shape) == 0 for x in (r, t, l, v, p)):
        raise ValueError('Nonempty matrix operands required')
    dimension = r.shape[0]
    if (r.shape != (dimension, dimension) or p.shape != r.shape
            or t.shape[0] != dimension or t.shape[1] != l.shape[0]
            or l.shape[1] != v.shape[0] or v.shape[1] != dimension):
        raise ValueError('Compatible frozen causal-map operands required')
    previous = ctx.prec
    ctx.prec = PRECISION
    try:
        matrix = _exact_matrix(r)
        inverse = matrix.inv()
        identity = arb_mat(np.eye(dimension, dtype=int).tolist())
        residual = identity - matrix * inverse
        residual_upper = max(sum(abs(residual[i,j]) for j in range(dimension)).upper()
                             for i in range(dimension))
        if not (residual_upper.is_finite() and residual_upper < 1):
            raise RuntimeError('Frozen inverse could not be certified')
        target = -inverse * (_exact_matrix(t) * _exact_matrix(l) * _exact_matrix(v))
        error = target - _exact_matrix(p)
        if not all(error[i,j].is_finite() for i in range(dimension) for j in range(dimension)):
            raise RuntimeError('Map error enclosure is not finite')
        frobenius = sum(abs(error[i,j]).upper()**2
                        for i in range(dimension) for j in range(dimension)).sqrt().upper()
        return dict(
            scope='EXACT_STORED_FROZEN_INVERSE_MAP_CONSTRUCTION_ONLY',
            arithmetic_precision_bits=PRECISION,
            inverse_residual_infinity_upper=_float_upper(residual_upper),
            map_operator_error_upper=_float_upper(_operator_norm_upper(error, frobenius)),
            map_frobenius_error_upper=_float_upper(frobenius),
            physical_operand_errors_enclosed=False,
        )
    finally:
        ctx.prec = previous


def transport_map_perturbations(maps, map_error_bounds, block_size=10):
    """Bound the map perturbation in the node block-sup Euclidean norm.

    Let G propagate source errors through P and E=G DeltaP act on states
    with z[0]=0. If ||E||<=k<1, exact frozen-map solutions obey
      ||z_star-z|| <= (k ||z|| + ||G Deltaf||)/(1-k).
    Thus all existing source-error bounds can be lifted with the reported
    source multiplier; the map/source cross term is included automatically.
    Bounds on z and G Deltaf remain obligations of the caller.
    """
    p = _real_binary64(maps, 'maps')
    errors = _real_binary64(map_error_bounds, 'map error bounds')
    if (p.ndim != 3 or min(p.shape) == 0 or p.shape[1] != p.shape[2]
            or errors.shape != (p.shape[0],) or np.any(errors < 0)):
        raise ValueError('Square maps and matching nonnegative bounds required')
    errors = errors.copy()
    errors[0] = 0.0  # The initial state is fixed at zero, including its error.
    result = causal.transport_local_errors(p, errors, block_size)
    k = result['maximum_node_error_norm_upper']
    previous = ctx.prec
    ctx.prec = PRECISION
    try:
        passed = k < 1.0
        source = (1.0 if k == 0.0 else _float_upper(1/(1-arb(k)))) if passed else None
        relative = _float_upper(arb(k)/(1-arb(k))) if passed else None
    finally:
        ctx.prec = previous
    return dict(
        scope='FROZEN_MAP_PERTURBATION_FOR_ZERO_INITIAL_STATE',
        transport=result, perturbation_gain_upper=k,
        status='PERTURBATION_GAIN_BELOW_ONE' if passed else 'GAIN_BOUND_INCONCLUSIVE',
        source_error_multiplier_upper=source,
        relative_stored_response_error_multiplier_upper=relative,
        source_and_stored_response_bounds_require_external_verification=True,
        physical_operand_errors_enclosed=False,
        physical_Hessian_error_enclosed=False,
        output_map_construction_rounding_enclosed=False,
        neighborhood_remainder_enclosed=False,
        Gate7_closed=False, FULL_BHSM_COMPLETE=False,
    )
