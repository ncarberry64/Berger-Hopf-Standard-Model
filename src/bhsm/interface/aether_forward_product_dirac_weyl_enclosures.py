"""Relative-form enclosures for factorized product-Dirac Weyl channels."""

from __future__ import annotations

import math


def _positive(value: float, name: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number <= 0.0:
        raise ValueError(f"finite positive {name} required")
    return number


def product_dirac_nonnegative_exterior_weyl_bounds(
    proper_duration_lower: float,
    superpotential_absolute_upper: float,
    negative_spectral_magnitude: float,
) -> dict[str, float]:
    """Bound a factorized channel without differentiating its superpotential.

    The channel form is ``||A u||^2`` for ``A=d_tau+s`` and the resolvent
    probe adds ``kappa^2||u||^2``.  At birth, ``M=-A u(0)/u(0)``.  The
    retained future has a nonnegative inward graph.  Positivity gives the
    lower bound zero.  The piecewise-linear Dirichlet trial
    ``u=1-tau/T`` on the certified core gives the upper bound while using
    only ``|s|<=S``; no derivative of ``s`` is introduced.
    """

    duration = _positive(proper_duration_lower, "proper duration")
    kappa2 = _positive(negative_spectral_magnitude, "negative spectral magnitude")
    superpotential = float(superpotential_absolute_upper)
    if not math.isfinite(superpotential) or superpotential < 0.0:
        raise ValueError("finite nonnegative superpotential bound required")
    upper = (
        1.0 / duration
        + superpotential
        + (superpotential**2 + kappa2) * duration / 3.0
    )
    return {
        "lower": 0.0,
        "upper": upper,
        "width": upper,
        "trial_derivative_energy": 1.0 / duration,
        "trial_cross_bound": superpotential,
        "trial_potential_and_probe_bound": (
            (superpotential**2 + kappa2) * duration / 3.0
        ),
    }


def product_dirac_compact_radius_weyl_variation_bounds(
    weyl_upper: float,
    superpotential_absolute_upper: float,
    negative_spectral_magnitude: float,
    *,
    first_log_radius_bound: float = 1.0,
    second_log_radius_bound: float = 0.0,
) -> dict[str, float]:
    """Bound compact-support Weyl jets directly in the factorized form.

    For ``s=lambda*exp(-x)``, ``|s_h|<=S H`` and
    ``|s_hk|<=S(H^2+L)``.  The coercive energy norm controls both
    ``||A u||`` and ``kappa||u||``.  The mixed bound includes the direct
    mixed form jet and both Dirichlet-resolvent pair contractions.
    """

    m = _positive(weyl_upper, "Weyl upper bound")
    kappa2 = _positive(negative_spectral_magnitude, "negative spectral magnitude")
    superpotential = float(superpotential_absolute_upper)
    h = float(first_log_radius_bound)
    ell = float(second_log_radius_bound)
    if any(
        not math.isfinite(value) or value < 0.0
        for value in (superpotential, h, ell)
    ):
        raise ValueError("finite nonnegative variation data required")
    kappa = math.sqrt(kappa2)
    first = 2.0 * superpotential * h * m / kappa
    direct_mixed = m * (
        2.0 * superpotential**2 * h**2 / kappa2
        + 2.0 * superpotential * (h**2 + ell) / kappa
    )
    resolvent_pair = 8.0 * superpotential**2 * h**2 * m / kappa2
    return {
        "Poisson_L2_norm_squared_upper": m / kappa2,
        "Poisson_A_norm_squared_upper": m,
        "first_Weyl_variation_bound": first,
        "direct_mixed_form_bound": direct_mixed,
        "two_resolvent_pair_bound": resolvent_pair,
        "mixed_Weyl_variation_bound": direct_mixed + resolvent_pair,
    }


__all__ = [
    "product_dirac_nonnegative_exterior_weyl_bounds",
    "product_dirac_compact_radius_weyl_variation_bounds",
]
