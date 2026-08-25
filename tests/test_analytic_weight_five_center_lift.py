import mpmath as mp

from bhsm.interface.analytic_weight_five_center_lift import (
    assemble_weight_five_lift,
)


def test_analytic_local_block_lift_is_high_precision_and_sign_stable():
    result = assemble_weight_five_lift(points=48, decimal_digits=60)
    assert result["relative_residual"] < mp.mpf("1e-50")
    assert result["q0_coefficient"] > 0
    assert result["q0_rate_coefficient"] < 0
