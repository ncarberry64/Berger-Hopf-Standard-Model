"""Dual-pairing and geometry checks for direct raw Euler--Lagrange caps."""

from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import tighten_n12_current_dop853_rhs_raw_source_caps as direct


def test_raw_output_dual_legs_reproduce_the_source_formula() -> None:
    q = np.linspace(1, 10, 37)
    reduced = np.r_[np.ones(37), np.linspace(1, 4, 24)]
    weights = np.r_[q, reduced]
    G, M = direct._output_legs(weights, q, reduced)
    generator = np.random.default_rng(347)
    gradient = generator.normal(size=98)
    hessian = generator.normal(size=(98, 98))
    hessian = (hessian + hessian.T) / 2
    velocity = generator.normal(size=37)
    configuration = np.r_[q * velocity, np.zeros(61)]
    normalized_gradient = gradient / weights
    normalized_hessian = hessian / weights[:, None] / weights[None, :]
    expected = reduced * (np.r_[q * normalized_gradient[:37], np.zeros(24)] - normalized_hessian[37:, :37] @ configuration[:37])
    actual = G.T @ normalized_gradient - M.T @ normalized_hessian @ configuration
    np.testing.assert_allclose(actual, expected, rtol=1e-13, atol=1e-13)


def test_projection_only_rebuild_matches_retained_source_geometry() -> None:
    current = direct.current
    current._initialize({"inverse": str(current.DEFAULT_INVERSE), "projector": str(current.DEFAULT_PROJECTOR), "center": str(current.DEFAULT_CENTER)})
    rebuilt_center, rebuilt_projection = direct._geometry_only(0, 0, 8)
    existing = current._same_center_tangent_geometry(0, 0, 8)
    np.testing.assert_array_equal(rebuilt_center, existing["midpoint"])
    np.testing.assert_array_equal(rebuilt_projection, existing["projection"])
