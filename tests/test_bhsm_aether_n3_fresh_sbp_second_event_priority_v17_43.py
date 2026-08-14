from bhsm.interface.aether_n3_fresh_sbp_second_event_priority_v17_43 import (
    completion_payload,
    v17_42_selected_raw_vector,
)


def test_v17_42_state_has_complete_dimension():
    assert v17_42_selected_raw_vector().shape == (376,)


def test_second_event_priority_validates():
    assert completion_payload()["validation_passed"]
