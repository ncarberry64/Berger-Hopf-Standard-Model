from bhsm.interface.ckm_bidirectional_channel import audit_ckm_channel_alternative_resolution


def test_bidirectional_and_maximal_self_are_distinct_candidate_sources():
    report = audit_ckm_channel_alternative_resolution()
    rows = {row["id"]: row for row in report["rows"]}
    assert rows["bidirectional_adjoint_pair"]["dimension"] == 16
    assert rows["maximal_self_response"]["dimension"] == 16
    assert rows["bidirectional_adjoint_pair"]["interpretation"] != rows["maximal_self_response"]["interpretation"]
    assert rows["maximal_self_response"]["status"] == "RETIRED_MAXIMAL_SELF_RESPONSE_AS_PRIMARY_CKM_SOURCE"
    assert report["theorem_level_unique_assignment"] is None
    assert report["status"] == "MULTIPLE_COMPETING_CHANNEL_ASSIGNMENTS"

