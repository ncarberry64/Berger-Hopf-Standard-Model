import math

import pytest

from bhsm.interface.aether_forward_barrier_threshold import (
    barrier_critical_robin,
    barrier_scattering_birth_amplitude,
    barrier_zero_energy_transfer,
    critical_birth_amplitude_limit,
    regular_birth_amplitude_slope_limit,
)


def test_critical_graph_has_exact_zero_wronskian() -> None:
    critical = barrier_critical_robin(2.0, 0.75)
    transfer = barrier_zero_energy_transfer(2.0, 0.75, critical)
    assert critical == pytest.approx(-2.0 * math.tanh(1.5))
    assert transfer["derivative_at_barrier_end"] == pytest.approx(0.0, abs=1.0e-15)
    assert transfer["value_at_barrier_end"] == pytest.approx(1.0 / math.cosh(1.5))


def test_regular_and_critical_scattering_limits_differ_by_one_power() -> None:
    rate = 2.0
    length = 0.75
    critical = barrier_critical_robin(rate, length)
    regular_limit = regular_birth_amplitude_slope_limit(rate, length)
    critical_limit = critical_birth_amplitude_limit(rate, length)
    for momentum in (1.0e-3, 3.0e-4, 1.0e-4):
        regular = barrier_scattering_birth_amplitude(
            momentum, rate, length, 0.0
        )
        resonant = barrier_scattering_birth_amplitude(
            momentum, rate, length, critical
        )
        assert regular / momentum == pytest.approx(regular_limit, rel=2.0e-6)
        assert resonant == pytest.approx(critical_limit, rel=2.0e-6)


@pytest.mark.parametrize("bad", [0.0, -1.0, math.inf, math.nan])
def test_positive_barrier_inputs_fail_closed(bad: float) -> None:
    with pytest.raises(ValueError):
        barrier_critical_robin(bad, 1.0)
