"""Sufficient source-weighted spectral criteria for the retained E1 force."""

from __future__ import annotations

import math


def e1_source_measure_dyadic_bound(
    low_energy_constant: float,
    low_energy_excess_exponent: float,
    high_energy_weighted_tail: float,
) -> dict[str, float]:
    """Bound the normalized-heat-length first E1 variation.

    Let ``nu`` be the total-variation measure of the source-weighted graded
    spectral contraction and suppose

    ``|nu|([0,Lambda]) <= C Lambda^(1+epsilon)`` for ``0<Lambda<=1``.

    If ``H=int_[1,infinity] exp(-lambda)/lambda d|nu|`` is finite, dyadic
    summation bounds ``int exp(-lambda)/lambda d|nu|``.  The returned force
    includes the retained factor one half.
    """

    c = float(low_energy_constant)
    epsilon = float(low_energy_excess_exponent)
    high = float(high_energy_weighted_tail)
    if any(not math.isfinite(value) for value in (c, epsilon, high)):
        raise ValueError("finite source-measure data required")
    if c < 0.0 or epsilon <= 0.0 or high < 0.0:
        raise ValueError("C,H nonnegative and epsilon positive required")
    low = 2.0 * c / (1.0 - 2.0 ** (-epsilon))
    return {
        "low_energy_integral_upper": low,
        "high_energy_integral_upper": high,
        "first_E1_variation_absolute_upper": 0.5 * (low + high),
    }


__all__ = ["e1_source_measure_dyadic_bound"]
