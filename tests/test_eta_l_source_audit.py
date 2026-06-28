from __future__ import annotations

from bhsm.interface.charged_closure import derive_or_locate_eta_l_source


def test_eta_l_remains_conditional_and_does_not_use_fit() -> None:
    result = derive_or_locate_eta_l_source()
    assert result.status == "CONDITIONAL_ETA_L_SOURCE_CANDIDATE"
    assert result.fitted_eta_present_in_history is True
    assert result.fitted_eta_used_as_theorem_input is False
    assert result.exact_value_derived is False
    assert result.action_source_status == "OPEN_MISSING_ETA_L_ACTION_SOURCE"
    assert result.transport_normalization_status == "OPEN_MISSING_ETA_L_TRANSPORT_NORMALIZATION"
    assert result.empirical_inputs_used is False
    assert result.frozen_predictions_changed is False
