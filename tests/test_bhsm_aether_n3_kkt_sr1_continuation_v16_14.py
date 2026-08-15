from bhsm.interface.aether_n3_kkt_sr1_continuation_v16_14 import (
    v16_13_accepted_raw_vector,
)


def test_v16_13_state_round_trips_from_hex():
    vector = v16_13_accepted_raw_vector()
    assert vector.shape == (376,)
    assert vector[-2] > 0.0
