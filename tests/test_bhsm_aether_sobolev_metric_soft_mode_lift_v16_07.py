import numpy as np

from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    sobolev_weights,
    spectral_frequencies,
)


def test_nested_basis_frequencies_are_exact():
    result = spectral_frequencies(3)
    assert np.array_equal(result["coordinates"], [0, 4, 8, 12, 0, 4, 8, 0, 4, 8])
    assert np.array_equal(result["multipliers"], [4, 8, 12, 0, 4, 8])


def test_high_modes_are_not_cheap_in_the_declared_sobolev_metric():
    result = sobolev_weights(6, 6.0)
    velocity = result["velocities"]
    multipliers = result["multipliers"]
    assert velocity[-1] > velocity[1] > 1.0
    assert multipliers[-1] > multipliers[0] > 1.0


def test_regular_phase_space_threshold_is_enforced():
    try:
        sobolev_weights(3, 5.5)
    except ValueError as error:
        assert "s>11/2" in str(error)
    else:
        raise AssertionError("invalid Sobolev regularity accepted")
