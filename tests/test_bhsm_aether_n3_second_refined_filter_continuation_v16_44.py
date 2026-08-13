from bhsm.interface.aether_n3_second_refined_filter_continuation_v16_44 import v16_43_raw_vector


def test_v16_43_state_has_complete_kkt_dimension():
    assert v16_43_raw_vector().shape == (376,)
