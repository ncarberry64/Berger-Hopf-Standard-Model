from bhsm.interface.aether_n3_rank_aware_basin_step_v16_24 import SEARCH_RADII


def test_basin_search_brackets_the_measured_minimum():
    assert 400.0 in SEARCH_RADII
    assert min(SEARCH_RADII) < 400.0 < max(SEARCH_RADII)
    assert tuple(sorted(SEARCH_RADII)) == SEARCH_RADII
