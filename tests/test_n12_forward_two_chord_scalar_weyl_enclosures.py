from scripts.derive_n12_forward_two_chord_scalar_weyl_enclosures import (
    build_payload,
)


def test_two_chord_scalar_derham_enclosures_validate() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["adjudication"][
        "scalar_and_deRham_base_Weyl_on_two_chord_core"
    ] == "ENCLOSED_BROADLY"
    assert len(payload["representative_retained_low_levels"]["rows"]) == 8


def test_comparison_does_not_select_future_or_close_gate7() -> None:
    payload = build_payload()
    assert payload["claim_boundary"]["terminal_event_reachability_required"] is False
    assert payload["adjudication"]["product_Dirac_channels"] == "OPEN"
    assert payload["adjudication"]["zero_source_force"] == "OPEN"
    assert payload["claim_boundary"]["Gate_7"] == "ACTIVE_NOT_CLOSED"
    assert payload["FULL_BHSM_COMPLETE"] is False
