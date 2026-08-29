from scripts.audit_n12_gate7_compact_reset_propagation_reserve import build_payload


def test_stored_1222_cover_has_exactly_two_zero_reserve_transitions() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "STORED_1222_CORE_PROPAGATED_SET_MAP_FAILS_STRICT_RESERVE_AT_TWO_TRANSITIONS"
    )
    test = payload["propagated_set_test"]
    assert test["segment_count"] == 1222
    assert test["minimum_stored_output_reserve"] == 0.0
    assert [row["global_segment_index"] for row in test["zero_reserve_rows"]] == [
        791,
        1064,
    ]


def test_audit_fails_closed_without_reclassifying_the_dynamics() -> None:
    payload = build_payload()
    adjudication = payload["adjudication"]
    assert adjudication["compact_reset_quotient_domain"] == "CERTIFIED_AND_PRESERVED"
    assert adjudication["pointwise_1222_finite_core"] == "CERTIFIED_AND_PRESERVED"
    assert adjudication["boundary_controlled_propagated_compact_set_map"] == (
        "NOT_CERTIFIED"
    )
    assert adjudication["dynamical_nonexistence_inferred"] is False
    assert adjudication["reset_member_selected"] is False
    assert payload["propagated_set_test"]["minimum_allowable_initial_radius"] == 0.0
    assert payload["propagated_set_test"][
        "minimum_strictly_positive_allowable_initial_radius"
    ] > payload["propagated_set_test"]["derived_open_subball_target_radius"] > 0.0
    assert len(payload["propagated_set_test"][
        "required_new_reserve_at_zero_rows_for_open_subball_target"
    ]) == 2
    assert payload["FULL_BHSM_COMPLETE"] is False
