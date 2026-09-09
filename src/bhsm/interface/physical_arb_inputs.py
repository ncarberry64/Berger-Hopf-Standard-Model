"""Preserve interval state/direction operands in physical derivative graphs."""
import numpy as np
from flint import arb


def preserve_ball(value):
    """Copy an Arb ball or lift an exact integer/binary64 without narrowing."""
    if isinstance(value, arb):
        result = arb(value)
    elif isinstance(value, (int, np.integer)) and not isinstance(value, (bool, np.bool_)):
        result = arb(int(value))
    elif isinstance(value, (float, np.floating)):
        if isinstance(value, np.floating) and value.dtype.itemsize > 8:
            raise ValueError('wider floating operands need an explicit exact conversion')
        result = arb(float(value))
    else:
        raise ValueError('finite Arb, integer or binary64 operand required')
    if not result.is_finite():
        raise ValueError('finite physical operand required')
    return result


def same_ball_vector(left, right):
    """Compare represented balls, not the uncertain equality of their values."""
    a, b = np.asarray(left, dtype=object), np.asarray(right, dtype=object)
    if a.ndim != 1 or a.shape != b.shape:
        return False
    for x, y in zip(a, b, strict=True):
        x, y = preserve_ball(x), preserve_ball(y)
        if x.mid() != y.mid() or x.rad() != y.rad():
            return False
    return True
