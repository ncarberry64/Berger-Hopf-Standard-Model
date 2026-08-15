from bhsm.interface.aether_n3_fresh_sbp_log_scale_priority_family_v17_27 import (
    completion_payload,
)
from bhsm.interface.aether_n3_fresh_sbp_post_period_audit_v17_26 import (
    v17_25_selected_raw_vector,
)


def test_v17_25_state_has_complete_dimension():
    assert v17_25_selected_raw_vector().shape == (376,)


def test_log_scale_priority_family_validates():
    assert completion_payload()["validation_passed"]
