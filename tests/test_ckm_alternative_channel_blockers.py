from bhsm.interface.normalized_action_adjoint_pair import audit_ckm_alternative_channel_blockers


def test_alternative_channel_blockers_record_all_dimensions():
    payload = audit_ckm_alternative_channel_blockers()
    rows = {row["id"]: row for row in payload["alternatives"]}
    assert rows["one_way_up_down"]["dimension"] == 8
    assert rows["bidirectional_adjoint_pair"]["dimension"] == 16
    assert rows["maximal_self_response"]["dimension"] == 16
    assert rows["sector_self_response_sum"]["dimension"] == 21
    assert rows["total_charged_endomorphism"]["dimension"] == 49
    assert payload["status"] == "MULTIPLE_COMPETING_CHANNEL_ASSIGNMENTS"


def test_same_dimension_does_not_establish_physical_source():
    payload = audit_ckm_alternative_channel_blockers()
    rows = {row["id"]: row for row in payload["alternatives"]}
    assert rows["maximal_self_response"]["current_status"] == "RETIRED_MAXIMAL_SELF_RESPONSE_AS_PRIMARY_CKM_SOURCE"
    assert "Same numerical dimension does not prove same physical source." == payload["same_dimension_warning"]
    assert "unless action evidence revives it" in payload["claim_boundary"]

