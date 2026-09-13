"""Lower bounds on observed variation from two verified point enclosures."""
import numpy as np
from flint import arb
from bhsm.interface.affine_eigenpair_contraction import _balls


def difference_lower_bounds(first, second):
    """Return differences and lower bounds for their absolute values.

    Half a coordinate lower bound is necessary for any single interval radius
    covering both actual values. Samples give no uniform upper bound.
    """
    a, b = _balls(first), _balls(second)
    if a.shape != b.shape or not a.size:
        raise ValueError('matching nonempty verified point arrays required')
    difference = a-b
    lower = np.array([max(arb(0), abs(v).lower()) for v in difference.flat], dtype=object).reshape(a.shape)
    return difference, lower
