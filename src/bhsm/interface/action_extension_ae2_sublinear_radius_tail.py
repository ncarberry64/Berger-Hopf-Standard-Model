"""Agmon threshold bounds for exact sublinear AE2 radius tails."""

from __future__ import annotations

import math


def sublinear_positive_chirality_agmon_action(
    beta: float,
    radius_power: float,
    threshold_wave_number: float,
) -> dict[str, float]:
    """Lower-bound the barrier action for ``s=beta*x**(-a)``, ``0<a<1``.

    On ``1<=x<=x_k=(beta/(2k))**(1/a)``, ``s>=2k`` and the positive
    chirality potential ``s**2-s'`` is at least ``s**2``.  Hence
    ``sqrt(V-k**2)>=sqrt(3)*s/2`` and the stated exact integral follows.
    """

    strength = float(beta)
    power = float(radius_power)
    k = float(threshold_wave_number)
    if not math.isfinite(strength) or strength <= 0.0:
        raise ValueError("finite positive beta required")
    if not math.isfinite(power) or not 0.0 < power < 1.0:
        raise ValueError("radius power strictly between zero and one required")
    if not math.isfinite(k) or not 0.0 < k < strength / 2.0:
        raise ValueError("threshold variable must lie in (0,beta/2)")
    turning_lower = (strength / (2.0 * k)) ** (1.0 / power)
    action = (
        math.sqrt(3.0)
        * strength
        * (turning_lower ** (1.0 - power) - 1.0)
        / (2.0 * (1.0 - power))
    )
    return {
        "beta": strength,
        "radius_power": power,
        "threshold_wave_number": k,
        "barrier_endpoint_lower": turning_lower,
        "agmon_action_lower": action,
        "squared_amplitude_suppression_upper": math.exp(-2.0 * action),
        "stretched_exponential_power": (1.0 - power) / power,
    }


def power_radius_tail_class(radius_power: float) -> dict[str, object]:
    """Classify exact ``R4~x**a`` tails by the proved threshold route."""

    power = float(radius_power)
    if not math.isfinite(power) or power < 0.0:
        raise ValueError("finite nonnegative radius power required")
    if power == 0.0:
        route = "ASYMPTOTIC_CONSTANT_SUPERPOTENTIAL_GAP"
    elif power < 1.0:
        route = "SUBLINEAR_STRETCHED_EXPONENTIAL_AGMON_SUPPRESSION"
    elif power == 1.0:
        route = "EXACT_LINEAR_BESSEL_SOURCE_DINI_THEOREM"
    else:
        route = "INTEGRABLE_RECIPROCAL_RADIUS_THEOREM"
    return {
        "radius_power": power,
        "threshold_route": route,
        "factorized_E1_threshold_integrable": True,
    }


__all__ = ["power_radius_tail_class", "sublinear_positive_chirality_agmon_action"]
