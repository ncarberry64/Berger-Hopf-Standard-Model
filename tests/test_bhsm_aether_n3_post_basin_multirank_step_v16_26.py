from bhsm.interface.aether_n3_post_basin_multirank_step_v16_26 import (
    RELATIVE_CUTOFFS,
    STEP_FRACTIONS,
)


def test_multirank_probe_is_complete_and_ordered():
    assert RELATIVE_CUTOFFS == tuple(sorted(RELATIVE_CUTOFFS, reverse=True))
    assert STEP_FRACTIONS == tuple(sorted(STEP_FRACTIONS, reverse=True))
    assert len(RELATIVE_CUTOFFS) * len(STEP_FRACTIONS) == 20
