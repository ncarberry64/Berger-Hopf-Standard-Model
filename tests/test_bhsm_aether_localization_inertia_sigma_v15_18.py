from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import sympy as sp

from bhsm.interface.aether_localization_inertia_sigma_v15_18 import (
    CAMPAIGN_OBJECT,
    EXACT_NEXT_OBJECT,
    FULL_BHSM_COMPLETE,
    coefficient_and_contact_audit_payload,
    completion_payload,
    deterministic_json,
    eta_p2_p8_velocity_hessian,
    formation_reduced_dynamics,
    inertia_sigma_jet,
    materialize,
    moving_sigma_zero_selector_jacobian,
    parity_reduction_theorem_payload,
    retained_inertia_matrix,
    sigma_tangent_on_moving_trajectory,
)


ROOT = Path(__file__).resolve().parents[1]


def test_quoted_formation_equation_matches_v15_9_reduced_potential() -> None:
    q, m, ac = 0.31, 0.4, 1.7
    acceleration = 5 * m * q / (6 * ac**2) - 23 * q**3 / (54 * ac**2)
    result = formation_reduced_dynamics(
        q, 0.2, acceleration, supercriticality=m, critical_radius=ac
    )
    assert result["collective_inertia"] == pytest.approx(1.5 * ac**2)
    assert result["Euler_residual"] == pytest.approx(0.0, abs=1e-15)
    assert result["collective_inertia"] * acceleration + result["potential_prime"] == pytest.approx(
        0.0, abs=1e-15
    )


def test_symbolic_retained_inertia_has_no_first_sigma_variation_at_zero() -> None:
    sigma, g, mass, velocity = sp.symbols("sigma g mass velocity", real=True)
    inertia = mass * (1 + g * sigma**2)
    source = sp.diff(inertia, sigma) * velocity**2 / 2
    assert sp.simplify(source.subs(sigma, 0)) == 0
    assert sp.diff(inertia, sigma, 2).subs(sigma, 0) == 2 * g * mass
    assert sp.diff(inertia, sigma, 4) == 0


def test_numeric_inertia_jet_distinguishes_source_from_tangent_shift() -> None:
    jet = inertia_sigma_jet(0.0, 0.7, q_inertia=2.3, g=0.8)
    assert jet["dI_qq_dsigma"] == 0.0
    assert jet["J_sigma_inertia"] == 0.0
    assert jet["d2I_qq_dsigma2"] == pytest.approx(3.68)
    assert jet["linearized_curvature_shift"] == pytest.approx(-0.8 * 2.3 * 0.7**2)


def test_full_p2_p8_velocity_hessian_preserves_sigma_evenness() -> None:
    result = eta_p2_p8_velocity_hessian(
        spatial_gradient_squared=2.0,
        eta_velocity=0.3,
        sigma=0.0,
        kappa1=1.0,
        g=0.8,
    )
    x = 2.0 - 0.3**2
    expected = 1.0 + x**3 - 6.0 * 0.3**2 * x**2
    assert result["velocity_Hessian"] == pytest.approx(expected)
    assert result["d_velocity_Hessian_dsigma"] == 0.0
    assert result["d2_velocity_Hessian_dsigma2"] == pytest.approx(1.6 * expected)
    assert result["inside_positive_Legendre_cone"] is True


def test_motion_can_create_parametric_instability_without_forcing_sigma() -> None:
    stable = sigma_tangent_on_moving_trajectory(
        static_sigma_curvature=2.0, q_dot=0.2, q_inertia=3.0, zsigma=2.0, g=0.5
    )
    unstable = sigma_tangent_on_moving_trajectory(
        static_sigma_curvature=2.0, q_dot=2.0, q_inertia=3.0, zsigma=2.0, g=0.5
    )
    assert stable["parametrically_unstable"] is False
    assert unstable["parametrically_unstable"] is True
    assert unstable["sigma_zero_remains_exact_solution"] is True
    assert unstable["absolute_q_dot_threshold"] == pytest.approx((2.0 / 1.5) ** 0.5)


def test_velocity_hessian_and_parity_reduction() -> None:
    matrix = retained_inertia_matrix(0.3, q_inertia=2.0, zsigma=0.7, g=0.4)
    assert matrix == pytest.approx(np.diag([2.0 * (1 + 0.4 * 0.3**2), 0.7]))
    assert np.min(np.linalg.eigvalsh(matrix)) > 0.0
    parity = parity_reduction_theorem_payload()
    assert parity["physical_inertia_parity"] == "I_phys(-sigma)=I_phys(sigma)"
    assert parity["dI_phys_dsigma_at_zero"] == 0.0
    assert parity["parity_odd_inertia_term_present"] is False


def test_moving_zero_profile_does_not_select_coefficients_or_contact_momentum() -> None:
    assert np.linalg.matrix_rank(moving_sigma_zero_selector_jacobian()) == 0
    audit = coefficient_and_contact_audit_payload()
    assert audit["dynamic_tangent_response"]["selects_r_without_target_response"] is False
    assert audit["gamma"]["selected"] is False
    assert audit["localization_coordinate_ell"]["canonical_momentum"] is None
    assert audit["separation_coordinate_d"]["canonical_momentum"] is None
    assert audit["contact_cross_inertia_I_dq"] is None


def test_completion_preserves_inertial_insight_and_claim_boundary() -> None:
    payload = completion_payload()
    assert FULL_BHSM_COMPLETE is False
    assert payload["validation_passed"] is True
    assert payload["campaign_object"] == CAMPAIGN_OBJECT
    assert payload["moving_sigma_zero_selector"]["rank"] == 0
    assert payload["physical_inertia"]["sigma_jet_at_zero_on_moving_control"][
        "J_sigma_inertia"
    ] == 0.0
    assert payload["contact_momentum_transfer"].startswith("NOT_DERIVED")
    assert EXACT_NEXT_OBJECT.startswith("ACTION_OWNED_M5_M4_LOCALIZATION_INERTIA_KERNEL")


def test_deterministic_materialization_and_repository_artifact(tmp_path: Path) -> None:
    encoded = deterministic_json(completion_payload())
    assert encoded.endswith("\n")
    assert "NaN" not in encoded and "Infinity" not in encoded
    assert json.loads(encoded)["version"] == "v15.18"
    first = materialize(tmp_path / "first")
    second = materialize(tmp_path / "second")
    assert hashlib.sha256(first.read_bytes()).digest() == hashlib.sha256(second.read_bytes()).digest()
    assert first.read_bytes() == (ROOT / "artifacts" / first.name).read_bytes()
