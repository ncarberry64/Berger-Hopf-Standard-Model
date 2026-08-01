from bhsm.interface.envelopment import spacetime_removal_depth_v10_3 as depth


def test_depth_candidates_are_not_coordinate_or_duplicate_core_mode():
    payload = depth.depth_payload()
    rows = {row["candidate"]: row for row in payload["candidate_audit"]}
    assert rows["lapse degeneration"]["gauge_invariant"] is False
    assert rows["fiber-volume deficit -3 delta beta"]["distinct_from_q_C"] is False
    assert rows["R_ABCD R^ABCD concentration"]["monotonic_removal"] is False


def test_missing_depth_fails_closed_without_value():
    payload = depth.depth_payload()
    assert payload["selected_depth_functional"] is None
    assert payload["physical_depth_value"] is None
    assert payload["verdict"] == "BHSM_SPACETIME_REMOVAL_DEPTH_REQUIRES_A_NEW_ACTION_OWNED_DEGREE"
