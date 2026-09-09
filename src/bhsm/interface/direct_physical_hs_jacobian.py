"""Outward chain rule at the actual physical Hermite–Simpson midpoint."""
import numpy as np
from flint import arb, arb_mat, ctx


def _matrix(values):
    if isinstance(values, arb_mat):
        if not values.nrows() or not values.ncols() or not all(v.is_finite() for v in values.entries()):
            raise ValueError('finite nonempty matrix required')
        return arb_mat(values.nrows(), values.ncols(), values.entries())
    array = np.asarray(values, dtype=object)
    if array.ndim != 2 or not all(array.shape):
        raise ValueError('nonempty matrix required')
    result = arb_mat(*array.shape, [arb(v) for v in array.flat])
    if not all(v.is_finite() for v in result.entries()):
        raise ValueError('finite matrix required')
    return result


def physical_hs_blocks(left_df, midpoint_df, right_df, step, *, precision=512):
    """Return DM/Dz0, DM/Dz1, Dr/Dz0, Dr/Dz1 as Arb matrices.

    The caller must certify each DF at the matching physical endpoint or
    actual HS midpoint. These algebraic operations do not certify their
    input derivatives, physical branch continuation, or quotient frames.
    The residual convention is r = z1-z0-h*(f0+4*fm+f1)/6.
    """
    if type(precision) is not int or precision < 64:
        raise ValueError('at least 64 bits of arithmetic precision required')
    previous = ctx.prec
    ctx.prec = precision
    try:
        a, m, b = [_matrix(v) for v in (left_df, midpoint_df, right_df)]
        n = a.nrows()
        if any(v.nrows() != n or v.ncols() != n for v in (a, m, b)):
            raise ValueError('matching square derivative matrices required')
        h = arb(step)
        if not h.is_finite() or not h.rad().is_zero() or not h > 0:
            raise ValueError('positive exact step required')
        identity = arb_mat(np.eye(n, dtype=int).tolist())
        ml = identity/2+a*(h/8)
        mr = identity/2-b*(h/8)
        rl = -identity-a*(h/6)-(m*ml)*(2*h/3)
        rr = identity-b*(h/6)-(m*mr)*(2*h/3)
        matrices = dict(midpoint_left=ml, midpoint_right=mr,
                        residual_left=rl, residual_right=rr)
        if not all(v.is_finite() for matrix in matrices.values() for v in matrix.entries()):
            raise ArithmeticError('nonfinite physical HS chain rule result')
        return matrices
    finally:
        ctx.prec = previous


def fixed_frame_pullback(residual_block, trial, test, right, *, precision=512):
    """Enclose R^-1 T Dr E for caller-supplied fixed finite frames and R.

    This does not assert that the frames are an intrinsic physical quotient,
    or that R is the physical right Jacobian block. It is a fixed algebraic
    pullback. The sign used by any subsequent Newton map remains its caller's
    responsibility.
    """
    if type(precision) is not int or precision < 64:
        raise ValueError('at least 64 bits of arithmetic precision required')
    previous = ctx.prec
    ctx.prec = precision
    try:
        d, e, t, r = [_matrix(v) for v in (residual_block, trial, test, right)]
        if (d.nrows() != d.ncols() or e.nrows() != d.ncols()
                or t.ncols() != d.nrows() or r.nrows() != r.ncols()
                or r.nrows() != t.nrows()):
            raise ValueError('compatible derivative, trial, test and right matrices required')
        try:
            result = r.solve(t*d*e)
        except (ValueError, ZeroDivisionError) as error:
            raise ArithmeticError('fixed right block solve unresolved') from error
        if not all(v.is_finite() for v in result.entries()):
            raise ArithmeticError('nonfinite fixed right block solve')
        return result
    finally:
        ctx.prec = previous
