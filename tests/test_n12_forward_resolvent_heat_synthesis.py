from scripts.audit_n12_forward_resolvent_heat_synthesis import build_payload


def test_single_probe_does_not_determine_heat_functional() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    witness = payload["single_probe_counterexample"]
    assert witness["common_Weyl_value"]["exact"] == "11/4"
    assert witness["second_Weyl_value"]["exact"] == "11/4"
    assert abs(witness["regulated_trace_difference"]) > 1.0e-6
    assert payload["retained_functional_calculus"][
        "one_resolvent_probe_sufficient"
    ] is False


def test_z_minus_1_rows_remain_valid_but_force_open() -> None:
    payload = build_payload()
    assert payload["adjudication"]["z_minus_1_rows_retracted"] is False
    assert payload["adjudication"]["z_minus_1_rows_promoted_to_Gamma_heat"] is False
    assert payload["current_channel_result_scope"][
        "zero_source_weak_geometry_force"
    ] == "OPEN"
    assert payload["claim_boundary"]["Gate_7"] == "ACTIVE_NOT_CLOSED"
