import numpy as np

from bhsm.interface.aether_n3_kkt_range_nullspace_audit_v16_21 import (
    v16_20_projected_raw_vector,
)


def test_v16_20_projected_state_is_finite_and_square():
    vector = v16_20_projected_raw_vector()
    assert vector.shape == (376,)
    assert np.all(np.isfinite(vector))
