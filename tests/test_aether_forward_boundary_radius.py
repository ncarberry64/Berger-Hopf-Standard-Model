import math

import numpy as np

from bhsm.interface.aether_diagonal_sp1_m4_attachment_v15_50 import RADIUS0
from bhsm.interface.aether_forward_boundary_radius import (
    boundary_log_lapse,
    boundary_log_radius,
    boundary_log_radius_jets,
    proper_time_log_radius_rate,
)


def test_round_origin_has_the_physical_m4_reference_radius() -> None:
    q = np.zeros(37)
    assert abs(math.exp(boundary_log_radius(12, q)) - RADIUS0 / 2.0) < 1e-15


def test_boundary_radius_action_jets_include_direction_curvature() -> None:
    rng = np.random.default_rng(17)
    q = 0.1 * rng.normal(size=37)
    h = rng.normal(size=37)
    k = rng.normal(size=37)
    ell = rng.normal(size=37)
    jets = boundary_log_radius_jets(12, q, h, k, ell)
    eps = 2.0e-4

    def value(left: float, right: float) -> float:
        return boundary_log_radius(
            12, q + left * h + right * k + left * right * ell
        )

    first = (value(1e-6, 0.0) - value(-1e-6, 0.0)) / 2e-6
    mixed = (
        value(eps, eps)
        - value(eps, -eps)
        - value(-eps, eps)
        + value(-eps, -eps)
    ) / (4.0 * eps**2)
    assert abs(float(jets["first_left"]) - first) < 1e-8
    assert abs(float(jets["mixed_second"]) - mixed) < 1e-6


def test_proper_time_rate_uses_positive_boundary_lapse() -> None:
    q = np.zeros(37)
    velocity = np.zeros(37)
    velocity[0] = 0.3
    multipliers = np.zeros(24)
    multipliers[0] = -0.2
    log_lapse = boundary_log_lapse(12, multipliers)
    expected = 0.3 / math.exp(log_lapse)
    assert abs(proper_time_log_radius_rate(12, q, velocity, multipliers) - expected) < 1e-15
