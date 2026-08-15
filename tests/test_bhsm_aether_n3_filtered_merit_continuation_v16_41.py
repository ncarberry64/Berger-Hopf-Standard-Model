from bhsm.interface.aether_n3_filtered_merit_continuation_v16_41 import FILTER_RELATIVE_SCALES, STEP_FRACTIONS


def test_filtered_bank_grid_is_complete():
    assert len(FILTER_RELATIVE_SCALES) * len(STEP_FRACTIONS) == 28
    assert STEP_FRACTIONS[-1] < 0.0625
