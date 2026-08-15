from bhsm.interface.aether_n3_oriented_projected_cauchy_v16_51 import REDUCTION_MARGIN


def test_strict_reduction_margin_excludes_roundoff_zero_steps():
    assert REDUCTION_MARGIN > 1e-12
