from fractions import Fraction
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "theory"))

from candidate_boundary_second_variation import (  # noqa: E402
    excess_hessian_coefficient,
    hessian_projector_scaffold_supported,
    projector_second_variation_registry,
    selected_low_energy_dims_from_second_variation,
    topographic_lambda,
)


def test_topographic_lambda_zero_at_reference_and_positive_for_stable_modes():
    assert topographic_lambda(0) == Fraction(0, 1)
    assert topographic_lambda(1) > 0
    assert topographic_lambda(2) > 0
    with pytest.raises(ValueError):
        topographic_lambda(1, Fraction(-1, 1))


def test_excess_hessian_zero_for_low_dims_positive_for_excess_dims():
    for d in [1, 2, 3]:
        assert excess_hessian_coefficient(d) == Fraction(0, 1)
    for d in [4, 5, 8]:
        assert excess_hessian_coefficient(d) > 0


def test_projector_second_variation_registry_and_selection():
    registry = projector_second_variation_registry()
    assert set(registry) == {"P_ref", "P_orient", "P_cyclic", "P_excess"}
    assert hessian_projector_scaffold_supported()
    assert selected_low_energy_dims_from_second_variation(8) == [1, 2, 3]

