import math

import numpy as np

from bhsm.interface.aether_join_skin_nonlinear_constraint_v15_32 import (
    completion_payload,
    constraint_schur_persistence_theorem,
    deterministic_json,
    join_trace_arrays,
    join_trace_domain_and_jet,
    nonlinear_wall_translation_energy,
    operator_basis_uniqueness_audit,
    physical_skin_spectrum,
    thin_wall_pressure_no_stability_theorem,
)


def test_operator_basis_does_not_fake_uniqueness():
    result = operator_basis_uniqueness_audit()
    assert result["independent_classes_after_IBP"] == 2
    assert result["requirements_in_author_directive_select_unique_operator"] is False


def test_reciprocal_join_trace_is_smooth_and_reflection_symmetric():
    arrays = join_trace_arrays(8001)
    sigma = np.asarray(arrays["sigma"])
    assert np.max(np.abs(sigma + sigma[::-1])) < 1e-11
    assert np.allclose([sigma[0], sigma[-1]], [-0.5, 0.5])


def test_join_trace_jet_and_seam_are_selected():
    result = join_trace_domain_and_jet(16001)
    assert abs(result["median_chi"] - math.pi / 4.0) < 1e-9
    assert abs(result["linear_fit_residual"]) < 1e-5
    assert abs(result["cubic_fit_residual"]) < 3e-4
    assert result["S6_trace_transplant_rejected"]


def test_physical_hessian_has_one_computed_negative_mode():
    result = physical_skin_spectrum(1000)
    assert result["lowest_eigenvalue"] < -14.0
    assert result["negative_mode_count_among_computed"] == 1
    assert result["gauge_mode"] is False


def test_nonlinear_wall_family_runs_to_both_poles():
    result = nonlinear_wall_translation_energy(points=16001)
    assert result["collective_second_variation"] < 0.0
    assert result["energy_decreases_both_directions"]
    assert result["large_shift_energy_approaches_zero"]


def test_constraint_and_pressure_theorems_preserve_instability():
    schur = constraint_schur_persistence_theorem()
    pressure = thin_wall_pressure_no_stability_theorem()
    assert schur["negative_sigma_direction_survives"]
    assert schur["full_constraint_solution_needed_to_decide_stability_sign"] is False
    assert pressure["sign"].startswith("strictly_negative")


def test_payload_reports_no_stable_child_and_passes():
    payload = completion_payload()
    child = payload["encapsulated_child_result"]
    assert payload["validation_passed"]
    assert child["finite_material_skin_stationary_solution"]
    assert child["stable_material_skin"] is False
    assert child["regular_persistent_encapsulated_child"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False


def test_json_is_deterministic_and_finite():
    first = deterministic_json(completion_payload())
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
