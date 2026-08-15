from bhsm.interface.aether_n3_fresh_sbp_second_period_priority_v17_33 import (
    completion_payload,
    v17_31_selected_raw_vector,
)


def test_v17_31_state_has_complete_dimension():
    assert v17_31_selected_raw_vector().shape == (376,)


def test_second_period_priority_validates():
    assert completion_payload()["validation_passed"]
