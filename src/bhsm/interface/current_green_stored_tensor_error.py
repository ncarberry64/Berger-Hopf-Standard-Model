"""Transport stored tensor-rounding bounds through exact stored maps."""
from __future__ import annotations

import numpy as np
from flint import arb, ctx

from bhsm.interface.current_green_midpoint_coordinate_error import (
    PRECISION, _float_upper, _real_binary64, _squared_norm,
)


def _matrix_norm_upper(matrix):
    """Use the smaller of Frobenius and sqrt(one-norm * infinity-norm)."""
    absolute = [[abs(arb(float(x))) for x in row] for row in matrix]
    infinity = max(sum(row).upper() for row in absolute)
    one = max(sum(row[j] for row in absolute).upper()
              for j in range(matrix.shape[1]))
    return min(_squared_norm(matrix).sqrt().upper(), (one * infinity).sqrt().upper())


def bound_stored_tensor_error(output_map, input_map, tensor_error_frobenius_upper,
                             scalar_addition_error_frobenius_upper=0.,
                             scalar_output=-1):
    """Bound the error in L (M.T Q M), retaining the scalar error's output.

For a full tensor error E and an additional error A confined to output s,
the Frobenius bound is
``||M||_2**2 * (||L||_2 ||E||_F + ||L[:,s]||_2 ||A||_F)``.
Every supplied binary64 map is treated as exact. The caller must supply
valid local error bounds. This does not bound construction of the maps,
evaluation of the adjoint correction, or pullback assembly arithmetic.
"""
    left = _real_binary64(output_map, 'output map')
    right = _real_binary64(input_map, 'input map')
    if any(value.ndim != 2 or min(value.shape) == 0 for value in (left, right)):
        raise ValueError('nonempty matrix maps required')
    if not isinstance(scalar_output, (int, np.integer)) or not -left.shape[1] <= scalar_output < left.shape[1]:
        raise ValueError('scalar output outside the output map')
    errors = [_real_binary64(value, 'local error bound') for value in
              (tensor_error_frobenius_upper, scalar_addition_error_frobenius_upper)]
    if any(value.shape != () or float(value) < 0 for value in errors):
        raise ValueError('nonnegative scalar error bounds required')
    previous = ctx.prec
    ctx.prec = PRECISION
    try:
        input_norm = _matrix_norm_upper(right)
        output_norm = _matrix_norm_upper(left)
        scalar_column_norm = _squared_norm(left[:, scalar_output]).sqrt().upper()
        tensor_part = input_norm**2 * output_norm * arb(float(errors[0]))
        scalar_part = input_norm**2 * scalar_column_norm * arb(float(errors[1]))
        return dict(
            scope='LOCAL_STORED_ROUNDING_THROUGH_EXACT_STORED_MAPS_ONLY',
            arithmetic_precision_bits=PRECISION,
            input_operator_norm_upper=_float_upper(input_norm),
            output_operator_norm_upper=_float_upper(output_norm),
            scalar_output_column_norm_upper=_float_upper(scalar_column_norm),
            mapped_tensor_error_frobenius_upper=_float_upper(tensor_part),
            mapped_scalar_addition_error_frobenius_upper=_float_upper(scalar_part),
            mapped_total_error_frobenius_upper=_float_upper(tensor_part + scalar_part),
            local_error_bounds_require_external_verification=True,
            physical_Hessian_error_enclosed=False,
            map_construction_rounding_enclosed=False,
            pullback_assembly_rounding_enclosed=False,
            causal_rounding_enclosed=False,
            Gate7_closed=False, FULL_BHSM_COMPLETE=False,
        )
    finally:
        ctx.prec = previous
