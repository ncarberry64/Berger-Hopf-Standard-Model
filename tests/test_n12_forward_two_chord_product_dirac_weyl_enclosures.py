from scripts.derive_n12_forward_two_chord_product_dirac_weyl_enclosures import (
    build_payload,
)


def test_two_chord_product_dirac_enclosures_validate() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["adjudication"][
        "product_Dirac_base_Weyl_at_z_minus_1"
    ] == "ENCLOSED_BROADLY"
    assert len(payload["representative_retained_low_levels"]["rows"]) == 4


def test_factorized_route_does_not_add_s_prime_or_close_gate7() -> None:
    payload = build_payload()
    theorem = payload["factorized_comparison_theorem"]
    assert "NOT_IN_AN_EXPANDED_SCHRODINGER" in theorem[
        "reason_s_prime_is_absent"
    ]
    assert payload["adjudication"][
        "all_channel_pair_contact_incidence_assembly"
    ] == "OPEN"
    assert payload["claim_boundary"]["Gate_7"] == "ACTIVE_NOT_CLOSED"
    assert payload["FULL_BHSM_COMPLETE"] is False
