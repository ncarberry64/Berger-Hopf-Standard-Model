"""Exact half-line barrier threshold and birth-graph counterfamily."""

from __future__ import annotations

import math


def _positive(value: float, name: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number <= 0.0:
        raise ValueError(f"finite positive {name} required")
    return number


def barrier_critical_robin(rate: float, barrier_length: float) -> float:
    """Return the Robin value producing a zero-threshold resonance.

    The potential is ``rate**2`` on ``[0,T]`` and zero afterward, with
    ``u'(0)=h*u(0)``.  The zero-energy regular solution has ``u'(T)=0``
    exactly when ``h=-rate*tanh(rate*T)``; it then continues as a constant.
    """

    a = _positive(rate, "barrier rate")
    length = _positive(barrier_length, "barrier length")
    return -a * math.tanh(a * length)


def barrier_zero_energy_transfer(
    rate: float,
    barrier_length: float,
    robin_parameter: float,
) -> dict[str, float]:
    """Transfer the unit birth value through the constant barrier at zero."""

    a = _positive(rate, "barrier rate")
    length = _positive(barrier_length, "barrier length")
    h = float(robin_parameter)
    if not math.isfinite(h):
        raise ValueError("finite Robin parameter required")
    hyperbolic_sine = math.sinh(a * length)
    hyperbolic_cosine = math.cosh(a * length)
    value = hyperbolic_cosine + (h / a) * hyperbolic_sine
    derivative = a * hyperbolic_sine + h * hyperbolic_cosine
    return {
        "value_at_barrier_end": value,
        "derivative_at_barrier_end": derivative,
        "zero_energy_Wronskian": derivative,
    }


def barrier_scattering_birth_amplitude(
    energy_momentum: float,
    rate: float,
    barrier_length: float,
    robin_parameter: float,
) -> float:
    """Return the delta-normalized generalized eigenfunction at birth.

    This formula applies for ``0<k<rate``.  Matching the regular core
    solution to ``A*cos(k(x-T))+B*sin(k(x-T))`` gives normalization
    ``sqrt(2/pi)/sqrt(A**2+B**2)`` because the unit birth value is one.
    """

    k = _positive(energy_momentum, "energy momentum")
    a = _positive(rate, "barrier rate")
    length = _positive(barrier_length, "barrier length")
    h = float(robin_parameter)
    if not math.isfinite(h):
        raise ValueError("finite Robin parameter required")
    if k >= a:
        raise ValueError("barrier formula requires momentum below rate")
    alpha = math.sqrt(a * a - k * k)
    sine = math.sinh(alpha * length)
    cosine = math.cosh(alpha * length)
    value = cosine + (h / alpha) * sine
    derivative = alpha * sine + h * cosine
    normalization_denominator = math.hypot(value, derivative / k)
    return math.sqrt(2.0 / math.pi) / normalization_denominator


def regular_birth_amplitude_slope_limit(
    rate: float,
    barrier_length: float,
) -> float:
    """Return ``lim_(k->0) phi_k(0)/k`` for the nonnegative ``h=0`` graph."""

    a = _positive(rate, "barrier rate")
    length = _positive(barrier_length, "barrier length")
    return math.sqrt(2.0 / math.pi) / (a * math.sinh(a * length))


def critical_birth_amplitude_limit(
    rate: float,
    barrier_length: float,
) -> float:
    """Return ``lim_(k->0) phi_k(0)`` at the critical nonnegative graph."""

    a = _positive(rate, "barrier rate")
    length = _positive(barrier_length, "barrier length")
    return math.sqrt(2.0 / math.pi) * math.cosh(a * length)


__all__ = [
    "barrier_critical_robin",
    "barrier_zero_energy_transfer",
    "barrier_scattering_birth_amplitude",
    "regular_birth_amplitude_slope_limit",
    "critical_birth_amplitude_limit",
]
