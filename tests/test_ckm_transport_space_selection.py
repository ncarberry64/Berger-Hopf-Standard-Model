from bhsm.interface.ckm_bounded_interface_normalization import audit_ckm_transport_space_selection


def test_transport_selection_and_ckm_exponent_fail_closed():
    payload = audit_ckm_transport_space_selection()
    assert payload["selection_status"] == "OPEN_MISSING_CKM_TRANSPORT_SPACE_SELECTION"
    assert payload["overall_status"] == "MULTIPLE_COMPETING_TRANSPORT_SPACES"
    assert payload["selected_space"] is None
    assert payload["selected_dimension"] is None
    assert payload["ckm_exponent_status"] == "not_derived"
