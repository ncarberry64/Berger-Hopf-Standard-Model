import numpy as np

from bhsm.interface.aether_n3_rank_aware_trust_step_v16_23 import (
    exact_event_multiplier_projection,
)


def test_event_multiplier_projection_validates_shape():
    with np.testing.assert_raises(ValueError):
        exact_event_multiplier_projection(np.zeros(375))
