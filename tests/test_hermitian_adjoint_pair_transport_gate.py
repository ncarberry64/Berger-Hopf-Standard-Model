from bhsm.interface.charged_current_action import audit_hermitian_adjoint_pair_transport_gate


def test_hermitian_adjoint_pair_gate_separates_hc_from_selection():
    payload = audit_hermitian_adjoint_pair_transport_gate()
    assert payload["off_diagonal_map_present"] is True
    assert payload["hermiticity_required"] is True
    assert payload["conjugate_term_required"] is False
    assert payload["normalization_ties_both_terms"] is False
    assert payload["status"] == "OPEN_MISSING_HERMITIAN_ADJOINT_PAIR_TRANSPORT_SPACE"
    assert payload["selected_space"] is None
    assert "does not by itself derive CKM transport-space selection" in payload["claim_boundary"]

