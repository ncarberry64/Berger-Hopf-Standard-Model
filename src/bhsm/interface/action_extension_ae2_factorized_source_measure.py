"""Resonance-compatible source-measure reduction for AE2 factorized channels."""

from __future__ import annotations

import math


def resonant_transfer_majorant(
    superpotential_abs_upper: float,
    source_support_length: float,
    log_radius_direction_abs_upper: float,
    delta_normalization_squared_sum_upper: float,
) -> dict[str, float]:
    """Bound the threshold coefficient of the first source weight by ``C*k**2``.

    Write ``lambda=k**2`` and ``v=A u``.  The fixed-channel system is

    ``u'=-s*u+v`` and ``v'=s*v-lambda*u``.

    At a zero resonance, ``u_0=exp(-integral s)`` and ``v_0=0``.  The
    lambda derivative satisfies

    ``v_1(t)=-exp(S(t))*integral_0^t exp(-2*S(r)) dr``.

    Therefore the compact first form vertex
    ``2 Re integral v*(-h*s*u)`` is linear in lambda.  This function returns
    a conservative explicit coefficient using only uniform core bounds and
    a uniform near-threshold bound on the sum of squared delta-normalization
    amplitudes.  That one scalar supremum is the weakest remaining exterior
    input.  The returned coefficient is a limsup/asymptotic majorant; local
    continuity supplies a finite neighborhood with an arbitrarily inflated
    coefficient.
    """

    values = (
        float(superpotential_abs_upper),
        float(source_support_length),
        float(log_radius_direction_abs_upper),
        float(delta_normalization_squared_sum_upper),
    )
    if not all(math.isfinite(value) and value >= 0.0 for value in values):
        raise ValueError("finite nonnegative resonant-transfer inputs required")
    s_bound, length, h_bound, normalization = values
    exponential = math.exp(4.0 * s_bound * length)
    coefficient = 2.0 * normalization * h_bound * s_bound * length * length * exponential
    return {
        "spectral_value_variable": "lambda=k^2",
        "factor_image_order_in_lambda": 1.0,
        "first_form_weight_order_in_k": 2.0,
        "superpotential_abs_upper": s_bound,
        "source_support_length": length,
        "log_radius_direction_abs_upper": h_bound,
        "uniform_near_threshold_delta_normalization_squared_sum_upper": normalization,
        "transfer_exponential_majorant": exponential,
        "first_form_weight_over_k_squared_upper": coefficient,
        "cumulative_measure_over_Lambda_to_three_halves_upper": coefficient / 3.0,
        "source_measure_excess_exponent": 0.5,
    }


def exact_constant_resonance_coefficient(
    superpotential: float,
    source_support_length: float,
) -> dict[str, float]:
    """Return the exact transfer-derivative coefficient for the constant core."""

    s = float(superpotential)
    length = float(source_support_length)
    if not all(math.isfinite(value) and value > 0.0 for value in (s, length)):
        raise ValueError("finite positive constant-resonance inputs required")
    normalization = (2.0 / math.pi) * math.exp(2.0 * s * length)
    unnormalized = length - (1.0 - math.exp(-2.0 * s * length)) / (2.0 * s)
    coefficient = normalization * unnormalized
    return {
        "threshold_delta_normalization_squared": normalization,
        "unnormalized_transfer_derivative_coefficient": unnormalized,
        "first_form_weight_over_k_squared_limit": coefficient,
        "cumulative_measure_over_Lambda_to_three_halves_limit": coefficient / 3.0,
    }


