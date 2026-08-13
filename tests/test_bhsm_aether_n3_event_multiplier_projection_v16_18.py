from bhsm.interface.aether_n3_event_multiplier_projection_v16_18 import (
    v16_17_final_raw_vector,
)


def test_projection_source_state_dimension():
    assert v16_17_final_raw_vector().shape == (376,)
