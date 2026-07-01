from bhsm.interface.normalized_action_adjoint_pair import search_normalized_action_adjoint_pair_sources


def test_normalized_action_adjoint_pair_source_search_records_required_fields():
    payload = search_normalized_action_adjoint_pair_sources()
    assert payload["files_scanned"] > 0
    assert payload["hits"]
    assert payload["evidence_for_adjoint_pair"]
    assert payload["evidence_for_normalized_action_rule"]
    assert payload["evidence_against_action_derivation"]
    assert payload["missing_sources"]
    assert payload["status"] == "OPEN_MISSING_NORMALIZED_ACTION_ADJOINT_PAIR_SELECTION"


def test_source_search_keeps_empirical_inputs_out():
    payload = search_normalized_action_adjoint_pair_sources()
    assert payload["empirical_inputs_used"] is False
    assert payload["forbidden_theorem_inputs_used"] == []
    assert payload["ckm_fitting_used"] is False
    assert payload["pdg_reference_values_used"] is False

