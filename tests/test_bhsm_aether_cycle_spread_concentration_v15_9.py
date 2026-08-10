from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import sympy as sp

from bhsm.interface.aether_cycle_spread_concentration_v15_9 import (
    EXACT_NEXT_OBJECT,
    FULL_BHSM_COMPLETE,
    PRIMARY_OBJECT,
    USB_REMOVABLE_MEDIA_TOUCHED,
    completion_payload,
    concentration_series_payload,
    critical_radius,
    deterministic_json,
    eta_to_sigma_payload,
    exact_lyapunov_schmidt_payload,
    hopf_identity_hessian_payload,
    identity_hessian_ratio,
    independent_collocation_check,
    materialize,
    non_killing_mode_payload,
    radial_solution_diagnostics,
    schur_response_payload,
    sigma_curvature_root,
    sigma_threshold,
)


ROOT = Path(__file__).resolve().parents[1]


def test_campaign_boundary_and_primary_object() -> None:
    assert FULL_BHSM_COMPLETE is False
    assert USB_REMOVABLE_MEDIA_TOUCHED is False
    assert PRIMARY_OBJECT.startswith("CYCLE_DRIVEN_ETA_SPREAD_TO_CONCENTRATION")
    assert "FULL_HOPF_PARENT_CHILD" in EXACT_NEXT_OBJECT


def test_exact_critical_radius_and_identity_hessian_crossing() -> None:
    kappa1 = 1.7
    radius = critical_radius(kappa1)
    assert radius**6 == pytest.approx(343.0 / (5.0 * kappa1))
    assert identity_hessian_ratio(radius, kappa1) == pytest.approx(0.0, abs=2e-15)
    assert identity_hessian_ratio(0.99 * radius, kappa1) > 0.0
    assert identity_hessian_ratio(1.01 * radius, kappa1) < 0.0


def test_symbolic_normal_form_reproduction() -> None:
    c, alpha, m, q = sp.symbols("c alpha m q", real=True)
    order_q2_residual = -sp.Rational(6, 7) * (108 * c - 19)
    order_q3_projection = sp.Rational(35, 1152) * sp.pi * (45 * alpha - 23)
    reduced_energy = -sp.Rational(5, 8) * m * q**2 + sp.Rational(23, 144) * q**4
    assert sp.solve(order_q2_residual, c) == [sp.Rational(19, 108)]
    assert sp.solve(order_q3_projection, alpha) == [sp.Rational(23, 45)]
    nonzero_stationarity = sp.factor(sp.diff(reduced_energy, q) / q)
    assert sp.solve(nonzero_stationarity, q**2) == [sp.Rational(45, 23) * m]
    assert sp.diff(reduced_energy, q, 2).subs(q**2, sp.Rational(45, 23) * m) == sp.Rational(5, 2) * m


def test_exact_series_payload_has_reproduced_rationals() -> None:
    payload = exact_lyapunov_schmidt_payload()
    assert payload["complement_coefficient_c"] == "19/108"
    assert payload["radius_relation_alpha"] == "23/45"
    assert payload["reduced_energy_q4"] == "23/144"
    assert payload["bifurcation"].startswith("SUPERCRITICAL")


def test_concentration_and_depleted_support_series_are_exact() -> None:
    payload = concentration_series_payload()
    assert payload["C_eta_q2"] == "49/8"
    assert payload["C_eta_radius_coefficient"] == "2205/184"
    assert payload["depleted_pole_q2"] == "73/54"
    assert payload["primitive_Aether_density_claimed"] is False


@pytest.mark.parametrize("modes", (4, 8, 12))
def test_below_crossing_returns_to_identity(modes: int) -> None:
    diagnostics = radial_solution_diagnostics(0.99, modes)
    assert abs(diagnostics["q_fourier"]) < 1e-9
    assert diagnostics["degree"] == pytest.approx(1.0, abs=2e-12)


@pytest.mark.parametrize("ratio", (1.001, 1.01, 1.04))
def test_full_radial_branch_is_nonuniform_degree_one_and_stable(ratio: float) -> None:
    diagnostics = radial_solution_diagnostics(ratio, 12)
    assert diagnostics["q_fourier"] > 0.0
    assert diagnostics["C_eta"] > 1.0
    assert diagnostics["degree"] == pytest.approx(1.0, abs=2e-12)
    assert diagnostics["galerkin_residual_inf"] < 2e-10
    assert diagnostics["pointwise_weighted_Euler_residual_inf"] < 3e-8
    assert diagnostics["radial_coefficient_hessian_positive"] is True


