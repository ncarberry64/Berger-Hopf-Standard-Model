import numpy as np

from bhsm.interface.aether_n3_post_multirank_refresh_v16_27 import v16_26_raw_vector


def test_v16_26_full_precision_state_loads():
    result = v16_26_raw_vector()
    assert result.shape == (376,)
    assert np.all(np.isfinite(result))
