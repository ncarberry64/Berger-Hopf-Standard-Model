from bhsm.interface.aether_n3_targeted_filter_continuation_v16_46 import FILTER_RELATIVE_SCALES, STEP_FRACTIONS


def test_targeted_grid_is_centered_on_v16_44_winner():
    assert 1e-9 in FILTER_RELATIVE_SCALES
    assert 0.03125 in STEP_FRACTIONS
    assert len(FILTER_RELATIVE_SCALES) * len(STEP_FRACTIONS) == 9
