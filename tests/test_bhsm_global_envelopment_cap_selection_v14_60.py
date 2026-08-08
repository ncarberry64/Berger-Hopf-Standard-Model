from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from bhsm.interface.completion.global_envelopment_cap_selection_v14_60 import (
    EXACT_NEXT_OBJECT,
    EnvelopmentParameters,
    action_components,
    action_gradient,
    artifact_payloads,
    completion_gate_payload,
    degeneracy_lift_certificate,
    galerkin_convergence_payload,
    global_functional_payload,
    global_linear_system,
    interior_mode,
    materialize,
    physical_readiness_payload,
    profile_basis,
    profile_polynomial,
    seam_output_certificate,
    seam_signature,
    solve_global_stationary,
    strict_convexity_certificate,
    validate_parameters,
)


def test_interior_modes_are_invisible_to_center_and_seam_cauchy_data() -> None:
    for index in range(8):
        mode = interior_mode(index)
        derivative = mode.deriv()
        assert mode(0.0) == pytest.approx(0.0, abs=1e-14)
        assert derivative(0.0) == pytest.approx(0.0, abs=1e-14)
        assert mode(1.0) == pytest.approx(0.0, abs=1e-14)
        assert derivative(1.0) == pytest.approx(0.0, abs=1e-14)


def test_profile_basis_contains_independent_seam_value_and_slope_modes() -> None:
    basis = profile_basis(4)
    value_mode, slope_mode = basis[:2]
    assert value_mode(1.0) == pytest.approx(1.0)
    assert value_mode.deriv()(1.0) == pytest.approx(0.0, abs=1e-14)
    assert slope_mode(1.0) == pytest.approx(0.0, abs=1e-14)
    assert slope_mode.deriv()(1.0) == pytest.approx(1.0)


def test_global_hessian_is_symmetric_positive_definite() -> None:
    hessian, _, _, _ = global_linear_system(EnvelopmentParameters())
    assert np.linalg.norm(hessian - hessian.T) < 1e-13
    assert np.min(np.linalg.eigvalsh(hessian)) > 0.0


def test_stationary_solution_has_small_residual() -> None:
    solution = solve_global_stationary()
    assert solution["stationarity_residual"] < 1e-12
    assert solution["min_hessian_eigenvalue"] > 0.0
    assert 0.0 < solution["nesting_ratio"] < 1.0


def test_action_gradient_vanishes_at_stationary_solution() -> None:
    solution = solve_global_stationary()
    gradient = action_gradient(solution["solution"])
    assert np.linalg.norm(gradient) < 1e-12


def test_seam_coordinates_equal_actual_profile_cauchy_outputs() -> None:
    solution = solve_global_stationary()
    profile = profile_polynomial(solution["profile_coordinates"], solution["basis"])
    signature = seam_signature(profile)
    assert signature["center_value"] == pytest.approx(0.0, abs=1e-14)
    assert signature["center_slope"] == pytest.approx(0.0, abs=1e-14)
    assert signature["seam_value"] == pytest.approx(solution["seam_value"], abs=1e-12)
    assert signature["seam_slope"] == pytest.approx(solution["seam_slope"], abs=2e-12)


def test_local_seam_degeneracy_is_lifted_by_global_action() -> None:
    payload = degeneracy_lift_certificate()
    assert payload["same_center_and_seam_Cauchy_data"] is True
    assert payload["max_abs_signature_difference"] < 1e-12
    assert payload["global_action_distinguishes_profiles"] is True
    assert payload["global_action_rise"] > 0.0
    assert payload["alternative_gradient_norm"] > 1e-6


def test_quadratic_action_rise_identity_is_exact_numerically() -> None:
    payload = degeneracy_lift_certificate()
    assert payload["quadratic_identity_residual"] < 5e-13


def test_action_components_sum_to_total() -> None:
    solution = solve_global_stationary()
    components = action_components(solution["solution"])
    subtotal = sum(value for key, value in components.items() if key != "total")
    assert subtotal == pytest.approx(components["total"], abs=1e-13)


def test_strict_convexity_certificate_is_fail_closed_about_physical_action() -> None:
    payload = strict_convexity_certificate()
    assert payload["hessian_positive_definite"] is True
    assert payload["unique_stationary_solution_in_reduced_class"] is True
    assert payload["full_BHSM_global_hessian_proved_positive"] is False
    assert payload["physical_uniqueness_claimed"] is False


def test_seam_is_output_not_prescribed_in_reduced_global_solver() -> None:
    payload = seam_output_certificate()
    assert payload["seam_prescribed_before_global_variation"] is False
    assert payload["cosmological_R_H_inserted_as_physical_number"] is False
    assert payload["physical_seam_claimed"] is False


def test_galerkin_harness_remains_stationary_and_positive() -> None:
    payload = galerkin_convergence_payload(8)
    assert payload["stationary_solution_computable_at_all_resolutions"] is True
    assert payload["positive_reduced_hessian_at_all_resolutions"] is True
    assert payload["last_profile_error"] == pytest.approx(0.0, abs=1e-15)
    assert payload["physical_continuum_convergence_claimed"] is False


def test_functional_payload_is_deterministic_and_nonphysical() -> None:
    first = global_functional_payload()
    second = global_functional_payload()
    assert first == second
    assert first["strictly_convex_reduced_functional"] is True
    assert first["physical_BHSM_coefficients_derived"] is False
    assert first["physical_cap_selected"] is False
    assert first["physical_prediction_emitted"] is False


def test_parameter_validation_fail_closed() -> None:
    with pytest.raises(ValueError):
        validate_parameters(EnvelopmentParameters(mu2=0.0))
    with pytest.raises(ValueError):
        validate_parameters(EnvelopmentParameters(global_budget_weight=-1.0))
    with pytest.raises(ValueError):
        validate_parameters(EnvelopmentParameters(interior_modes=0))


def test_physical_readiness_remains_false() -> None:
    payload = physical_readiness_payload()
    assert payload["mathematical_global_selection_mechanism_valid"] is True
    assert payload["physical_global_cap_selection_valid"] is False
    assert payload["checks"]["global_envelopment_variational_architecture_formulated"] is True
    assert payload["checks"]["actual_unified_BHSM_coefficients_inserted"] is False
    assert payload["checks"]["full_global_physical_hessian_non_degenerate"] is False
    assert payload["physical_prediction_emitted"] is False


def test_completion_gate_records_conceptual_lift_but_not_completion() -> None:
    gate = completion_gate_payload()
    assert gate["v14_59_conceptual_roadblock"] == "LIFTED_IN_REDUCED_GLOBAL_VARIATIONAL_CLASS"
    assert gate["v14_59_physical_cap_roadblock"] == "OPEN_UNTIL_FULL_ACTION_GLOBAL_HESSIAN_IS_DERIVED"
    assert gate["full_BHSM_complete"] is False
    assert gate["mark_III"] == "NOT_REACHED"
    assert gate["usb_touched"] is False
    assert gate["exact_next_object"] == EXACT_NEXT_OBJECT


def test_artifact_materialization_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    paths_first = materialize(first)
    paths_second = materialize(second)
    assert len(paths_first) == len(paths_second) == len(artifact_payloads()) == 7
    for a, b in zip(paths_first, paths_second):
        assert a.name == b.name
        assert a.read_bytes() == b.read_bytes()
        json.loads(a.read_text(encoding="utf-8"))
