from bhsm.interface.aether_n3_adaptive_spectral_continuation_v16_42 import v16_41_raw_vector


def test_v16_41_state_has_complete_kkt_dimension():
    assert v16_41_raw_vector().shape == (376,)
