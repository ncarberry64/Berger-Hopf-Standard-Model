from bhsm.interface.aether_n3_kkt_refreshed_curvature_v16_16 import (
    v16_15_final_raw_vector,
)


def test_v16_15_state_has_nonzero_event_multiplier():
    vector = v16_15_final_raw_vector()
    assert vector.shape == (376,)
    assert vector[-1] != 0.0
