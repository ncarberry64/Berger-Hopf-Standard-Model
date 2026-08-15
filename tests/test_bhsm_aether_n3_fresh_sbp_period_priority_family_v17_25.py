from bhsm.interface.aether_n3_fresh_sbp_period_priority_family_v17_25 import (
    completion_payload,
    v17_23_selected_raw_vector,
)


def test_v17_23_state_has_complete_dimension():
    assert v17_23_selected_raw_vector().shape == (376,)


def test_period_priority_family_validates():
    assert completion_payload()["validation_passed"]
