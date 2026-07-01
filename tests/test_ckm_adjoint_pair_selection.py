from bhsm.interface.ckm_bidirectional_channel import audit_ckm_adjoint_pair_selection


def test_adjoint_pair_selection_remains_open_without_action_rule():
    report = audit_ckm_adjoint_pair_selection()
    assert report["status"] == "OPEN_MISSING_CKM_ADJOINT_PAIR_SELECTION_RULE"
    assert report["candidate_status"] == "CONDITIONAL_CKM_ADJOINT_PAIR_SELECTION"
    assert report["selection_rule_proven"] is False
    assert report["selected_N_CKM"] is None
    assert report["evidence_for_adjoint_pair"]
    assert report["artifact_limitations"]

