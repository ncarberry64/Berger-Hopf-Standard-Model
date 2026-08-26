from scripts.derive_n12_c2_signed_duration_incidence_owner import build_payload


def test_signed_duration_incidence_owner_is_localized() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"][
        "signed_radius_lapse_duration_incidence_formula"
    ] == "DERIVED"
    assert payload["adjudication"]["signed_log_radius_incidence"] == "CLOSED"
    assert payload["adjudication"]["signed_log_lapse_incidence"] == "CLOSED"
    assert payload["claim_boundary"]["signed_D_Y_Delta"] == "OPEN"


def test_norm_center_and_zero_witness_are_not_promoted() -> None:
    payload = build_payload()
    assert payload["adjudication"]["proof_center_used_as_physical_history"] is False
    assert "ZERO_ONLY_FOR_ALGEBRAIC_CROSSCHECK" in payload["exact_incidence"][
        "formula_witness_DDelta"
    ]
    invalid = next(
        row for row in payload["matching_audit"]
        if row["diagram_slot"] == "SIGNED_D_Y_Delta_ALONG_EXACT_C2_FAMILY"
    )
    assert invalid["verdict"] == "INVALID_MATCH_NORM_HAS_NO_SIGN_OR_DIRECTION"
    assert payload["claim_boundary"]["actual_projected_zero_source_force"] == "OPEN"
    assert payload["claim_boundary"]["FULL_BHSM_COMPLETE"] is False
