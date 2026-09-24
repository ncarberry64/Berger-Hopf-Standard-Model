"""Restore a saved Arb ball exactly, or reject it; no tolerance is used.

Arb's public radius constructor may add one magnitude ulp. When necessary,
give it an interior half-ulp argument, then require the resulting midpoint
and radius to equal the saved rational values exactly. This changes neither
endpoint of the represented ball and is not certificate coarsening.
"""
from fractions import Fraction
from flint import arb


def restore_exact_ball(midpoint, radius):
    m, r = Fraction(midpoint), Fraction(radius)
    if r < 0 or any(v.denominator & (v.denominator-1) for v in (m, r)):
        raise ValueError('Finite dyadic midpoint and nonnegative dyadic radius required')
    mt = (m.numerator, 1-m.denominator.bit_length())
    value = arb(mt, (r.numerator, 1-r.denominator.bit_length()))
    if Fraction(str(value.rad().fmpq())) != r and r:
        if r.numerator.bit_length() > 30:
            raise ValueError('Saved radius is not an Arb magnitude')
        shift = max(1, 31-r.numerator.bit_length())
        value = arb(mt, ((r.numerator << shift)-1, 1-r.denominator.bit_length()-shift))
    if Fraction(str(value.mid().fmpq())) != m or Fraction(str(value.rad().fmpq())) != r:
        raise ArithmeticError('Exact ball restoration failed at current precision')
    return value
