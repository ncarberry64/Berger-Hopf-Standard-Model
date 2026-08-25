from __future__ import annotations

import math

import pytest

from bhsm.interface.aether_forward_channel_transfer import (
    product_dirac_dirichlet_birth_terminal_weyl_bounds,
    scalar_dirichlet_birth_terminal_weyl_bounds,
)


def test_scalar_constant_comparison_contains_exact_values() -> None:
    duration_lower, duration_upper = 0.2, 0.3
    kappa2, vmax = 1.7, 2.4
    bounds = scalar_dirichlet_birth_terminal_weyl_bounds(
        duration_lower, duration_upper, vmax, kappa2
    )
    exact_lower = math.sqrt(kappa2) / math.tanh(
        math.sqrt(kappa2) * duration_upper
    )
    exact_upper = math.sqrt(kappa2 + vmax) / math.tanh(
        math.sqrt(kappa2 + vmax) * duration_lower
    )
    assert bounds["lower"] == pytest.approx(exact_lower)
    assert bounds["upper"] == pytest.approx(exact_upper)
    assert 0.0 < bounds["lower"] <= bounds["upper"]


def test_scalar_tiny_duration_is_finite() -> None:
    bounds = scalar_dirichlet_birth_terminal_weyl_bounds(
        2.0e-46, 1.0e-45, 3.1, 1.0e16
    )
    assert math.isfinite(bounds["lower"])
    assert math.isfinite(bounds["upper"])
    assert bounds["lower"] == pytest.approx(1.0e45)


def test_product_factorized_bound_is_positive_and_sign_independent() -> None:
    positive = product_dirac_dirichlet_birth_terminal_weyl_bounds(
        0.1, 0.2, 1.5, 1.0
    )
    assert 0.0 < positive["lower"] <= positive["upper"]
    assert positive["lower_log_weight_correction"] == pytest.approx(-1.2)
    assert positive[
        "factorized_form_used_without_superpotential_derivative"
    ] is True


@pytest.mark.parametrize("bad", [0.0, -1.0, math.inf, math.nan])
def test_invalid_duration_rejected(bad: float) -> None:
    with pytest.raises(ValueError):
        scalar_dirichlet_birth_terminal_weyl_bounds(bad, 1.0, 0.0, 1.0)
