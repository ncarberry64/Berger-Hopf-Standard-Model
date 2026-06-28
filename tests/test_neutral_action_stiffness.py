from __future__ import annotations

from bhsm.interface.neutrino_action import (
    derive_neutral_stiffness_length,
    derive_or_locate_neutral_curvature_penalty,
    derive_or_locate_neutral_kinetic_stiffness,
)


def test_neutral_stiffness_coefficients_are_symbolic_not_fabricated() -> None:
    kinetic = derive_or_locate_neutral_kinetic_stiffness()
    penalty = derive_or_locate_neutral_curvature_penalty()
    length = derive_neutral_stiffness_length()
    assert kinetic.status == "OPEN_MISSING_NEUTRAL_KINETIC_STIFFNESS"
    assert kinetic.symbolic_available is True and kinetic.numeric_available is False
    assert penalty.status == "OPEN_MISSING_NEUTRAL_CURVATURE_PENALTY"
    assert penalty.symbolic_available is True and penalty.numeric_available is False
    assert penalty.coefficient_symbol == "A_nu_gap"
    assert penalty.distinct_from_robin_coefficient is True
    assert length.status == "OPEN_MISSING_NUMERIC_STIFFNESS_LENGTH"
    assert length.dimension == "length required by spectral-gap dimensional closure"
    assert length.numeric_length_available is False
    assert length.stiffness_length_m is None

