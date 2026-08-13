import numpy as np

from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import (
    artifact_seed_vector,
    scaled_action_gradient,
)


def test_artifact_seed_has_anchored_kkt_dimension():
    assert artifact_seed_vector().shape == (376,)


def test_scaled_action_gradient_has_base_dimension_and_is_finite():
    raw = artifact_seed_vector()
    from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
        kkt_variable_scales,
    )
    gradient = scaled_action_gradient(
        (raw * kkt_variable_scales())[:-1]
    )
    assert gradient.shape == (375,)
    assert np.all(np.isfinite(gradient))
