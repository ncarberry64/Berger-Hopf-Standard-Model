from scripts.audit_n12_forward_brst_heat_tail_cancellation import build_payload


def test_physical_graded_heat_tail_does_not_cancel() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["exact_asymptotic"]["leading_degeneracy_coefficient"] == -20
    assert payload["exact_asymptotic"]["leading_scaled_limit"] == "-5*sqrt(pi)"
    assert payload["adjudication"]["longitudinal_ghost_BRST_pair"] == (
        "CANCELS_EXACTLY"
    )
    assert payload["adjudication"][
        "BRST_grading_closes_source_angular_tail"
    ] is False


def test_relative_or_finite_endpoint_route_remains_open() -> None:
    payload = build_payload()
    assert payload["adjudication"][
        "action_owned_relative_reference_or_low_energy_control"
    ] == "STILL_REQUIRED"
    assert payload["claim_boundary"]["Gate_7"] == "ACTIVE_NOT_CLOSED"
    assert payload["FULL_BHSM_COMPLETE"] is False
