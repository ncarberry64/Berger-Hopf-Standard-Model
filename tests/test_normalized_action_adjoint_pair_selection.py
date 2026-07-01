from bhsm.interface.normalized_action_adjoint_pair import audit_normalized_action_adjoint_pair_selection


def test_normalized_action_adjoint_pair_selection_counts_and_status():
    payload = audit_normalized_action_adjoint_pair_selection()
    dims = payload["dimension_count"]
    assert dims["dim_V_u"] == 2
    assert dims["dim_V_d"] == 4
    assert dims["dim_Hom_Vu_Vd"] == 8
    assert dims["dim_Hom_Vd_Vu"] == 8
    assert dims["N_CKM_candidate"] == 16
    assert payload["status"] == "OPEN_MISSING_NORMALIZED_ACTION_ADJOINT_PAIR_SELECTION"
    assert payload["selection_rule_proven"] is False
    assert payload["selected_space"] is None
    assert payload["selected_dimension"] is None


def test_adjoint_pair_selection_records_competing_assignments_and_gap():
    payload = audit_normalized_action_adjoint_pair_selection()
    combined = " ".join(payload["competing_assignments"])
    for number in ("8", "16", "21", "49"):
        assert number in combined
    assert "No artifact-backed normalized BHSM action theorem" in payload["proof_gap"]
    assert "conditional channel assignment" in payload["claim_boundary"]

