"""Norm enclosures for fixed-descriptor moving proper-time readouts."""

from __future__ import annotations

import math


def segment_duration_pullback_upper(
    *,
    proper_duration_upper: float,
    lapse_log_action_dual: float,
    delta_lower: float,
    delta_action_derivative_upper: float,
    local_state_growth_upper: float,
) -> float:
    """Bound the segment-duration derivative from its segment-start state.

    For ``d tau/ds = N(Y(s))*s/Delta(Y(s))``, logarithmic
    differentiation and the fixed-descriptor state propagator give

    ``|D h| <= h^+ G (||D log N|| + ||D Delta||/Delta_-)``.
    """

    values = (
        proper_duration_upper,
        lapse_log_action_dual,
        delta_lower,
        delta_action_derivative_upper,
        local_state_growth_upper,
    )
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError("finite duration-adjoint inputs required")
    if not (
        proper_duration_upper > 0.0
        and lapse_log_action_dual >= 0.0
        and delta_lower > 0.0
        and delta_action_derivative_upper >= 0.0
        and local_state_growth_upper >= 1.0
    ):
        raise ValueError("positive duration, denominator, and growth required")
    return math.nextafter(
        proper_duration_upper
        * local_state_growth_upper
        * (lapse_log_action_dual + delta_action_derivative_upper / delta_lower),
        math.inf,
    )


__all__ = ["segment_duration_pullback_upper"]
