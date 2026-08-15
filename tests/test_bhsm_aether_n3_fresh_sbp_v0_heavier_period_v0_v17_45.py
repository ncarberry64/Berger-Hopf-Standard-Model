from bhsm.interface.aether_n3_fresh_sbp_v0_heavier_period_v0_v17_45 import (
    PRIORITY_PROFILES, completion_payload, v17_44_selected_raw_vector)

def test_v17_44_state_has_complete_dimension():
    assert v17_44_selected_raw_vector().shape == (376,)

def test_profiles_are_v0_heavier():
    assert len(PRIORITY_PROFILES) == 8
    assert all(period < v0 for period, v0 in PRIORITY_PROFILES)

def test_v0_heavier_period_v0_validates():
    assert completion_payload()["validation_passed"]
