"""Outward second chain rule for the existing physical Hermite-Simpson map."""
from flint import arb, ctx
from bhsm.interface.direct_physical_hs_jacobian import _matrix


def physical_hs_second_residual(left_second, midpoint_second_rate, right_second,
                                midpoint_df, step, *, precision=512):
    """Enclose D2M and D2r on caller-supplied pairs of endpoint directions.

    Columns are corresponding bilinear contractions H0[u0,v0],
    HM[DM*u,DM*v], H1[u1,v1]. These are rate Hessians, not residual Hessians.
    HM and DF must refer to the same actual HS midpoint. This algebra does
    not certify the Hessians, their evaluation points or the input directions.
    """
    if type(precision) is not int or precision < 64:
        raise ValueError('at least 64 bits of arithmetic precision required')
    previous = ctx.prec; ctx.prec = precision
    try:
        left, middle, right, df = map(_matrix,
            (left_second, midpoint_second_rate, right_second, midpoint_df))
        n, count = left.nrows(), left.ncols()
        if (any(m.nrows() != n or m.ncols() != count for m in (middle, right))
                or df.nrows() != n or df.ncols() != n):
            raise ValueError('matching rate contractions and square midpoint derivative required')
        h = arb(step)
        if not h.is_finite() or not h.rad().is_zero() or not h > 0:
            raise ValueError('positive exact step required')
        midpoint = (left-right)*(h/8)
        residual = -(left+4*middle+right)*(h/6)-(df*midpoint)*(2*h/3)
        if not all(v.is_finite() for m in (midpoint,residual) for v in m.entries()):
            raise ArithmeticError('nonfinite physical HS second chain rule')
        return dict(midpoint_second=midpoint, residual_second=residual)
    finally:
        ctx.prec = previous


def frozen_newton_quadratic_source(residual_second, test, frozen_right, *, precision=512):
    """Enclose -R^-1 T D2r/2 for fixed frames and the unchanged frozen inverse.

    The factor 1/2 belongs to the Taylor quadratic form. Its mixed two-radius
    term still has factor 2. No state-dependent frame derivative is supplied
    or silently set to zero; the scope here is a fixed-frame operator only.
    """
    if type(precision) is not int or precision < 64:
        raise ValueError('at least 64 bits of arithmetic precision required')
    previous = ctx.prec; ctx.prec = precision
    try:
        second, t, r = map(_matrix, (residual_second, test, frozen_right))
        if (t.ncols() != second.nrows() or r.nrows() != r.ncols()
                or r.nrows() != t.nrows()):
            raise ValueError('compatible second derivative, test frame and frozen right block required')
        try:
            source = -r.solve(t*second)/2
        except (ValueError, ZeroDivisionError) as error:
            raise ArithmeticError('fixed quadratic-source solve unresolved') from error
        if not all(v.is_finite() for v in source.entries()):
            raise ArithmeticError('nonfinite fixed quadratic-source solve')
        return source
    finally:
        ctx.prec = previous
