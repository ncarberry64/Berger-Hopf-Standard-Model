from bhsm.interface.ckm_channel_equivalence import audit_ckm_channel_counts


def test_all_predeclared_ckm_channel_dimensions_are_exact():
    report = audit_ckm_channel_counts()
    assert (report["N_ud"], report["N_total_end"], report["N_sum_self"], report["N_max_self"]) == (8, 49, 21, 16)
    assert report["max_self_reciprocal"] == "1/16"
    assert report["max_self_reciprocal_exact"] is True
    assert report["selected_N_CKM"] is None
    assert report["status"] == "MULTIPLE_COMPETING_CHANNEL_ASSIGNMENTS"

