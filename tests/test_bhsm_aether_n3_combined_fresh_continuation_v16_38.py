import numpy as np

from bhsm.interface.aether_n3_combined_fresh_continuation_v16_38 import v16_37_raw_vector


def test_v16_37_full_precision_state_loads():
    result = v16_37_raw_vector()
    assert result.shape == (376,)
    assert np.all(np.isfinite(result))
