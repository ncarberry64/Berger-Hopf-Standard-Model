from bhsm.interface.aether_n3_second_projected_cauchy_v16_50 import v16_49_raw_vector


def test_v16_49_state_has_complete_kkt_dimension():
    assert v16_49_raw_vector().shape == (376,)
