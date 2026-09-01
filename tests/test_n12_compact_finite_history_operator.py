from scripts.derive_n12_compact_finite_history_operator import build_payload


def test_compact_finite_history_operator_uses_action_owned_partition() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["endpoint_partition"]["ordered_traces"] == [
        "birth",
        "new_event",
    ]
    assert payload["endpoint_partition"]["endpoint_condition_imposed"] is False
    assert payload["quadratic_action_operator"][
        "full_ill_conditioned_Euler_Dirac_block_inverted"
    ] is False


def test_compact_operator_keeps_common_scale_and_time_quotient_distinct() -> None:
    payload = build_payload()
    quotient = payload["intrinsic_quotient"]
    assert quotient["explicit_hybrid_time_generator_needed_for_force"] is False
    assert quotient["physical_common_scale"] == "RETAINED_WITH_D_x=1"
    assert payload["claim_boundary"]["actual_family_M_C_value"].startswith("OPEN")
