from bhsm.interface.aether_n3_refined_filter_continuation_v16_43 import FILTER_RELATIVE_SCALES, STEP_FRACTIONS


def test_refined_filter_grid_covers_local_trust_region():
    assert 1e-12 in FILTER_RELATIVE_SCALES
    assert min(STEP_FRACTIONS) < 0.015625
