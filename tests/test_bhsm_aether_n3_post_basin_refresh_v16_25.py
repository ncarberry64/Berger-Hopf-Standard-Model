import numpy as np

from bhsm.interface.aether_n3_post_basin_refresh_v16_25 import v16_24_raw_vector


def test_v16_24_full_precision_state_loads():
    result = v16_24_raw_vector()
    assert result.shape == (376,)
    assert np.all(np.isfinite(result))
