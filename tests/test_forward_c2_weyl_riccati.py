from __future__ import annotations

import numpy as np

from bhsm.interface.aether_forward_c2_weyl_riccati import (
    finite_core_weyl_and_coefficient_cotangent,
)


def test_scalar_constant_path_matches_coth_solution() -> None:
    x = np.zeros(5)
    h = np.full(4, 0.1)
    result = finite_core_weyl_and_coefficient_cotangent(
        log_radii=x,
        proper_durations=h,
        channel="scalar",
        unit_channel_value=3.0,
        spectral_parameter=-1.0,
    )
    k = 2.0
    expected = k / np.tanh(k * np.sum(h))
    assert np.isclose(result["Weyl_birth_value"], expected, rtol=1.0e-14)
    assert result["Weyl_birth_value_decimal"]
    assert np.all(result["backward_impedance_values"] > 0.0)
    assert result["explicit_matrix_inverse_formed"] is False


def test_reverse_uniform_x_derivative_matches_complex_step() -> None:
    x = np.asarray([0.02, 0.03, 0.01, 0.04])
    h = np.asarray([0.11, 0.07, 0.09])
    base = finite_core_weyl_and_coefficient_cotangent(
        log_radii=x,
        proper_durations=h,
        channel="product_Dirac",
        unit_channel_value=1.5,
        spectral_parameter=-1.0,
        chirality=1,
    )
    epsilon = 1.0e-6
    plus = finite_core_weyl_and_coefficient_cotangent(
        log_radii=x + epsilon, proper_durations=h, channel="product_Dirac",
        unit_channel_value=1.5, spectral_parameter=-1.0, chirality=1,
    )["Weyl_birth_value"]
    minus = finite_core_weyl_and_coefficient_cotangent(
        log_radii=x - epsilon, proper_durations=h, channel="product_Dirac",
        unit_channel_value=1.5, spectral_parameter=-1.0, chirality=1,
    )["Weyl_birth_value"]
    finite = (plus - minus) / (2.0 * epsilon)
    analytic = float(np.sum(base["D_log_R4_node_Weyl"]))
    assert np.isclose(analytic, finite, rtol=2.0e-8, atol=1.0e-9)
