from bhsm.interface.aether_n3_terminal_scale_range_defect_v16_20 import (
    v16_19_final_raw_vector,
)


def test_v16_19_state_dimension():
    assert v16_19_final_raw_vector().shape == (376,)
