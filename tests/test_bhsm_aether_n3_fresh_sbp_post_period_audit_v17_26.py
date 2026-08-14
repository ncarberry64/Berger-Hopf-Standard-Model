from bhsm.interface.aether_n3_fresh_sbp_post_period_audit_v17_26 import (
    completion_payload,
    v17_25_selected_raw_vector,
)


def test_v17_25_state_has_complete_dimension():
    assert v17_25_selected_raw_vector().shape == (376,)


def test_post_period_audit_validates():
    assert completion_payload()["validation_passed"]