def test_small_branch_matches_lyapunov_schmidt_amplitude() -> None:
    diagnostics = radial_solution_diagnostics(1.001, 12)
    relative_error = abs(
        diagnostics["q_fourier"] / diagnostics["q_leading_prediction"] - 1.0
    )
    assert relative_error < 0.002


def test_independent_collocation_reproduces_variational_branch() -> None:
    check = independent_collocation_check(1.01, 12)
    assert check["converged"] is True
    assert check["profile_difference_from_Fourier_inf"] < 1e-7
    assert check["first_order_equation_residual_inf"] < 1e-7
    assert check["boundary_residual_inf"] < 1e-10


@pytest.mark.parametrize("alpha", (-2.0, -1.0, -0.25))
def test_sigma_threshold_is_continued_on_actual_eta_branch(alpha: float) -> None:
    root = sigma_curvature_root(alpha)
    assert alpha + root + 1.25 * root**4 == pytest.approx(0.0, abs=2e-13)
    threshold = sigma_threshold(alpha)
    assert threshold["continued_radius_ratio_six"] > 1.0
    assert abs(threshold["sigma_curvature_residual"]) < 1e-8
    assert threshold["classification"].endswith("UNSELECTED_ALPHA")


def test_sigma_result_is_not_promoted_past_its_action_provenance() -> None:
    payload = eta_to_sigma_payload()
    assert "independent_theory_inputs" in payload["coefficient_selection_evidence"]
    assert payload["physical_alpha_selected_by_action"] is False
    assert payload["coupled_eta_sigma_metric_branch_solved"] is False
    assert payload["formation_promoted"] is False


def test_eta_only_hopf_sector_is_strictly_positive_but_scope_limited() -> None:
    payload = hopf_identity_hessian_payload()
    assert payload["kernel"] is None
    assert payload["verdict"].startswith("NO_ETA_ONLY_HOPF")
    assert payload["scope"] == "HOPF_COHOMOGENEITY_ONE_ETA_ONLY_IDENTITY_BRANCH"
    assert payload["radial_S6_level_surface_identified_with_Hopf_seam"] is False


def test_non_killing_l2_mode_spectrum_and_moments() -> None:
    payload = non_killing_mode_payload()
    assert payload["first_non_Killing_k"] == 2
    assert payload["candidate_constraint_reduced_frequency_squared"] == "21/a^2"
    assert payload["mean_norm_squared"] == "1/40"
    assert payload["mean_norm_fourth"] == "1/560"
    assert payload["participation_ratio"] == "20/7"
    assert np.sqrt(21.0) > 0.0


def test_positive_response_schur_order_preserves_parent_instability() -> None:
    payload = schur_response_payload()
    assert payload["order"] == "H_eff<=H_eta_in_quadratic_form_order"
    assert payload["assumption"].startswith("H_response_positive")
    assert payload["new_branch_full_coupled_stability"].startswith("OPEN")


def test_completion_payload_passes_without_false_completion() -> None:
    payload = completion_payload()
    assert payload["validation_passed"] is True
    assert all(payload["validation"].values())
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["formation_status"].endswith("OPEN")
    assert payload["persistence_status"].startswith("OPEN")
    assert payload["no_retuning_certificate"]["new_fields"] == []
    assert payload["no_retuning_certificate"]["new_continuous_physical_parameters"] == []


def test_json_is_strict_and_deterministic(tmp_path: Path) -> None:
    encoded = deterministic_json(completion_payload())
    assert encoded.endswith("\n")
    assert "NaN" not in encoded
    assert json.loads(encoded)["version"] == "v15.9"
    first = materialize(tmp_path / "a")
    second = materialize(tmp_path / "b")
    assert hashlib.sha256(first.read_bytes()).digest() == hashlib.sha256(second.read_bytes()).digest()


def test_committed_artifact_matches_materializer(tmp_path: Path) -> None:
    generated = materialize(tmp_path)
    committed = ROOT / "artifacts" / generated.name
    assert generated.read_bytes() == committed.read_bytes()
