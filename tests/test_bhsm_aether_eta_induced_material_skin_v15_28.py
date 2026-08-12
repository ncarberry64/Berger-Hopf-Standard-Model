from __future__ import annotations

from pathlib import Path

import numpy as np

from bhsm.interface.aether_eta_induced_material_skin_v15_28 import (
    CLASSIFICATION,
    completion_payload,
    flat_analytic_control,
    materialize,
    orientation_reversal_theorem,
    potential_uniqueness_theorem,
    retained_material_skin_diagnostics,
)


def test_inverse_euler_map_is_coefficient_free_and_unique_in_scope() -> None:
    theorem = potential_uniqueness_theorem()
    assert "unique" in theorem["uniqueness"]
    assert theorem["constant_selection"].startswith("U_eta(+1/2)=0")
    assert not theorem["new_polynomial_ansatz"]
    assert not theorem["new_continuous_coefficient"]


def test_retained_eta_trace_is_exact_material_solution() -> None:
    skin = retained_material_skin_diagnostics(points=16001)
    assert np.allclose(skin["profile_endpoints"], [-0.5, 0.5], atol=1.0e-12)
    assert skin["maximum_Euler_residual"] < 1.0e-13
    assert abs(skin["U_outside_parent_subtracted"]) < 1.0e-12


def test_material_force_activates_sigma_and_tracks_orientation() -> None:
    skin = retained_material_skin_diagnostics(points=16001)
    reversal = orientation_reversal_theorem()
    assert abs(skin["orientation_odd_force_Uprime_at_sigma_zero"]) > 0.1
    assert skin["potential_reflection_asymmetry"] > 0.01
    assert reversal["source_sign_reverses"]
    assert not reversal["independent_sigma_reflection_is_symmetry_of_fixed_oriented_branch"]
    assert reversal["diagonal_orientation_sigma_reversal_is_symmetry_of_pair"]


def test_derived_enclosure_has_finite_width_pressure_and_tension() -> None:
    skin = retained_material_skin_diagnostics(points=16001)
    assert skin["width_10_to_90"] > skin["width_25_to_75"] > 0.0
    assert skin["pressure_jump_per_Zsigma"] > 0.0
    assert skin["surface_tension_per_Zsigma"] > 0.0
    assert abs(skin["Laplace_identity_residual"]) < 1.0e-12


def test_critical_skin_has_physical_negative_scaling_direction() -> None:
    skin = retained_material_skin_diagnostics(points=16001)
    assert abs(skin["Derrick_virial_5K_plus_7P"]) < 1.0e-4
    assert skin["Derrick_scaling_second_variation_per_Omega6_Zsigma"] < 0.0
    assert skin["physical_negative_enclosure_direction"]
    assert skin["scaling_growth_rate_in_kappa1_one_units"] > 0.0


def test_flat_collar_limit_recovers_historical_quartic_exactly() -> None:
    control = flat_analytic_control()
    assert control["maximum_identity_residual"] < 1.0e-13
    assert control["historical_A_ST"] == -2.0
    assert control["historical_G_ST"] == 8.0


def test_completion_payload_records_fixed_background_boundary() -> None:
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["classification"] == CLASSIFICATION
    assert payload["claim_boundary"]["fixed_eta_background"]
    assert not payload["claim_boundary"]["full_Einstein_eta_sigma_constraints_solved"]
    assert not payload["claim_boundary"]["negative_direction_is_gauge"]
    assert not payload["FULL_BHSM_COMPLETE"]


def test_materialization_is_deterministic(tmp_path: Path) -> None:
    first = materialize(tmp_path).read_bytes()
    second = materialize(tmp_path).read_bytes()
    assert first == second
