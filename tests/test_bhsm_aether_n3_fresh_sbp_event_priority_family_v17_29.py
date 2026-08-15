from bhsm.interface.aether_n3_fresh_sbp_event_priority_family_v17_29 import (
    completion_payload,
    v17_27_selected_raw_vector,
)


def test_v17_27_state_has_complete_dimension():
    assert v17_27_selected_raw_vector().shape == (376,)


def test_event_priority_family_validates():
    assert completion_payload()["validation_passed"]
