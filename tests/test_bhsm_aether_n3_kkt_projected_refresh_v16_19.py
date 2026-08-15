from bhsm.interface.aether_n3_kkt_projected_refresh_v16_19 import (
    v16_18_projected_raw_vector,
)


def test_v16_18_projected_state_round_trips():
    vector = v16_18_projected_raw_vector()
    assert vector.shape == (376,)
    assert vector[-1] > 1.0
