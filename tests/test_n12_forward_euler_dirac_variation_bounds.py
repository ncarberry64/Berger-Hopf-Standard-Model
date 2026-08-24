from scripts.derive_n12_forward_euler_dirac_variation_bounds import build_payload


def test_local_second_state_jacobi_tube_validates() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    tube = payload["local_state_Jacobi_tube"]
    assert tube["duration"] > 0.0
    assert tube["D2V_bound"] > 0.0
    assert tube["unit_first_Jacobi_bound"] >= 1.0
    assert tube["zero_initial_mixed_Jacobi_bound"] > 0.0


def test_local_tube_does_not_overclaim_maximal_cover() -> None:
    payload = build_payload()
    assert payload["scope_boundary"]["local_anchor_action_ball"] == "CERTIFIED"
    assert payload["scope_boundary"]["maximal_forward_component_cover"] == "OPEN"
    assert payload["claim_boundary"]["Gate_7"] == "ACTIVE_NOT_CLOSED"
    assert payload["FULL_BHSM_COMPLETE"] is False
