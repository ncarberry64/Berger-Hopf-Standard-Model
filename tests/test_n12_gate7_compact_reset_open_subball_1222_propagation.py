from decimal import Decimal

from scripts.certify_n12_gate7_compact_reset_open_subball_1222_propagation import (
    build_payload,
)


def test_decimal_replay_recovers_both_hidden_strict_reserves() -> None:
    payload = build_payload()
    assert payload["validation_passed"] is True
    assert payload["status"] == (
        "NONEMPTY_OPEN_AE2_RESET_QUOTIENT_SUBBALL_PROPAGATED_THROUGH_1222_CORE"
    )
    assert set(payload["exact_transition_replays"]) == {"791", "1064"}
    for replay in payload["exact_transition_replays"].values():
        assert replay["stored_step_replayed_exactly"] is True
        assert replay["selected_allocation_replayed_exactly"] is True
        assert replay["local_radius_replayed_exactly"] is True
        assert replay["branch_replayed_exactly"] is True
        assert Decimal(replay["exact_output_reserve_decimal"]) > 0
        assert replay["directed_output_reserve_lower"] > 0.0


def test_open_72_subball_and_first_jet_propagate_through_core() -> None:
    payload = build_payload()
    subball = payload["open_subball"]
    assert subball["dimension"] == 72
    assert subball["nonempty_and_open_in_reset_quotient"] is True
    assert subball["parameter_radius"] > 0.0
    assert subball["certified_segment_count"] == 1222
    assert subball["minimum_output_reserve_slack_lower"] > 0.0
    assert subball["terminal_quotient_first_jet_singular_value_lower"] > 0.0
    assert payload["adjudication"][
        "nonempty_open_reset_family_through_1222_core"
    ] == "CERTIFIED"
    assert payload["adjudication"]["favorable_reset_member_selected"] is False
    assert payload["adjudication"]["NHIM_capture_or_later_retained_stop"] == (
        "OPEN_CURRENT_OWNER"
    )
    assert payload["FULL_BHSM_COMPLETE"] is False
