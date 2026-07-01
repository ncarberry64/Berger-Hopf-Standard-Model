from bhsm.interface.ckm_bounded_interface_normalization import audit_paired_term_normalization


def test_target_hc_does_not_supply_paired_action_normalization():
    payload = audit_paired_term_normalization()
    assert payload["forward_term_present"] is True
    assert payload["adjoint_term_present"] is True
    assert payload["same_normalization_source"] is False
    assert payload["paired_as_single_action_object"] is False
    assert payload["status"] == "OPEN_MISSING_PAIRED_TERM_NORMALIZATION"
