import math

from bhsm.interface.aether_forward_scalar_weyl_enclosures import (
    scalar_compact_radius_weyl_variation_bounds,
    scalar_nonnegative_exterior_weyl_bounds,
)


def test_constant_channel_comparison_extremes() -> None:
    duration = 0.3
    bounds = scalar_nonnegative_exterior_weyl_bounds(duration, 3.0, 1.0)
    assert bounds["lower"] == math.tanh(duration)
    assert bounds["upper"] == 2.0 / math.tanh(2.0 * duration)
    assert bounds["lower"] < bounds["upper"]


def test_compact_radius_variation_bounds_are_finite() -> None:
    bounds = scalar_compact_radius_weyl_variation_bounds(10.0, 3.0, 1.0)
    assert bounds["Poisson_L2_norm_squared_upper"] == 10.0
    assert bounds["first_operator_bound"] == 6.0
    assert bounds["mixed_operator_bound"] == 12.0
    assert bounds["mixed_Weyl_variation_bound"] > bounds[
        "first_Weyl_variation_bound"
    ]
