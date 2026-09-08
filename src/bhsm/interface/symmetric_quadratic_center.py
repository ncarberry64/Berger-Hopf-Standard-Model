"""Represent a stored real quadratic form by its unique symmetric matrix.

This is an algebraic representation certificate, not an error estimate for
the action Hessian that produced the stored array.
"""
import math
import numpy as np
from flint import arb, ctx

PRECISION = 512


def symmetric_center(raw):
    """Return a symmetric binary64 approximation to (Q+Q.T)/2 per output."""
    raw = np.asarray(raw)
    if (raw.dtype != np.dtype('float64') or raw.ndim != 3
            or not all(raw.shape) or raw.shape[1] != raw.shape[2]
            or not np.all(np.isfinite(raw))):
        raise ValueError('finite nonempty real binary64 square tensor required')
    transpose = raw.transpose(0, 2, 1)
    # Halve before adding to avoid overflow. Preserve equal entries exactly,
    # including diagonal subnormals that separate halving would underflow.
    result = np.where(raw == transpose, raw, raw * .5 + transpose * .5)
    if not np.array_equal(result, result.transpose(0, 2, 1)):
        raise RuntimeError('symmetric representation is not exactly symmetric')
    return result


def certify_representation(raw):
    """Enclose ||Qhat_sym - exact sym(Q)||_F using actual dyadic operands.

    No floating-point rounding model is used to estimate this error. Arb
    encloses the exact average-minus-stored-result for every unequal pair.
    The returned relative bound uses max|Q_ijk|, a conservative lower bound
    on ||Q||_F. It does not bound ||Q-H_physical|| or any causal accumulation.
    """
    raw = np.asarray(raw)
    result = symmetric_center(raw)
    previous = ctx.prec
    ctx.prec = PRECISION
    try:
        square = arb(0)
        for output in range(raw.shape[0]):
            for i in range(raw.shape[1]):
                for j in range(i + 1, raw.shape[2]):
                    a, b = float(raw[output, i, j]), float(raw[output, j, i])
                    if a == b:
                        continue
                    exact = (arb(a) + arb(b)) / 2
                    error = arb(float(result[output, i, j])) - exact
                    square += 2 * abs(error).upper() ** 2
        norm = square.sqrt()
        scale = float(np.max(np.abs(raw)))
        relative = norm / arb(scale) if scale else arb(0)

        def upper(value):
            if value.is_zero():
                return 0.
            bound = math.nextafter(float(value.upper()), math.inf)
            if not math.isfinite(bound) or bound < 0:
                raise RuntimeError('representation bound is not finite in binary64')
            return bound

        return result, {
            'arithmetic_precision_bits': PRECISION,
            'projection_rounding_Frobenius_upper': upper(norm),
            'projection_rounding_relative_to_maximum_entry_upper': upper(relative),
            'maximum_raw_entry_absolute': scale,
            'represented_tensor_exactly_symmetric': True,
            'scope': 'REPRESENTATION_OF_STORED_QUADRATIC_FORM_ONLY',
            'physical_Hessian_error_enclosed': False,
            'FULL_BHSM_COMPLETE': False,
        }
    finally:
        ctx.prec = previous
