from bhsm.interface.aether_n3_exact_merit_orientation_audit_v18_17 import completion_payload


def test_v18_17_uses_exact_merit_to_classify_both_orientations() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    result = payload["exact_merit_orientation_audit"]
    assert result["v18_16_forward_candidate_count"] == 0
    assert not result["proposal_orientation_is_exact_descent"]
    assert not result["componentwise_monotonicity_required"]
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    if selected is not None:
        assert selected["complete_norm_reduction"] > 0.0
        assert selected["eta_minimum"] > 0.0
