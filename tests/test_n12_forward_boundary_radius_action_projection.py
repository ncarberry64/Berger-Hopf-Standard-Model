from scripts.derive_n12_forward_boundary_radius_action_projection import build_payload


def test_boundary_radius_action_projection_validates() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["action_projection"]["no_independent_radius_degree_of_freedom"] is True
    assert payload["certified_child_anchor"]["R4"] > 0.0


def test_projection_closes_only_the_radius_pullback() -> None:
    payload = build_payload()
    owner = payload["remaining_variational_owner"]
    assert owner["radius_pullback_after_state_jets"] == "CLOSED_BY_THIS_ARTIFACT"
    assert owner["global_DV_and_D2V_enclosures_on_maximal_component"] == "OPEN"
    assert payload["claim_boundary"]["maximal_x_history_numerically_enclosed"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
