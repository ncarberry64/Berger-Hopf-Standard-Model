from scripts.derive_n12_c2_signed_duration_incidence_owner import build_payload


def test_signed_duration_incidence_owner_is_localized() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"][
        "signed_radius_lapse_duration_incidence_formula"
    ] == "DERIVED"
    assert payload["adjudication"]["signed_log_radius_incidence"] == "CLOSED"
    assert payload["adjudication"]["signed_log_lapse_incidence"] == "CLOSED"
    assert payload["adjudication"][
        "signed_D_Y_Delta_reference_center_ball"
    ] == "CERTIFIED_LOCAL_SEED"
    assert payload["exact_incidence"][
        "D_Y_Delta_center_relative_remainder_upper"
    ] < 2.8e-3
    assert payload["claim_boundary"]["signed_D_Y_Delta"] == "OPEN"


def test_norm_center_and_zero_witness_are_not_promoted() -> None:
    payload = build_payload()
    assert payload["adjudication"]["proof_center_used_as_physical_history"] is False
    assert "NOT_EXACT_FAMILY" in payload["exact_incidence"]["center_ball_scope"]
    invalid = next(
        row for row in payload["matching_audit"]
        if row["diagram_slot"] == "SIGNED_D_Y_Delta_ALONG_EXACT_C2_FAMILY"
    )
    assert invalid["verdict"] == (
        "VALID_LOCAL_SEED_BALL_NOT_YET_TRANSPORTED_TO_EXACT_FAMILY"
    )
    assert payload["claim_boundary"]["actual_projected_zero_source_force"] == "OPEN"
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
