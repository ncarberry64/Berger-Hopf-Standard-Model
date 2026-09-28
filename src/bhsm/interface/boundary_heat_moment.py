"""Positive fixed-channel boundary heat moments from a current collar.

This controls the FULL-domain birth spectral measure with an explicit
nonnegative exterior graph, not the heat spectrum of a cut-off collar.
Grading and joint contact/transport are composed by the caller.
"""
from flint import arb


def collar_weyl_upper(*, duration, coefficient_upper, spectral_shift,
                     channel):
    """Energy of the linear Dirichlet trial, extended by zero past the collar.

    Scalar coefficient is sup V>=0. Product-Dirac coefficient is sup |W|;
    the factorized form ||u'+W*u||^2 is used without a derivative of W.
    The complete retained exterior has nonnegative form and is not zeroed.
    """
    T, c, u = map(arb, (duration, coefficient_upper, spectral_shift))
    if not T > 0 or not c >= 0 or not u > 0:
        raise ValueError('positive current duration/shift and nonnegative coefficient required')
    # Use an exact subcollar length; lower duration endpoints are sufficient.
    t = T.lower()
    if channel == 'scalar':
        return 1/t+(c+u)*t/3
    if channel == 'product_Dirac':
        return 1/t+c+(c*c+u)*t/3
    raise ValueError('owned scalar or factorized product-Dirac channel required')


def boundary_heat_moment_upper(*, weyl_shift_upper, weyl_zero_lower,
                               heat_length, spectral_shift):
    """Bound H=1/2 integral exp(-ell^2 lambda)/lambda d rho(lambda).

    W(u)-W(0)=u integral d rho/[lambda*(lambda+u)], with W(u)=M(-u).
    For u>=1/ell^2, exp(-ell^2 lambda)<=u/(lambda+u).
    Hence 0<=H<=(W(u)-W(0))/2, including continuous spectrum at zero.
    These must be bounds on the same full-domain Weyl function. Independent
    valid upper/lower enclosures may lose correlation but remain rigorous.
    """
    hi, lo, ell, u = map(arb, (weyl_shift_upper, weyl_zero_lower, heat_length, spectral_shift))
    if not ell > 0 or not u > 0 or not u*ell*ell >= 1:
        raise ValueError('positive shift with u*ell^2>=1 required')
    if not lo >= 0 or not hi >= lo:
        raise ValueError('ordered nonnegative full-domain Weyl bounds required')
    return (hi-lo)/2
