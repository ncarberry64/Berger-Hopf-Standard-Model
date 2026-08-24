import math

import pytest

from bhsm.interface.aether_forward_threshold_source_measure import (
    constant_superpotential_zero_mode_witness,
    factorized_first_form_bound,
    free_neumann_compact_counting_leading_coefficient,
    free_robin_compact_counting_bound,
    scalar_core_zero_energy_impedance_lower,
)


def test_scalar_core_margin_is_positive_except_for_constant_channel() -> None:
    assert scalar_core_zero_energy_impedance_lower(0.25, 2.0, 0.0) == 0.0
    margin = scalar_core_zero_energy_impedance_lower(0.25, 2.0, 4.0)
    assert margin == pytest.approx(math.tanh(0.25))


def test_free_positive_robin_has_three_halves_counting_bound() -> None:
    result = free_robin_compact_counting_bound(2.0, 3.0, 5.0, 0.25)
    coefficient = 2.0 * 5.0 * (7.0 / 2.0) ** 2 / (3.0 * math.pi)
    assert result["excess_exponent"] == 0.5
    assert result["counting_coefficient"] == pytest.approx(coefficient)
    assert result["counting_upper"] == pytest.approx(coefficient / 8.0)


def test_free_neumann_has_only_square_root_threshold_weight() -> None:
    assert free_neumann_compact_counting_leading_coefficient(3.0, 2.0) == (
        pytest.approx(12.0 / math.pi)
    )


def test_factorized_kernel_atom_has_zero_first_weight() -> None:
    assert factorized_first_form_bound(0.0, 1.0e30) == 0.0
    witness = constant_superpotential_zero_mode_witness(2.0)
    assert witness["L2_norm_squared"] == 1.0
    assert witness["factor_image_norm"] == 0.0
    assert witness["birth_conormal"] == 0.0
    assert witness["first_form_weight"] == 0.0


@pytest.mark.parametrize("bad", [0.0, -1.0, math.inf, math.nan])
def test_positive_inputs_fail_closed(bad: float) -> None:
    with pytest.raises(ValueError):
        scalar_core_zero_energy_impedance_lower(bad, 1.0, 1.0)
    with pytest.raises(ValueError):
        free_robin_compact_counting_bound(bad, 1.0, 1.0, 1.0)
    with pytest.raises(ValueError):
        constant_superpotential_zero_mode_witness(bad)
