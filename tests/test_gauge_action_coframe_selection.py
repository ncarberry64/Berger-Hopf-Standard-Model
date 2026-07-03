from bhsm.interface.berger_hodge_component_map.coframe_basis_selection import audit_coframe_basis_selection

def test_action_coframe_selection_remains_open():
    assert audit_coframe_basis_selection()["status"] == "OPEN_MISSING_GAUGE_ACTION_COFRAME_SELECTION"
