from bhsm.interface.aether_n3_event_log_curvature_compensated_v17_53 import (
    COMPENSATOR_RADII,
    EVENT_ROOT_FRACTIONS,
    completion_payload,
)


def test_bounded_grid():
    assert len(EVENT_ROOT_FRACTIONS) == 7
    assert len(COMPENSATOR_RADII) == 11


def test_validates():
    assert completion_payload()["validation_passed"]
