from scripts.derive_n12_c2_1222_parametric_base_family import build_payload


def test_parametric_base_family_exists_through_the_finite_core() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"][
        "parametric_base_history_existence_through_1222"
    ] == "DERIVED"
    assert payload["adjudication"][
        "parametric_C2_base_history_exists_through_finite_core_1222"
    ] is True
    assert payload["finite_cover_witness"]["segment_count"] == 1222
    assert payload["finite_cover_witness"]["complete_fixed_s_growth_upper"] < 1.013


def test_family_theorem_does_not_promote_a_center_endpoint_or_force() -> None:
    payload = build_payload()
    adjudication = payload["adjudication"]
    assert adjudication["positive_duration_forward_history_existence_reopened"] is False
    assert adjudication["proof_center_selected_as_a_physical_member"] is False
    assert adjudication["far_core_edge_is_event_or_stop"] is False
    assert adjudication["signed_backward_adjoint_numerically_evaluated_and_certified"] is False
    assert payload["claim_boundary"]["actual_projected_zero_source_force"] == "OPEN"
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
