from bhsm.interface.ckm_channel_equivalence import audit_alternative_channel_assignments


def test_competing_channel_assignments_are_reported_not_hidden():
    report = audit_alternative_channel_assignments()
    assert [row["dimension"] for row in report["rows"]] == [8, 49, 21, 16]
    assert all(row["excluded"] is False for row in report["rows"])
    assert report["unique_surviving_assignment"] is None
    assert report["status"] == "MULTIPLE_COMPETING_CHANNEL_ASSIGNMENTS"
