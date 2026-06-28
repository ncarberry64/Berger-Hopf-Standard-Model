from __future__ import annotations

from bhsm.interface.neutrino_action import derive_response_cone_from_neutral_action


def test_response_cone_has_partial_not_complete_action_support() -> None:
    result = derive_response_cone_from_neutral_action()
    assert result.status == "CONDITIONAL_ACTION_DERIVED_RESPONSE_CONE_CANDIDATE"
    assert result.ontology_support is True
    assert result.partial_action_support is True
    assert result.complete_action_derived is False
    assert result.positivity_proven_on_cone is True
    assert any("x_i >= 0" in item for item in result.constraints)
    assert "complete normalized neutral action" in result.remaining_missing_object

