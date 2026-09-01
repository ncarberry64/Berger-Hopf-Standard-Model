from scripts.derive_n12_forward_compact_interval_recentering import build_payload


def test_finite_regular_interval_cover_is_automatic() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"]["finite_regular_interval_variational_cover"] == "DERIVED"
    reduction = payload["necessity_reduction"]
    assert reduction["explicit_a_priori_global_B_delta_for_finite_regular_intervals"] is False
    assert reduction["terminal_event_return_for_finite_regular_interval_jets"] is False


def test_infinite_friedrichs_variational_limit_remains_open() -> None:
    payload = build_payload()
    assert payload["claim_boundary"]["infinite_Friedrichs_end_Weyl_C1_C2_limit"] == "OPEN"
    assert payload["claim_boundary"]["Gate_7"] == "ACTIVE_NOT_CLOSED"
    assert payload["FULL_BHSM_COMPLETE"] is False
