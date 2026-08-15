from bhsm.interface.aether_n3_component_direction_scale_audit_v17_56 import (
    DERIVATIVE_SCALES,
    completion_payload,
)


def test_internal_scale_bracketed():
    assert min(DERIVATIVE_SCALES) < 2e-6 < max(DERIVATIVE_SCALES)


def test_audit_validates():
    assert completion_payload()["validation_passed"]
