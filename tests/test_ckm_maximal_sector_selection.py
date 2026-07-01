from bhsm.interface.ckm_channel_equivalence import audit_maximal_sector_selection


def test_maximal_sector_is_not_selected_without_action_rule():
    report = audit_maximal_sector_selection()
    assert report["status"] == "OPEN_MISSING_MAXIMAL_SECTOR_CKM_SELECTION_RULE"
    assert report["candidate_status"] == "CONDITIONAL_MAXIMAL_SECTOR_CKM_SELECTION"
    assert report["selection_rule_proven"] is False
    assert report["selected_N_CKM"] is None
    assert len(report["competing_assignments"]) == 4

