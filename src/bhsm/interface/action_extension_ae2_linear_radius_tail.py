"""Exact Bessel threshold laws for AE2 factorized linear-radius tails."""

from __future__ import annotations

import math

from scipy.integrate import quad
from scipy.special import jv, yv


def linear_radius_tail_source_law(beta: float, chirality: int) -> dict[str, object]:
    """Return the exact source-weight asymptotic class for ``s=chi*beta/x``.

    ``x`` is a dimensionless translated proper-time tail coordinate and
    ``k=sqrt(lambda)`` is only a mathematical threshold variable.  It is not
    a physical momentum identification for the neutral spectral parameter.
    """

    value = float(beta)
    sign = int(chirality)
    if not math.isfinite(value) or value < 0.0 or sign not in (-1, 1):
        raise ValueError("finite nonnegative beta and chirality +/-1 required")
    if value == 0.0:
        return {
            "beta": value,
            "chirality": sign,
            "first_source_weight_law": "IDENTICALLY_ZERO_FOR_ZERO_SUPERPOTENTIAL",
            "cumulative_source_measure_law": "IDENTICALLY_ZERO",
            "power_exponent": None,
            "cumulative_Lambda_exponent": None,
            "E1_threshold_integrable": True,
        }
    if sign == -1:
        power = 2.0 * value + 2.0
        cumulative = value + 1.5
        law = f"O(k^{power})"
        measure = f"O(Lambda^{cumulative})"
    elif math.isclose(value, 0.5, rel_tol=0.0, abs_tol=1.0e-14):
        power = None
        cumulative = None
        law = "O(k/abs(log(k))^2)"
        measure = "O(Lambda/abs(log(Lambda))^2)"
    elif value < 0.5:
        power = 2.0 - 2.0 * value
        cumulative = 1.5 - value
        law = f"O(k^{power})"
        measure = f"O(Lambda^{cumulative})"
    else:
        power = 2.0 * value
        cumulative = value + 0.5
        law = f"O(k^{power})"
        measure = f"O(Lambda^{cumulative})"
    return {
        "beta": value,
        "chirality": sign,
        "first_source_weight_law": law,
        "cumulative_source_measure_law": measure,
        "power_exponent": power,
        "cumulative_Lambda_exponent": cumulative,
        "critical_log_Dini_case": sign == 1 and math.isclose(value, 0.5, rel_tol=0.0, abs_tol=1.0e-14),
        "E1_threshold_integrable": True,
    }


def _orders(beta: float, chirality: int) -> tuple[float, float, float]:
    if chirality == 1:
        return beta + 0.5, beta - 0.5, 1.0
    nu = abs(beta - 0.5)
    if beta >= 0.5:
        return nu, beta + 0.5, -1.0
    return nu, -(beta + 0.5), 1.0


def linear_radius_tail_delta_state(
    beta: float,
    chirality: int,
    threshold_wave_number: float,
    tail_coordinate: float,
) -> tuple[float, float]:
    """Return the delta-normalized Bessel state ``(u,A u)``.

    The tail begins at ``x=1`` and carries the natural graph ``A u(1)=0``.
    """

    value = float(beta)
    sign = int(chirality)
    k = float(threshold_wave_number)
    x = float(tail_coordinate)
    if not math.isfinite(value) or value <= 0.0 or sign not in (-1, 1):
        raise ValueError("positive beta and chirality +/-1 required")
    if not math.isfinite(k) or k <= 0.0 or not math.isfinite(x) or x < 1.0:
        raise ValueError("positive threshold variable and tail coordinate >=1 required")
    nu, boundary_order, factor_sign = _orders(value, sign)
    coefficient_j = yv(boundary_order, k)
    coefficient_y = -jv(boundary_order, k)
    denominator = math.hypot(coefficient_j, coefficient_y)
    common = math.sqrt(k * x) / denominator
    state = common * (
        coefficient_j * jv(nu, k * x) + coefficient_y * yv(nu, k * x)
    )
    factor_image = factor_sign * k * common * (
        coefficient_j * jv(boundary_order, k * x)
        + coefficient_y * yv(boundary_order, k * x)
    )
    return float(state), float(factor_image)


def linear_radius_tail_compact_source_weight(
    beta: float,
    chirality: int,
    threshold_wave_number: float,
    support_end: float = 2.0,
) -> float:
    """Integrate the absolute first log-radius form weight on ``[1,L]``."""

    value = float(beta)
    sign = int(chirality)
    end = float(support_end)
    if not math.isfinite(end) or end <= 1.0:
        raise ValueError("finite source support end above one required")

    def integrand(x: float) -> float:
        state, factor_image = linear_radius_tail_delta_state(
            value, sign, threshold_wave_number, x
        )
        factor_jet = -sign * value * state / x
        return 2.0 * factor_image * factor_jet

    return abs(float(quad(integrand, 1.0, end, epsabs=1.0e-24, epsrel=1.0e-10)[0]))


__all__ = [
    "linear_radius_tail_compact_source_weight",
    "linear_radius_tail_delta_state",
    "linear_radius_tail_source_law",
]
