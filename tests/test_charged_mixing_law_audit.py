from __future__ import annotations

from bhsm.interface.charged_closure import derive_or_locate_charged_mixing_law_source


def test_charged_mixing_law_is_conditional_with_explicit_sources() -> None:
    result = derive_or_locate_charged_mixing_law_source()
    assert result.status == "CONDITIONAL_CHARGED_MIXING_LAW_CANDIDATE"
    assert result.theta12_formula == "theta12_d - theta12_u"
    assert result.theta23_formula == "tau * theta12_CKM"
    assert result.theta13_formula == "tau^2 * theta12_CKM"
    assert result.delta_formula == "pi/3"
    assert result.theta12_source_status == "ARTIFACT_BACKED"
    assert result.theta23_source_status == "CONDITIONAL_CHARGED_MIXING_LAW_CANDIDATE"
    assert result.theta13_source_status == "CONDITIONAL_CHARGED_MIXING_LAW_CANDIDATE"
    assert result.delta_source_status == "ARTIFACT_BACKED"
    assert result.frozen_ckm_changed is False
