from bhsm.interface.aether_n3_strong_damping_continuation_v16_47 import FILTER_RELATIVE_SCALES, STEP_FRACTIONS


def test_strong_damping_grid_extends_v16_46_search():
    assert min(FILTER_RELATIVE_SCALES) == 1e-8
    assert max(FILTER_RELATIVE_SCALES) == 1e-6
    assert len(FILTER_RELATIVE_SCALES) * len(STEP_FRACTIONS) == 25
