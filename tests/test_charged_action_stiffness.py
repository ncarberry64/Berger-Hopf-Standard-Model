from __future__ import annotations

from bhsm.interface.charged_closure import derive_or_locate_charged_action_stiffness


def test_charged_stiffness_exposes_values_without_forcing_rho() -> None:
    result = derive_or_locate_charged_action_stiffness()
    assert result.status == "CONDITIONAL_CHARGED_ACTION_STIFFNESS_CANDIDATE"
    assert result.projector_coefficients == {"lepton": "1/7", "up": "2/7", "down": "4/7"}
    assert result.g_bridge == "16/189"
    assert result.rho_ch_1_status == "MINIMAL_ACTION_CLOSURE_CANDIDATE"
    assert result.rho_ch_3_status == "STRUCTURALLY_MOTIVATED_NOT_DERIVED"
    assert result.rho_ch_selected is None
    assert result.action_normalization_status == "OPEN_MISSING_CHARGED_ACTION_NORMALIZATION"
    assert result.kinetic_stiffness_status == "OPEN_MISSING_CHARGED_KINETIC_STIFFNESS"
    assert result.curvature_penalty_status == "OPEN_MISSING_CHARGED_CURVATURE_PENALTY"
    assert result.numeric_stiffness_status == "OPEN_MISSING_NUMERIC_CHARGED_STIFFNESS"
    assert result.empirical_inputs_used is False
