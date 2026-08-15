import numpy as np

from bhsm.interface.aether_n3_fourth_physical_refresh_v16_31 import v16_30_raw_vector


def test_v16_30_full_precision_state_loads():
    result = v16_30_raw_vector()
    assert result.shape == (376,)
    assert np.all(np.isfinite(result))
