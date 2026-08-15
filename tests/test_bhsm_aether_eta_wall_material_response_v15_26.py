from __future__ import annotations

from pathlib import Path

import numpy as np

from bhsm.interface.aether_eta_wall_material_response_v15_26 import (
    CLASSIFICATION,
    analytic_bps_recovery,
    analytic_eta_wall_response,
    collective_completion_gram,
    completed_sigma_action,
    completion_payload,
    diagonal_symmetry_audit,
    exact_gradient_field_redefinition_audit,
    materialize,
    nonexact_orientation_route_audit,
    normalized_eta_probability_response,
    retained_eta_profile_response,
)


def test_analytic_zero_mode_selects_exact_material_kink() -> None:
    s = np.linspace(-12.0, 12.0, 24001)
    response = analytic_eta_wall_response(s)
    assert response["first_order_residual"] < 1.0e-13
    assert response["second_order_residual"] < 1.0e-13


def test_normalized_probability_one_form_has_unit_holonomy() -> None:
    s = np.linspace(-12.0, 12.0, 24001)
    response = normalized_eta_probability_response(s, 1.0 / np.cosh(s))
    assert abs(response["unit_holonomy"] - 1.0) < 1.0e-13
    assert np.allclose(response["endpoint_values"], [-0.5, 0.5], atol=1.0e-13)
    assert response["monotone"]


def test_orientation_reversal_selects_conjugate_sigma_branch() -> None:
    s = np.linspace(-8.0, 8.0, 16001)
    asymmetric_profile = np.exp(-0.5 * (s - 0.7) ** 2)
    response = normalized_eta_probability_response(s, asymmetric_profile)
    assert response["orientation_reversal_residual"] < 1.0e-12


def test_completed_action_uses_existing_normalization_without_free_coefficient() -> None:
    action = completed_sigma_action()
    assert action["classification"] == CLASSIFICATION
    assert not action["new_continuous_coefficient"]
    assert not action["old_bosonic_Path_B_derivation_claimed"]
    assert "nabla_a(alpha_eta^a)" in action["oriented_source_form"]


def test_completed_action_reduces_product_to_diagonal_reflection() -> None:
    symmetry = diagonal_symmetry_audit()
    assert not symmetry["independent_sigma_reversal"]["completed_square_invariant"]
    assert not symmetry["independent_orientation_reversal"]["completed_square_invariant"]
    assert symmetry["diagonal_reversal"]["completed_square_invariant"]


def test_collective_pullback_is_positive_rank_one_and_has_cross_terms() -> None:
    result = collective_completion_gram(dC_dq=0.3, dC_ds=-0.2, zsigma=1.7)
    assert result["positive_semidefinite"]
    assert result["rank"] == 1
    assert result["cross_terms_nonzero_if_profile_moves"]
    assert result["G_qsigma"] != 0.0
    assert result["G_ssigma"] != 0.0
    assert not result["promoted_as_physical_transfer"]


def test_exact_gradient_completion_does_not_fake_bulk_activation() -> None:
    audit = exact_gradient_field_redefinition_audit()
    assert audit["identity"] == "alpha_eta=dC_eta"
    assert audit["closed_path_holonomy"] == 0.0
    assert audit["open_path_transport_is_not_closed_loop_holonomy"]
    assert not audit["irreducible_bulk_q_sigma_transfer_from_this_square"]
    assert not audit["physical_sigma_activation_closed"]


def test_nonexact_eta_hopf_routes_are_exhausted_without_overpromotion() -> None:
    audit = nonexact_orientation_route_audit()
    assert audit["eta_projector_connection"]["curvature_nonzero"]
    assert audit["eta_projector_connection"]["restricted_trace_norm"] < 1.0e-13
    assert not audit["eta_projector_connection"][
        "can_source_singlet_sigma_without_new_contraction_or_coefficient"
    ]
    assert not audit["transgressed_degree_current"]["regular_bulk_sigma_source"]
    assert not audit["relative_Z6_holonomy"]["creates_quadratic_amplitude"]


def test_historical_quartic_is_recovered_only_on_analytic_control() -> None:
    bps = analytic_bps_recovery()
    retained = retained_eta_profile_response(points=6001)
    assert bps["first_order_residual"] < 1.0e-13
    assert bps["historical_coefficients_in_dimensionless_convention"]["A_ST"] == -2.0
    assert bps["historical_coefficients_in_dimensionless_convention"]["G_ST"] == 8.0
    assert not retained["analytic_sech_BPS_profile_is_exact_for_retained_solution"]


def test_completion_payload_keeps_claim_boundary_closed() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["classification"] == CLASSIFICATION
    assert payload["claim_boundary"]["derived_from_existing_BHSM_structure_after_completing_action"]
    assert not payload["claim_boundary"]["derived_from_old_retained_bosonic_action"]
    assert not payload["claim_boundary"]["physical_material_response_selected"]
    assert not payload["claim_boundary"]["nonlinear_material_skin_solved"]
    assert not payload["FULL_BHSM_COMPLETE"]


def test_materialization_is_deterministic(tmp_path: Path) -> None:
    first = materialize(tmp_path).read_bytes()
    second = materialize(tmp_path).read_bytes()
    assert first == second
