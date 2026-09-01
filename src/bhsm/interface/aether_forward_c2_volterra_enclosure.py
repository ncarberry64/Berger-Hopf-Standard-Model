"""Inverse-free short-segment Volterra and two-boundary Weyl enclosures."""

from __future__ import annotations

import math
from typing import Any


Interval = tuple[float, float]


def _interval(values: tuple[float, float], name: str) -> Interval:
    lower, upper = (float(value) for value in values)
    if not all(math.isfinite(value) for value in (lower, upper)) or lower > upper:
        raise ValueError(f"finite ordered {name} interval required")
    return lower, upper


def _mul(left: Interval, right: Interval) -> Interval:
    products = tuple(a * b for a in left for b in right)
    return min(products), max(products)


def _add(left: Interval, right: Interval) -> Interval:
    return left[0] + right[0], left[1] + right[1]


def _div_positive(numerator: Interval, denominator: Interval) -> Interval:
    if denominator[0] <= 0.0:
        raise ValueError("strictly positive denominator interval required")
    quotients = tuple(a / b for a in numerator for b in denominator)
    return min(quotients), max(quotients)


def short_segment_transfer_weyl_enclosure(
    *,
    channel: str,
    unit_channel_value: float,
    spectral_parameter: float,
    log_radius_interval: tuple[float, float],
    proper_log_radius_rate_absolute_upper: float,
    proper_duration_interval: tuple[float, float],
    chirality: int = 1,
    log_radius_parameter_upper: float = 0.0,
    proper_duration_parameter_upper: float = 0.0,
) -> dict[str, Any]:
    """Enclose a supplied BHSM segment without integrating or inverting a block.

    The Duhamel estimate is centered on the birth generator ``G0``:

    ``||T-I-duration*G0|| <= .5*(K*duration)^2 exp(K*duration)``
    ``                           +.5*Lx*|x'|*duration^2``.

    Since every retained channel has ``G01=1``, this directly proves a
    positive transfer-``b`` chart.  The two-boundary response then uses only
    scalar interval reciprocals; no kinetic, Dirac, or transfer matrix is
    inverted.
    """

    kind = str(channel)
    value = float(unit_channel_value)
    z = float(spectral_parameter)
    x = _interval(log_radius_interval, "log-radius")
    duration = _interval(proper_duration_interval, "proper-duration")
    h_upper = float(proper_log_radius_rate_absolute_upper)
    x_parameter = float(log_radius_parameter_upper)
    duration_parameter = float(proper_duration_parameter_upper)
    sign = int(chirality)
    if (
        value < 0.0
        or duration[0] <= 0.0
        or h_upper < 0.0
        or x_parameter < 0.0
        or duration_parameter < 0.0
        or not all(math.isfinite(item) for item in (
            value, z, h_upper, x_parameter, duration_parameter,
        ))
    ):
        raise ValueError("finite nonnegative channel and positive duration required")

    potential = (
        value * math.exp(-2.0 * x[1]),
        value * math.exp(-2.0 * x[0]),
    )
    if kind == "scalar":
        shifted = (potential[0] - z, potential[1] - z)
        generator_norm = max(1.0, abs(shifted[0]), abs(shifted[1]))
        generator_x_norm = 2.0 * potential[1]
        diagonal_00 = (0.0, 0.0)
        diagonal_11 = (0.0, 0.0)
        lower_left = shifted
        channel_data: dict[str, Any] = {
            "potential_interval": list(potential),
            "shifted_potential_interval": list(shifted),
        }
    elif kind == "product_Dirac":
        if sign not in (-1, 1):
            raise ValueError("chirality must be +/-1")
        magnitude = (
            value * math.exp(-x[1]),
            value * math.exp(-x[0]),
        )
        superpotential = (
            sign * magnitude[0], sign * magnitude[1]
        ) if sign > 0 else (
            sign * magnitude[1], sign * magnitude[0]
        )
        # Frobenius is a safe bound for general z and is exact enough here.
        generator_norm = math.sqrt(
            2.0 * max(abs(item) for item in superpotential) ** 2
            + 1.0 + abs(z) ** 2
        )
        generator_x_norm = max(abs(item) for item in superpotential)
        diagonal_00 = (-superpotential[1], -superpotential[0])
        diagonal_11 = superpotential
        lower_left = (-z, -z)
        channel_data = {
            "superpotential_interval": list(superpotential),
        }
    else:
        raise ValueError("channel must be scalar or product_Dirac")

    scaled_norm = generator_norm * duration[1]
    nonlinear_remainder = 0.5 * scaled_norm**2 * math.exp(scaled_norm)
    coefficient_remainder = (
        0.5 * generator_x_norm * h_upper * duration[1] ** 2
    )
    transfer_remainder = nonlinear_remainder + coefficient_remainder
    b_interval = (
        duration[0] - transfer_remainder,
        duration[1] + transfer_remainder,
    )
    if b_interval[0] <= 0.0:
        raise ArithmeticError("Volterra remainder does not preserve transfer b")

    remainder_interval = (-transfer_remainder, transfer_remainder)
    a_interval = _add(
        (1.0, 1.0),
        _add(_mul(duration, diagonal_00), remainder_interval),
    )
    c_interval = _add(
        _mul(duration, lower_left), remainder_interval
    )
    d_interval = _add(
        (1.0, 1.0),
        _add(_mul(duration, diagonal_11), remainder_interval),
    )
    off_diagonal = (-1.0 / b_interval[0], -1.0 / b_interval[1])
    off_diagonal = (min(off_diagonal), max(off_diagonal))
    m00 = _div_positive(a_interval, b_interval)
    m11 = _div_positive(d_interval, b_interval)

    scaled_generator_parameter = (
        duration_parameter * generator_norm
        + duration[1] * generator_x_norm * x_parameter
    )
    transfer_parameter_upper = (
        math.exp(scaled_norm) * scaled_generator_parameter
    )
    a_absolute = max(abs(item) for item in a_interval)
    d_absolute = max(abs(item) for item in d_interval)
    inverse_b = 1.0 / b_interval[0]
    m00_parameter = (
        transfer_parameter_upper * inverse_b
        + a_absolute * transfer_parameter_upper * inverse_b**2
    )
    off_parameter = transfer_parameter_upper * inverse_b**2
    m11_parameter = (
        transfer_parameter_upper * inverse_b
        + d_absolute * transfer_parameter_upper * inverse_b**2
    )
    weyl_parameter_frobenius = math.sqrt(
        m00_parameter**2 + 2.0 * off_parameter**2 + m11_parameter**2
    )

    return {
        "channel": kind,
        "chirality": sign if kind == "product_Dirac" else None,
        "generator_norm_upper": generator_norm,
        "generator_log_radius_derivative_norm_upper": generator_x_norm,
        "scaled_generator_norm_upper": scaled_norm,
        "transfer_second_order_remainder_upper": transfer_remainder,
        "transfer_entries": {
            "a": list(a_interval),
            "b": list(b_interval),
            "c": list(c_interval),
            "d": list(d_interval),
        },
        "two_boundary_Weyl_entries": {
            "M00": list(m00),
            "M01_equals_M10": list(off_diagonal),
            "M11": list(m11),
        },
        "first_parameter_bounds": {
            "log_radius_parameter_upper": x_parameter,
            "proper_duration_parameter_upper": duration_parameter,
            "scaled_generator_parameter_upper": scaled_generator_parameter,
            "transfer_parameter_Frobenius_upper": transfer_parameter_upper,
            "Weyl_parameter_Frobenius_upper": weyl_parameter_frobenius,
        },
        "chart_margin_lower": b_interval[0],
        "Wronskian_identity": "det(T)=1_FROM_trace(G)=0",
        "endpoint_partition": ["C2_birth", "C2_launch_edge"],
        "endpoint_condition_imposed": False,
        "terminal_load_imposed": False,
        "explicit_matrix_inverse_formed": False,
        **channel_data,
    }


__all__ = ["short_segment_transfer_weyl_enclosure"]
