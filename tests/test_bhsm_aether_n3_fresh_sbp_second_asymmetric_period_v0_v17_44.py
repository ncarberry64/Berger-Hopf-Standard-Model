from bhsm.interface.aether_n3_fresh_sbp_second_asymmetric_period_v0_v17_44 import (
    completion_payload,
    v17_43_selected_raw_vector,
)


def test_v17_43_state_has_complete_dimension():
    assert v17_43_selected_raw_vector().shape == (376,)


def test_second_asymmetric_period_v0_validates():
    assert completion_payload()["validation_passed"]
