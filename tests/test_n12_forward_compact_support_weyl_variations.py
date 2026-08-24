from scripts.derive_n12_forward_compact_support_weyl_variations import build_payload


def test_compact_support_friedrichs_weyl_variations_validate() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["claim_boundary"][
        "infinite_Friedrichs_compact_support_Weyl_C1_C2"
    ] == "DERIVED"
    assert payload["weak_variation_theorem"]["endpoint_domain_variation"] == 0


def test_oracle_values_and_global_saddle_remain_open() -> None:
    payload = build_payload()
    assert payload["infinite_end_adjudication"][
        "uniform_transfer_jet_limit_as_T_to_infinity_required"
    ] is False
    assert payload["claim_boundary"]["oracle_values"] == "OPEN"
    assert payload["claim_boundary"]["same_action_saddle"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
