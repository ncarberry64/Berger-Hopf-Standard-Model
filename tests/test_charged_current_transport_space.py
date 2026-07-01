from bhsm.interface.charged_current_action import audit_charged_current_transport_space


def test_charged_current_transport_space_records_competing_assignments():
    payload = audit_charged_current_transport_space()
    spaces = {row["space_id"]: row for row in payload["spaces"]}
    assert spaces["one_way_up_down"]["dimension"] == 8
    assert spaces["hermitian_adjoint_pair"]["dimension"] == 16
    assert spaces["sector_self_response_sum"]["dimension"] == 21
    assert spaces["total_charged_endomorphism"]["dimension"] == 49
    assert spaces["maximal_self_response"]["dimension"] == 16
    assert spaces["maximal_self_response"]["current_status"] == "RETIRED_MAXIMAL_SELF_RESPONSE_AS_PRIMARY_CKM_SOURCE"


def test_charged_current_transport_space_selection_depends_on_action_evidence():
    payload = audit_charged_current_transport_space()
    assert payload["status"] == "MULTIPLE_COMPETING_TRANSPORT_SPACES"
    assert payload["transport_space_status"] == "OPEN_MISSING_CHARGED_CURRENT_TRANSPORT_SPACE"
    assert payload["selected_space"] is None
    assert payload["selected_dimension"] is None
    assert "not arithmetic channel-count coincidence" in payload["claim_boundary"]

