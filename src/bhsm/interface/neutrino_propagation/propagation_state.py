"""Propagation-state model for neutral BHSM boundary fields."""

from __future__ import annotations

from math import sqrt

from .common import PropagationState


def normalized_state(
    label: str,
    amplitudes: tuple[float, ...],
    propagation_response: float,
) -> PropagationState:
    if propagation_response < 0:
        raise ValueError("propagation_response must be nonnegative")
    norm = sqrt(sum(value * value for value in amplitudes))
    if norm == 0:
        raise ValueError("neutral boundary amplitudes cannot all vanish")
    normalized = tuple(value / norm for value in amplitudes)
    return PropagationState(
        label=label,
        amplitudes=normalized,
        propagation_response=float(propagation_response),
        stopped=propagation_response == 0,
        status="CONDITIONAL_PROPAGATION_THEOREM",
        claim_boundary="Propagation response is a dimensionless theorem variable, not an observed velocity or fitted mass input.",
    )


def canonical_channel_states(
    dimension: int = 3,
    propagation_response: float = 1.0,
) -> tuple[PropagationState, ...]:
    if dimension <= 0:
        raise ValueError("dimension must be positive")
    return tuple(
        normalized_state(
            f"neutral_channel_{index + 1}",
            tuple(1.0 if row == index else 0.0 for row in range(dimension)),
            propagation_response,
        )
        for index in range(dimension)
    )
