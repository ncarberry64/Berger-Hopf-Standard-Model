from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    PRIORITY_PROFILES,
    completion_payload,
    v17_41_selected_raw_vector,
)


def test_v17_41_state_has_complete_dimension():
    assert v17_41_selected_raw_vector().shape == (376,)


def test_profiles_are_bounded_and_v0_weighted():
    assert len(PRIORITY_PROFILES) == 8
    assert all(period <= v0 for period, v0 in PRIORITY_PROFILES)


def test_asymmetric_period_v0_priority_validates():
    assert completion_payload()["validation_passed"]
