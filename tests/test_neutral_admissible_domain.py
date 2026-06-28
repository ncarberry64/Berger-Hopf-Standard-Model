from __future__ import annotations

from bhsm.interface.neutrino_spectral import derive_or_load_neutral_admissible_domain


def test_measurement_supported_response_cone_is_explicit_and_conditional() -> None:
    domain = derive_or_load_neutral_admissible_domain()
    assert domain.status == "CONDITIONAL_MEASUREMENT_SUPPORTED_NEUTRAL_POSITIVITY_CANDIDATE"
    assert domain.admissible_domain_defined is True
    assert domain.action_derived is False
    assert any("x_i >= 0" in item for item in domain.admissible_domain_constraints)
    assert any("measurement-support" in item for item in domain.admissible_domain_constraints)
    assert "response-magnitude" in domain.coordinate_interpretation

