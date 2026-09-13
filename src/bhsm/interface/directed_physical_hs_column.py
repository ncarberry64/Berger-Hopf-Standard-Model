"""Fixed-frame HS chain rule from complete directional physical variations."""
import numpy as np
from flint import arb, arb_mat
from bhsm.interface.direct_physical_hs_jacobian import _matrix


def _step(step):
    h = arb(step)
    if not h.is_finite() or not h.rad().is_zero() or not h > 0:
        raise ValueError('positive exact step required')
    return h


def chain_direction(trial, endpoint_action, step, side):
    """Enclose DM/Dz_side applied to one fixed trial column."""
    e, a = _matrix(trial), _matrix(endpoint_action)
    if side not in ('left', 'right') or e.ncols() != 1 or (e.nrows(), 1) != (a.nrows(), a.ncols()):
        raise ValueError('matching single columns and explicit endpoint side required')
    h = _step(step)
    return e/2 + a*(h/8 if side == 'left' else -h/8)


def local_column(trial, endpoint_action, midpoint_action, step, test,
                 frozen_left, frozen_right, column, side):
    """Return equivalent associations of DL_j or DR_j; caller certifies inputs.

    Midpoint_action must enclose DF(M) applied to chain_direction(trial,
    endpoint_action, step, side) on the matching actual midpoint domain.
    No state-dependent frame derivative or physical quotient is asserted.
    """
    e, a, b, t, l, r = map(_matrix, (trial, endpoint_action, midpoint_action,
                                     test, frozen_left, frozen_right))
    n, k = e.nrows(), r.nrows()
    if (side not in ('left', 'right') or type(column) is not int or not 0 <= column < k
            or any((x.nrows(), x.ncols()) != (n, 1) for x in (e, a, b))
            or (l.nrows(), l.ncols()) != (n, n)
            or (t.nrows(), t.ncols()) != (k, n) or r.ncols() != k):
        raise ValueError('compatible fixed-frame single-column operands required')
    h = _step(step)
    p = r.solve(t)
    identity = arb_mat(np.eye(n, dtype=int).tolist())
    if side == 'left':
        fixed = (l+identity)*e
        combined = p*(fixed+a*(h/6)+b*(2*h/3))
        separated = p*fixed+(p*a)*(h/6)+(p*b)*(2*h/3)
    else:
        unit = arb_mat(k, 1, [arb(i == column) for i in range(k)])
        combined = unit+p*(-e+a*(h/6)+b*(2*h/3))
        separated = unit-p*e+(p*a)*(h/6)+(p*b)*(2*h/3)
    return dict(combined=combined, separated=separated)
