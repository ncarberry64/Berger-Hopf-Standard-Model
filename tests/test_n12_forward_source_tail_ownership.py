from scripts.audit_n12_forward_source_tail_ownership import build_payload


def test_child_tail_and_source_tail_are_distinguished() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["adjudication"]["SPATIAL_GALERKIN_TAIL_CERTIFIED"] is True
    assert payload["adjudication"][
        "certified_for_event_child_state_correction"
    ] is True
    assert payload["adjudication"]["certified_for_Gate7_source_Hessian"] is False
    assert payload["tail_provenance"]["same_Galerkin_index"] is False


def test_comparison_rows_are_not_promoted_to_a_source_tail() -> None:
    payload = build_payload()
    assert payload["comparison_bound_scope"][
        "angular_sum_or_relative_trace"
    ] == "NOT_CERTIFIED"
    assert payload["adjudication"]["zero_source_force"] == "OPEN"
    assert payload["claim_boundary"]["Gate_7"] == "ACTIVE_NOT_CLOSED"
    assert payload["FULL_BHSM_COMPLETE"] is False
