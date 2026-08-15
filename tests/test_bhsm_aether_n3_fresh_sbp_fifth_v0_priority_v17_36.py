from bhsm.interface.aether_n3_fresh_sbp_fifth_v0_priority_v17_36 import (
    completion_payload,
    v17_34_selected_raw_vector,
)


def test_v17_34_state_has_complete_dimension():
    assert v17_34_selected_raw_vector().shape == (376,)


def test_fifth_v0_priority_validates():
    assert completion_payload()["validation_passed"]
