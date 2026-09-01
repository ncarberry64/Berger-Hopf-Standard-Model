from scripts.derive_n12_forward_e1_source_measure_criterion import build_payload


def test_source_weighted_force_criterion_validates() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["hindsight"]["uniform_global_operator_gap_logically_required"] is False
    assert payload["hindsight"][
        "one_source_weighted_measure_estimate_sufficient_for_force"
    ] is True
    assert payload["exact_witness"]["first_E1_variation_absolute_upper"] == 7.0


def test_actual_force_and_second_variation_remain_open() -> None:
    payload = build_payload()
    assert payload["hindsight"][
        "actual_N12_source_weighted_constants_C_epsilon_H"
    ] == "OPEN"
    assert payload["hindsight"]["pair_contact_second_variation_criterion"] == (
        "NOT_DERIVED_HERE"
    )
    assert payload["claim_boundary"]["zero_source_force"] == "OPEN"
    assert payload["FULL_BHSM_COMPLETE"] is False
