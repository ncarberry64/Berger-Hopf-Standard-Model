from bhsm.interface.aether_n3_projected_cauchy_continuation_v16_49 import CAUCHY_FACTORS


def test_cauchy_factor_grid_brackets_linear_minimizer():
    assert 1.0 in CAUCHY_FACTORS
    assert min(CAUCHY_FACTORS) < 1.0 < max(CAUCHY_FACTORS)
