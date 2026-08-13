import numpy as np

from bhsm.interface.aether_n3_third_physical_refresh_v16_29 import v16_28_raw_vector


def test_v16_28_full_precision_state_loads():
    result = v16_28_raw_vector()
    assert result.shape == (376,)
    assert np.all(np.isfinite(result))
