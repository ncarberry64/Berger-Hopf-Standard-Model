"""Comparison enclosures for scalar fixed-channel forward Weyl maps."""

from __future__ import annotations

import math


def _positive(value: float, name: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number <= 0.0:
        raise ValueError(f"finite positive {name} required")
    return number


def scalar_nonnegative_exterior_weyl_bounds(
    proper_duration_lower: float,
    potential_upper: float,
    negative_spectral_magnitude: float,
) -> dict[str, float]:
    """Bound the birth Weyl value through a certified nonnegative core.

    The channel is ``-u''+V u=-kappa^2 u`` with ``0<=V<=Vmax`` on a core
    of duration at least ``T``.  Weyl values use the action Green-form sign
    ``M=-u'(0)/u(0)`` at the birth boundary.  Any retained nonnegative
    *inward* terminal graph ``-u'(T)/u(T)>=0``, including the
    Friedrichs/Dirichlet limit, lies between the constant-zero Neumann and
    constant-``Vmax`` Dirichlet comparison graphs.
    """

    duration = _positive(proper_duration_lower, "proper duration")
    kappa2 = _positive(negative_spectral_magnitude, "negative spectral magnitude")
    vmax = float(potential_upper)
    if not math.isfinite(vmax) or vmax < 0.0:
        raise ValueError("finite nonnegative potential upper bound required")
    kappa = math.sqrt(kappa2)
    maximum_rate = math.sqrt(kappa2 + vmax)
    lower = kappa * math.tanh(kappa * duration)
    upper = maximum_rate / math.tanh(maximum_rate * duration)
    return {
        "lower": lower,
        "upper": upper,
        "width": upper - lower,
        "kappa": kappa,
        "maximum_rate": maximum_rate,
    }


def scalar_compact_radius_weyl_variation_bounds(
    weyl_upper: float,
    potential_upper: float,
    negative_spectral_magnitude: float,
    *,
    first_log_radius_bound: float = 1.0,
    second_log_radius_bound: float = 0.0,
) -> dict[str, float]:
    """Bound compact-support first/mixed Weyl radius variations.

    The directions obey ``||x_h||_infty,||x_k||_infty<=H`` and
    ``||x_hk||_infty<=L``.  For ``V=c exp(-2x)``, the multiplication jets
    satisfy ``||V_h||<=2 H Vmax`` and
    ``||V_hk||<=(4 H^2+2 L)Vmax``.  The coercive energy identity and
    ``||R_D(-kappa^2)||<=1/kappa^2`` then give the returned bounds.
    """

    m = _positive(weyl_upper, "Weyl upper bound")
    kappa2 = _positive(negative_spectral_magnitude, "negative spectral magnitude")
    vmax = float(potential_upper)
    h = float(first_log_radius_bound)
    ell = float(second_log_radius_bound)
    if any(not math.isfinite(value) or value < 0.0 for value in (vmax, h, ell)):
        raise ValueError("finite nonnegative variation data required")
    first_operator = 2.0 * h * vmax
    mixed_operator = (4.0 * h**2 + 2.0 * ell) * vmax
    poisson_l2_squared = m / kappa2
    first = first_operator * poisson_l2_squared
    mixed = (
        mixed_operator + 2.0 * first_operator**2 / kappa2
    ) * poisson_l2_squared
    return {
        "Poisson_L2_norm_squared_upper": poisson_l2_squared,
        "first_operator_bound": first_operator,
        "mixed_operator_bound": mixed_operator,
        "first_Weyl_variation_bound": first,
        "mixed_Weyl_variation_bound": mixed,
    }


__all__ = [
    "scalar_nonnegative_exterior_weyl_bounds",
    "scalar_compact_radius_weyl_variation_bounds",
]
