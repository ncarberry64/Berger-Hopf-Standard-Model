from __future__ import annotations

import math

import pytest

from bhsm.interface.aether_forward_c2_duration_adjoint import (
    segment_duration_pullback_upper,
)


def test_segment_duration_pullback_formula() -> None:
    value = segment_duration_pullback_upper(
        proper_duration_upper=2.0,
        lapse_log_action_dual=3.0,
        delta_lower=0.5,
        delta_action_derivative_upper=4.0,
        local_state_growth_upper=5.0,
    )
    assert value >= 110.0
    assert math.nextafter(value, -math.inf) <= 110.0


@pytest.mark.parametrize("delta", [0.0, -1.0])
def test_segment_duration_pullback_rejects_bad_denominator(delta: float) -> None:
    with pytest.raises(ValueError):
        segment_duration_pullback_upper(
            proper_duration_upper=1.0,
            lapse_log_action_dual=1.0,
            delta_lower=delta,
            delta_action_derivative_upper=1.0,
            local_state_growth_upper=1.0,
        )
