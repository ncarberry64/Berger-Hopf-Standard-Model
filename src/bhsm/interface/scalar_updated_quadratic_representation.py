"""Reuse certified unchanged-output rounding after a scalar-only update."""
import math

import numpy as np
from flint import arb, ctx

from bhsm.interface import symmetric_quadratic_center as original


def certify_scalar_update(raw, corrected, raw_projection_error_upper):
    """Enclose the full updated representation without rechecking old outputs.

    If E bounds the full raw representation error and e bounds the new scalar
    representation error, sqrt(E**2+e**2) bounds the updated tensor error.
    The unchanged field error is <=E; this deliberately retains the old scalar
    contribution in E rather than subtracting an uncertified lower bound.
    The caller must verify E's certificate and its binding to raw.
    """
    raw, corrected = np.asarray(raw), np.asarray(corrected)
    represented = original.symmetric_center(corrected)
    if (raw.dtype != np.dtype('float64') or raw.shape != corrected.shape
            or not np.all(np.isfinite(raw))
            or not np.array_equal(raw[:-1], corrected[:-1])):
        raise ValueError('Only the last scalar output may change')
    bound = np.asarray(raw_projection_error_upper)
    if (bound.shape != () or bound.dtype.kind not in 'fiu'
            or not np.isfinite(float(bound)) or float(bound) < 0):
        raise ValueError('A finite nonnegative certified raw bound is required')
    _, scalar = original.certify_representation(corrected[-1:])
    previous = ctx.prec
    ctx.prec = original.PRECISION
    try:
        scale = float(np.max(np.abs(corrected)))
        error = (arb(float(bound))**2
                 + arb(scalar['projection_rounding_Frobenius_upper'])**2).sqrt()
        # A zero updated tensor has an exactly zero representation error,
        # including when a formerly nonzero scalar output was cancelled.
        if scale == 0:
            error = arb(0)

        def upper(value):
            if value.is_zero():
                return 0.
            result = math.nextafter(float(value.upper()), math.inf)
            if not math.isfinite(result) or result < 0:
                raise RuntimeError('Updated representation bound is not finite')
            return result

        return represented, dict(
            arithmetic_precision_bits=original.PRECISION,
            projection_rounding_Frobenius_upper=upper(error),
            projection_rounding_relative_to_maximum_entry_upper=upper(error/arb(scale)) if scale else 0.,
            maximum_raw_entry_absolute=scale,
            represented_tensor_exactly_symmetric=True,
            scope='REPRESENTATION_OF_STORED_QUADRATIC_FORM_ONLY',
            projection_error_method='REUSED_RAW_BOUND_PLUS_UPDATED_SCALAR_IN_QUADRATURE',
            reused_raw_projection_rounding_Frobenius_upper=float(bound),
            updated_scalar_projection_rounding_Frobenius_upper=scalar['projection_rounding_Frobenius_upper'],
            raw_bound_requires_external_verification=True,
            physical_Hessian_error_enclosed=False, FULL_BHSM_COMPLETE=False,
        )
    finally:
        ctx.prec = previous
