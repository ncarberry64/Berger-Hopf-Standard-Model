"""Directional eigenvalue slopes of the normalized retained symmetric family."""
import numpy as np
from flint import arb
from bhsm.interface.affine_eigenpair_contraction import _balls


def eigenvalue_slopes(action, state, psi, raw_directions, maps):
    """Return D3S[psi,psi,v]; the caller proves the normalized eigenpair family.

    The action Hessian acts on the final len(psi) state coordinates. This
    uses the actual eigenvalue derivative, never an auxiliary solve border.
    """
    x, p, v = map(_balls, (state, psi, raw_directions))
    if (x.ndim != 1 or p.ndim != 1 or not 0 < p.size < x.size
            or v.ndim != 2 or v.shape[0] != x.size or not v.shape[1]):
        raise ValueError('complete state, reduced eigenvector and directions required')
    raw_p = np.concatenate((np.full(x.size-p.size, arb(0)), p))
    slopes = np.asarray(action(x, [raw_p[:, None, None], raw_p[:, None, None],
                                   v[:, None, :]], maps), dtype=object)
    if slopes.shape != (1, v.shape[1]) or not all(a.is_finite() for a in slopes.flat):
        raise ArithmeticError('complete finite scalar eigenvalue slopes required')
    return slopes[0]