def endpoint_threshold_dichotomy(
    *,
    finite_regular_or_canonical_stop: bool,
    infinite_end_threshold_normalization_bound_available: bool,
) -> dict[str, object]:
    """Classify the exact remaining threshold obligation by far-end type."""

    finite = bool(finite_regular_or_canonical_stop)
    normalization = bool(infinite_end_threshold_normalization_bound_available)
    if finite:
        status = "COMPACT_RESOLVENT_ZERO_ATOM_HAS_EXACTLY_ZERO_FIRST_FORM_WEIGHT"
        open_input = None
    elif normalization:
        status = "RESONANCE_COMPATIBLE_SOURCE_MEASURE_SUPERLINEAR"
        open_input = None
    else:
        status = "OPEN_ONLY_THRESHOLD_DELTA_NORMALIZATION_SCALAR_BOUND"
        open_input = "FINITE_UNIFORM_NEAR_THRESHOLD_SUM_OF_SQUARED_GENERALIZED_EIGENSTATE_NORMALIZATIONS"
    return {
        "finite_regular_or_canonical_stop": finite,
        "infinite_end_threshold_normalization_bound_available": normalization,
        "status": status,
        "remaining_input": open_input,
        "strict_gap_required": False,
        "full_operator_norm_limiting_absorption_required": False,
    }


def integrable_reciprocal_radius_normalization(
    absolute_unit_radius_dirac_eigenvalue: float,
    reciprocal_radius_integral_upper: float,
    channel_multiplicity: int = 1,
    event_child_side_count: int = 2,
) -> dict[str, float]:
    """Return the two-chirality threshold normalization bound from ``int 1/R4``.

    For ``s_chi=chi*mu/R4`` and finite ``I_R=int d_tau/R4``, the zero
    transfer solution tends to ``exp(-chi*mu*I_R)``.  Relative to free
    half-line delta normalization, the squared threshold amplitudes are
    bounded by ``(2/pi)*exp(2*chi*mu*I_R)``.  Summing both chiralities,
    multiplicity, and the retained event/child sides gives the scalar below.
    """

    eigenvalue = float(absolute_unit_radius_dirac_eigenvalue)
    integral = float(reciprocal_radius_integral_upper)
    multiplicity = int(channel_multiplicity)
    sides = int(event_child_side_count)
    if not math.isfinite(eigenvalue) or eigenvalue < 0.0:
        raise ValueError("finite nonnegative Dirac eigenvalue required")
    if not math.isfinite(integral) or integral < 0.0:
        raise ValueError("finite nonnegative reciprocal-radius integral required")
    if multiplicity < 1 or sides < 1:
        raise ValueError("positive channel multiplicity and side count required")
    exponent = 2.0 * eigenvalue * integral
    positive = (2.0 / math.pi) * math.exp(exponent)
    negative = (2.0 / math.pi) * math.exp(-exponent)
    total = multiplicity * sides * (positive + negative)
    return {
        "absolute_unit_radius_dirac_eigenvalue": eigenvalue,
        "reciprocal_radius_integral_upper": integral,
        "positive_chirality_normalization_squared_upper": positive,
        "negative_chirality_normalization_squared_upper": negative,
        "chirality_event_child_multiplicity": float(multiplicity * sides),
        "uniform_near_threshold_normalization_squared_sum_upper": total,
    }


def reciprocal_radius_integral_from_power_growth(
    initial_radius_lower: float,
    growth_time_scale: float,
    excess_power: float,
) -> dict[str, float]:
    """Integrate a sufficient geometric lower growth law for ``R4``.

    If ``R4(tau)>=R0*(1+tau/T0)**(1+delta)``, then
    ``integral_0^infinity d_tau/R4 <= T0/(R0*delta)``.
    """

    radius = float(initial_radius_lower)
    scale = float(growth_time_scale)
    delta = float(excess_power)
    if not all(math.isfinite(value) and value > 0.0 for value in (radius, scale, delta)):
        raise ValueError("finite positive radius-growth inputs required")
    return {
        "radius_lower_law": "R4(tau)>=R0*(1+tau/T0)^(1+delta)",
        "initial_radius_lower": radius,
        "growth_time_scale": scale,
        "excess_power": delta,
        "reciprocal_radius_integral_upper": scale / (radius * delta),
    }


__all__ = [
    "endpoint_threshold_dichotomy",
    "exact_constant_resonance_coefficient",
    "integrable_reciprocal_radius_normalization",
    "reciprocal_radius_integral_from_power_growth",
    "resonant_transfer_majorant",
]
