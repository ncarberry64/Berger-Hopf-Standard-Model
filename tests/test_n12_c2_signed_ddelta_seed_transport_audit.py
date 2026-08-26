from scripts.audit_n12_c2_signed_ddelta_seed_transport import build_payload


def test_coarse_ddelta_transport_is_certified_but_not_sign_resolving() -> None:
    payload = build_payload()
    row = payload["reference_transport"]
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "COARSE_DDELTA_TRANSPORT_CERTIFIED_BUT_NOT_SIGN_RESOLVING"
    )
    assert row["proof_center_match_action_norm"] == 0.0
    assert (
        row["incoming_exact_state_tube_action_radius_upper"]
        < row["first_matrix_chart_action_radius"]
    )
    assert row["transported_DDelta_remainder_action_norm_upper"] > row[
        "DDelta_seed_partial_action_norm"
    ]
    assert row["transported_ball_zero_exclusion_margin"] < 0.0


def test_transport_failure_is_not_promoted_to_physics() -> None:
    payload = build_payload()
    assert payload["adjudication"]["physical_obstruction_found"] is False
    assert payload["adjudication"][
        "signed_DDelta_on_exact_parametric_family"
    ] == "OPEN_NOT_RESOLVED_BY_COARSE_BOUND"
    assert "CANCELLATION_PRESERVING_D2DELTA" in payload[
        "adjudication"
    ]["minimal_missing_theorem"]
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
