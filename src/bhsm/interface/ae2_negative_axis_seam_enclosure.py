"""Parametric negative-axis AE2 child-load comparison bounds."""

from __future__ import annotations

import math

from bhsm.interface.aether_forward_product_dirac_weyl_enclosures import (
    product_dirac_compact_radius_weyl_variation_bounds,
)
from bhsm.interface.aether_forward_scalar_weyl_enclosures import (
    scalar_compact_radius_weyl_variation_bounds,
    scalar_nonnegative_exterior_weyl_bounds,
)


def optimized_product_dirac_negative_axis_bounds(
    proper_duration_lower: float,
    superpotential_absolute_upper: float,
    kappa_squared: float,
) -> dict[str, float]:
    """Optimize the factorized Dirichlet trial inside the certified core.

    For every ``0<L<=T`` the zero-extended trial ``u=1-t/L`` gives

    ``M<=1/L+S+(S^2+kappa^2)L/3``.

    The unconstrained optimum is ``sqrt(3/(S^2+kappa^2))``.  Truncating it
    at the certified core duration retains validity and improves the old
    fixed-length estimate from ``O(kappa^2)`` to ``O(kappa)`` at high probe.
    """

    duration = float(proper_duration_lower)
    superpotential = float(superpotential_absolute_upper)
    kappa2 = float(kappa_squared)
    if not math.isfinite(duration) or duration <= 0.0:
        raise ValueError("positive finite proper duration required")
    if not math.isfinite(superpotential) or superpotential < 0.0:
        raise ValueError("finite nonnegative superpotential bound required")
    if not math.isfinite(kappa2) or kappa2 <= 0.0:
        raise ValueError("positive finite kappa squared required")
    rate2 = superpotential**2 + kappa2
    unconstrained = math.sqrt(3.0 / rate2)
    trial_length = min(duration, unconstrained)
    upper = (
        1.0 / trial_length
        + superpotential
        + rate2 * trial_length / 3.0
    )
    return {
        "lower": 0.0,
        "upper": upper,
        "trial_length": trial_length,
        "unconstrained_optimal_length": unconstrained,
        "uses_full_certified_core": trial_length == duration,
        "high_probe_linear_envelope": (
            superpotential + 2.0 * math.sqrt(rate2 / 3.0)
        ),
    }


def product_dirac_negative_axis_load_and_jets(
    proper_duration_lower: float,
    superpotential_absolute_upper: float,
    kappa_squared: float,
) -> dict[str, object]:
    """Return optimized base and unit compact log-radius jet bounds."""

    base = optimized_product_dirac_negative_axis_bounds(
        proper_duration_lower,
        superpotential_absolute_upper,
        kappa_squared,
    )
    jets = product_dirac_compact_radius_weyl_variation_bounds(
        base["upper"],
        superpotential_absolute_upper,
        kappa_squared,
        first_log_radius_bound=1.0,
        second_log_radius_bound=0.0,
    )
    return {"base": base, "jets": jets}


def scalar_negative_axis_load_and_jets(
    proper_duration_lower: float,
    potential_upper: float,
    kappa_squared: float,
) -> dict[str, object]:
    """Return scalar/de Rham base and unit compact log-radius jet bounds."""

    base = scalar_nonnegative_exterior_weyl_bounds(
        proper_duration_lower, potential_upper, kappa_squared
    )
    jets = scalar_compact_radius_weyl_variation_bounds(
        base["upper"],
        potential_upper,
        kappa_squared,
        first_log_radius_bound=1.0,
        second_log_radius_bound=0.0,
    )
    return {"base": base, "jets": jets}


__all__ = [
    "optimized_product_dirac_negative_axis_bounds",
    "product_dirac_negative_axis_load_and_jets",
    "scalar_negative_axis_load_and_jets",
]
