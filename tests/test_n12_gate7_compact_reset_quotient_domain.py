from scripts.certify_n12_gate7_compact_reset_quotient_domain import build_payload


def test_compact_reset_quotient_domain_closes_parametric_radii() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "COMPACT_NONEMPTY_AE2_RESET_QUOTIENT_DOMAIN_CERTIFIED"
    )
    assert payload["parameter_domain"]["dimension"] == 72
    assert payload["parameter_domain"]["compact"] is True
    assert payload["parameter_radii_theorem"]["radii_polynomial_upper"] < 0.0
    assert (
        payload["parameter_domain"]["joint_action_radius_upper"]
        < payload["parameter_domain"]["parent_action_radius"]
    )


def test_reset_domain_keeps_first_jets_margins_and_claim_boundary() -> None:
    payload = build_payload()
    assert payload["quotient_first_jet"][
        "uniform_C2_quotient_first_jet_singular_value_lower"
    ] > 0.0
    margins = payload["uniform_regular_domain_margins"]
    assert margins["boundary_lapse_lower"] > 0.0
    assert margins["boundary_radius_lower"] > 0.0
    assert margins["D_tau_log_R4_lower"] > 0.0
    assert payload["adjudication"]["reset_member_selected"] is False
    assert payload["adjudication"]["propagated_reset_to_terminal_map"] == (
        "OPEN_CURRENT_OWNER"
    )
    assert payload["FULL_BHSM_COMPLETE"] is False
