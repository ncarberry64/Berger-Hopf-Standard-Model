"""Closed-form factorized zero-resonance threshold identities for AE2."""

from __future__ import annotations

import math


def factorized_constant_core_log_radius_weight(
    superpotential: float,
    core_length: float,
    momentum: float,
) -> dict[str, float]:
    """Return the delta-normalized first log-radius form weight.

    The model is ``A=d/dx+s`` on ``[0,T]`` and ``A=d/dx`` afterward, with
    the natural birth condition ``A u(0)=0``.  For ``0<k<s``, the state
    ``(u,w=A u)`` is propagated exactly.  The log-radius direction has
    ``A_h=-s`` on the core.  Exterior cosine/sine normalization gives the
    delta-normalized spectral weight ``2 Re <A u,A_h u>``.
    """

    s = float(superpotential)
    length = float(core_length)
    k = float(momentum)
    if not all(math.isfinite(value) and value > 0.0 for value in (s, length, k)):
        raise ValueError("finite positive factorized threshold inputs required")
    if k >= s:
        raise ValueError("the closed hyperbolic row requires momentum below s")
    gamma = math.sqrt(s * s - k * k)
    sinh = math.sinh(gamma * length)
    cosh = math.cosh(gamma * length)
    u_end = cosh - (s / gamma) * sinh
    w_end = -(k * k / gamma) * sinh
    exterior_amplitude_squared = u_end * u_end + (w_end / k) ** 2
    integral_sinh_cosh = sinh * sinh / (2.0 * gamma)
    integral_sinh_squared = (
        math.sinh(2.0 * gamma * length) / (4.0 * gamma) - length / 2.0
    )
    integral_u_w = -(k * k / gamma) * (
        integral_sinh_cosh - (s / gamma) * integral_sinh_squared
    )
    delta_normalization_squared = (2.0 / math.pi) / exterior_amplitude_squared
    weight = -2.0 * s * delta_normalization_squared * integral_u_w
    return {
        "momentum": k,
        "spectral_value": k * k,
        "core_end_value": u_end,
        "core_end_factor_image": w_end,
        "exterior_amplitude_squared": exterior_amplitude_squared,
        "first_log_radius_weight": weight,
        "weight_over_momentum_squared": weight / (k * k),
    }


def factorized_zero_resonance_weight_coefficient(
    superpotential: float,
    core_length: float,
) -> dict[str, float]:
    """Return the exact small-momentum and cumulative-counting coefficients."""

    s = float(superpotential)
    length = float(core_length)
    if not all(math.isfinite(value) and value > 0.0 for value in (s, length)):
        raise ValueError("finite positive factorized threshold inputs required")
    coefficient = (2.0 / math.pi) * math.exp(2.0 * s * length) * (
        length - (1.0 - math.exp(-2.0 * s * length)) / (2.0 * s)
    )
    return {
        "zero_energy_core_end_value": math.exp(-s * length),
        "zero_energy_core_end_factor_image": 0.0,
        "zero_energy_exterior_solution": "NONZERO_CONSTANT",
        "strict_zero_energy_wronskian_margin": 0.0,
        "weight_over_momentum_squared_limit": coefficient,
        "cumulative_weight_over_Lambda_to_three_halves_limit": coefficient / 3.0,
    }


__all__ = [
    "factorized_constant_core_log_radius_weight",
    "factorized_zero_resonance_weight_coefficient",
]
