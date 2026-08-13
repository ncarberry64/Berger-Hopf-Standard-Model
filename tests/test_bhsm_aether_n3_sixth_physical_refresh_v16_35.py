import numpy as np

from bhsm.interface.aether_n3_sixth_physical_refresh_v16_35 import v16_34_raw_vector


def test_v16_34_full_precision_state_loads():
    result = v16_34_raw_vector()
    assert result.shape == (376,)
    assert np.all(np.isfinite(result))
