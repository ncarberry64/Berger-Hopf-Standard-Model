import numpy as np

from bhsm.interface.aether_n3_fifth_physical_refresh_v16_33 import v16_32_raw_vector


def test_v16_32_full_precision_state_loads():
    result = v16_32_raw_vector()
    assert result.shape == (376,)
    assert np.all(np.isfinite(result))
