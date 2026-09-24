"""Outward propagation of coordinate error through a stored midpoint tensor.

This concerns exact values of the supplied binary64 arrays, not their
physical construction or the rounding of a binary64 pullback evaluation.
"""
from __future__ import annotations

import math

import numpy as np
from flint import arb, ctx

PRECISION = 512


def _real_binary64(value, name):
    raw = np.asarray(value)
    if raw.dtype.kind not in "fiu" or raw.dtype.itemsize > 8:
        raise ValueError(f"{name} must contain real binary64-compatible numbers")
    result = np.asarray(raw, dtype=np.float64)
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must be finite")
    return result


def _squared_norm(values):
    # Converting each stored float directly to Arb is exact at 512 bits.
    # Accumulation and square roots use ball arithmetic, including underflow
    # and overflow ranges where binary64 norm formation would lose validity.
    total = arb(0)
    for value in values.flat:
        exact = arb(float(value))
        total += exact * exact
    return total


def _float_upper(value):
    if value.is_zero():
        return 0.0
    result = math.nextafter(float(value.upper()), math.inf)
    if not math.isfinite(result) or result < 0:
        raise RuntimeError("coordinate pullback bound is not finite in binary64")
    return result


def bound_coordinate_pullback_error(
    retained_retained,
    complement_retained,
    complement_complement,
    approximate_coordinates,
    coordinate_error_infinity_upper,
    output_map=None,
) -> dict:
    """Bound ``||L (X.T Q X - Xhat.T Q Xhat)||_F`` for all outputs.

    Requires a separately verified matrix row-sum bound
    ``||X-Xhat||_infinity <= coordinate_error_infinity_upper``. With n rows,
    ``e=sqrt(n)*epsilon`` bounds the Frobenius error. The tensor bound is
    ``||Q||_F (2 ||Xhat||_F e + e**2)``; an optional real output map adds
    the safe factor ``||L||_F``. Omitting L means the identity, factor one.
    The stored full tensor is [[UU, CU.T], [CU, CC]] in each output slice.
    Symmetrizing the pullback cannot increase the bound.

    This function does not verify the supplied epsilon or assert any
    physical Hessian, assembly-rounding, or final causal certificate.
    """
    uu, cu, cc, approximate = [
        _real_binary64(value, name) for value, name in (
            (retained_retained, "UU"), (complement_retained, "CU"),
            (complement_complement, "CC"),
            (approximate_coordinates, "approximate coordinates"),
        )
    ]
    epsilon_array = _real_binary64(coordinate_error_infinity_upper, "error bound")
    if epsilon_array.shape != () or float(epsilon_array) < 0:
        raise ValueError("error bound must be a nonnegative scalar")
    if uu.ndim != 3 or uu.shape[0] == 0 or uu.shape[1] == 0 or uu.shape[1] != uu.shape[2]:
        raise ValueError("UU must be nonempty and square per output")
    outputs, retained, _ = uu.shape
    complement = cc.shape[1] if cc.ndim == 3 else -1
    if (complement <= 0 or cc.shape != (outputs, complement, complement)
            or cu.shape != (outputs, complement, retained)
            or approximate.ndim != 2
            or approximate.shape[0] != retained + complement
            or approximate.shape[1] == 0):
        raise ValueError("incompatible full midpoint tensor and coordinate shapes")
    mapped = None if output_map is None else _real_binary64(output_map, "output map")
    if mapped is not None and (mapped.ndim != 2 or mapped.shape[0] == 0
                               or mapped.shape[1] != outputs):
        raise ValueError("output map has incompatible shape")

    previous = ctx.prec
    ctx.prec = PRECISION
    try:
        error = arb(approximate.shape[0]).sqrt() * arb(float(epsilon_array))
        coordinate_norm = _squared_norm(approximate).sqrt()
        tensor_norm = (_squared_norm(uu) + 2 * _squared_norm(cu)
                       + _squared_norm(cc)).sqrt()
        output_norm = arb(1) if mapped is None else _squared_norm(mapped).sqrt()
        bound = output_norm * tensor_norm * (2 * coordinate_norm * error + error * error)
        return {
            "scope": "COORDINATE_ERROR_THROUGH_EXACT_STORED_BINARY64_TENSOR_ONLY",
            "arithmetic_precision_bits": PRECISION,
            "coordinate_error_infinity_upper": float(epsilon_array),
            "coordinate_error_frobenius_upper": _float_upper(error),
            "approximate_coordinates_frobenius_upper": _float_upper(coordinate_norm),
            "full_stored_tensor_frobenius_upper": _float_upper(tensor_norm),
            "output_map_norm_factor_upper": _float_upper(output_norm),
            "pullback_coordinate_error_frobenius_upper": _float_upper(bound),
            "coordinate_bound_requires_external_verification": True,
            "physical_Hessian_rounding_enclosed": False,
            "pullback_assembly_rounding_enclosed": False,
            "Gate7_closed": False,
            "FULL_BHSM_COMPLETE": False,
        }
    finally:
        ctx.prec = previous
