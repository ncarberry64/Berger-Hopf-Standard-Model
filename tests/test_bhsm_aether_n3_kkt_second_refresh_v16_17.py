from bhsm.interface.aether_n3_kkt_second_refresh_v16_17 import (
    v16_16_final_raw_vector,
)


def test_v16_16_state_round_trips_for_second_refresh():
    vector = v16_16_final_raw_vector()
    assert vector.shape == (376,)
    assert vector[-2] > 0.0
