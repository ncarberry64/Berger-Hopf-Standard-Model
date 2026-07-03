from bhsm.interface.sector_boundary_operator import build_artifact_payloads, required_open_gates, status_table, whitened_action_formula


def test_whitened_variable_and_inverse_covariance_action_are_conditional():
    for sector in ("U1", "SU2", "SU3"):
        payload = whitened_action_formula(sector)
        assert payload["whitened_variable"] == "B_i=L_i(rho)^(1/2) A_i"
        assert "<A_i,L_i(rho)A_i>" in payload["quadratic_action"]
        assert "<B_i,B_i>" in payload["quadratic_action"]
        assert payload["physical_alpha_status"] == "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION"
        assert payload["is_action_derived"] is False


def test_domain_lower_terms_running_and_downstream_gates_remain_open():
    gates = required_open_gates()
    required = {
        "OPEN_MISSING_SECTOR_BOUNDARY_OPERATOR_ACTION_SOURCE",
        "OPEN_MISSING_GAUGE_FIXED_BOUNDARY_DOMAIN",
        "OPEN_MISSING_LOWER_ORDER_BOUNDARY_OPERATOR_TERMS",
        "OPEN_MISSING_SPECTRAL_CORRECTION_Z_i",
        "OPEN_MISSING_ACTION_SELECTED_RHO_i_OF_MU",
        "OPEN_MISSING_ALPHA_I_ACTION_DERIVATION",
        "OPEN_MISSING_G2_BH_ACTION_SOURCE",
        "OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE",
        "CKM_EXPONENT_NOT_DERIVED",
        "FULL_BHSM_NOT_COMPLETE",
    }
    assert required.issubset(gates)
    statuses = status_table()
    assert statuses["gauge_domain"] == "OPEN_MISSING_GAUGE_FIXED_BOUNDARY_DOMAIN"
    assert statuses["lower_order_terms"] == "OPEN_MISSING_LOWER_ORDER_BOUNDARY_OPERATOR_TERMS"
    assert statuses["full_completion"] == "FULL_BHSM_NOT_COMPLETE"


def test_principal_symbol_does_not_silently_complete_operator():
    payloads = build_artifact_payloads()
    assert payloads["gauge_fixed_domain_gate"]["unrestricted_domain_solved"] is False
    assert payloads["lower_order_operator_terms_gate"]["principal_symbol_determines_full_operator"] is False
    assert len(payloads["lower_order_operator_terms_gate"]["candidate_terms"]) == 6
