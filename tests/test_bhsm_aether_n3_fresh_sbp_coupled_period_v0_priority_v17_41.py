from bhsm.interface.aether_n3_fresh_sbp_coupled_period_v0_priority_v17_41 import (
    completion_payload,
    v17_39_selected_raw_vector,
)


def test_v17_39_state_has_complete_dimension():
    assert v17_39_selected_raw_vector().shape == (376,)


def test_coupled_period_v0_priority_validates():
    assert completion_payload()["validation_passed"]
