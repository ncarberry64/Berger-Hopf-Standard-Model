from scripts.audit_n12_forward_e1_infrared_control import build_payload


def test_current_bounds_do_not_close_e1_infrared() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["adjudication"]["uniform_global_positive_source_gap"] == (
        "NOT_CERTIFIED"
    )
    assert payload["adjudication"]["E1_infrared_synthesis_from_current_bounds"] == (
        "OPEN"
    )
    assert payload["adjudication"]["z_minus_1_channel_enclosures"] == (
        "VALID_NOT_SUFFICIENT"
    )


def test_finite_and_infinite_maximal_outcome_routes_remain() -> None:
    payload = build_payload()
    routes = payload["maximal_outcome_routes"]
    assert routes["terminal_event_reachability_required_a_priori"] is False
    assert "SPECTRAL_GAP" in routes["actual_finite_terminal_or_domain_exit"]
    assert "RELATIVE_HEAT_TRACE" in routes["infinite_regular_Friedrichs_history"]
    assert payload["claim_boundary"]["Gate_7"] == "ACTIVE_NOT_CLOSED"
    assert payload["FULL_BHSM_COMPLETE"] is False
