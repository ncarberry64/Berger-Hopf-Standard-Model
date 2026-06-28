from __future__ import annotations

from bhsm.interface.neutrino_spectral import search_neutral_stiffness_ratio


def test_neutral_stiffness_search_fails_closed_at_symbolic_ratio() -> None:
    result = search_neutral_stiffness_ratio()
    assert result.status == "CONDITIONAL_NEUTRAL_STIFFNESS_RATIO_CANDIDATE"
    assert result.value == "sqrt(A_nu/Z_nu)"
    assert result.symbolic_ratio_available is True
    assert result.numeric_length_available is False
    assert result.stiffness_length_m is None
    assert result.kinetic_stiffness.status == "OPEN_MISSING_NEUTRAL_KINETIC_STIFFNESS"
    assert result.curvature_penalty.status == "OPEN_MISSING_NEUTRAL_CURVATURE_PENALTY"
    assert result.reference_values_used_as_theorem_inputs is False

