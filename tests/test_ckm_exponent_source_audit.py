from __future__ import annotations

from bhsm.interface.charged_closure import derive_or_locate_ckm_exponent_source


def test_ckm_one_sixteenth_is_not_promoted() -> None:
    result = derive_or_locate_ckm_exponent_source()
    assert result.status == "OPEN_MISSING_CKM_EXPONENT_DERIVATION"
    assert result.exponent == "1/16"
    assert result.historical_candidate_selected_by_residual is True
    assert result.residual_used_as_theorem_input is False
    assert result.action_source_found is False
    assert result.projector_source_found is True
    assert result.cross_scale_transport_status == "OPEN_MISSING_CROSS_SCALE_TRANSPORT"
    assert result.frozen_ckm_changed is False
