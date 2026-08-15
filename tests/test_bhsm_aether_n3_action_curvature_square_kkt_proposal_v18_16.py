from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import completion_payload


def test_v18_16_uses_coordinate_map_only_for_square_kkt_proposals() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["action_curvature_square_kkt_proposal"]
    assert result["coordinate_map"]["invertible"]
    assert result["proposal_model"]["right_coordinate_map_only"]
    assert not result["proposal_model"]["left_residual_scaling_applied"]
    assert not result["componentwise_monotonicity_required"]
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    if selected is not None:
        assert selected["complete_norm_reduction"] > 0.0
        assert selected["eta_minimum"] > 0.0
