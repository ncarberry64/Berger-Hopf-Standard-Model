import pytest

from bhsm.interface.aether_forward_e1_source_measure import (
    e1_source_measure_dyadic_bound,
)


def test_source_weighted_e1_dyadic_bound() -> None:
    bound = e1_source_measure_dyadic_bound(3.0, 1.0, 2.0)
    assert bound["low_energy_integral_upper"] == 12.0
    assert bound["first_E1_variation_absolute_upper"] == 7.0


def test_strict_excess_exponent_is_required() -> None:
    with pytest.raises(ValueError):
        e1_source_measure_dyadic_bound(1.0, 0.0, 0.0)
