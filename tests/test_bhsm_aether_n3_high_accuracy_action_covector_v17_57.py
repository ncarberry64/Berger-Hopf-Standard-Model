from bhsm.interface.aether_n3_high_accuracy_action_covector_v17_57 import (
    COORDINATE_RELATIVE_STEP,
    completion_payload,
)


def test_coordinate_step_is_above_legacy_noise_scale():
    assert COORDINATE_RELATIVE_STEP > 2e-6


def test_validates():
    assert completion_payload()["validation_passed"]
