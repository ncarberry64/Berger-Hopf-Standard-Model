import math

from bhsm.interface.aether_complete_child_localized_fiber_v15_34 import (
    completion_payload,
    deterministic_json,
    enclosed_geometry_partition_theorem,
    fr_antiperiodic_domain_spectrum,
    full_child_tangent_embedding_theorem,
    localized_child_terms,
    localized_inertia_curvature,
    minimal_localized_fiber_completion,
    reduced_child_routhian_solution,
)


def test_skin_translation_is_relative_not_a_radial_gauge_mode():
    result = full_child_tangent_embedding_theorem()
    assert result["common_field_displacement"]["delta_sigma_GI"] == 0.0
    assert result["v15_32_skin_only_tangent"]["delta_sigma_GI"].endswith(
        "nonzero"
    )
    assert result["v15_32_mode_survives_as_complete_field_space_tangent"]


def test_smooth_cap_partition_does_not_invent_interior_pressure():
    result = enclosed_geometry_partition_theorem()
    assert result["first_partition_variation"] == 0.0
    assert result["second_partition_variation"] == 0.0
    assert result["internal_GHY_terms"].startswith("cancel")
    assert result["positive_complement_can_add_positive_curvature"] is False


def test_minimal_localized_factor_has_honest_completion_provenance():
    result = minimal_localized_fiber_completion()
    assert result["unique_solution"] == "Lambda(sigma)=1-4*sigma^2"
    assert result["unique_in_minimal_class"]
    assert result["new_continuous_coefficient"] is False
    assert result["historically_retained_term"] is False


def test_fr_antiperiodic_domain_derives_half_odd_momentum():
    result = fr_antiperiodic_domain_spectrum()
    assert result["boundary_form_vanishes"]
    assert result["lowest_abs_J"] == 0.5
    assert result["lowest_J_squared"] == 0.25
    assert result["lowest_sector_degeneracy"] == 2
    assert result["J_derived_from_domain"]


def test_localized_inertia_has_positive_fixed_charge_curvature():
    result = localized_inertia_curvature(points=12001)
    assert abs(result["I_first_at_seam"]) < 1e-8
    assert result["I_second_at_seam"] < 0.0
    assert result["seam_is_localized_inertia_max"]
    assert result["fixed_charge_curvature_positive"]


def test_fixed_charge_energy_obstructs_both_collapse_limits():
    seam = localized_child_terms(0.0, points=12001)
    flank = localized_child_terms(7.0, points=12001)
    assert seam["localized_inertia"] > flank["localized_inertia"]
    assert flank["cyclic_energy"] > seam["cyclic_energy"]
    assert math.isclose(
        localized_child_terms(-7.0, points=12001)["routhian_potential"],
        flank["routhian_potential"],
        rel_tol=2e-5,
    )


def test_reduced_child_routhian_has_finite_stable_negative_x_branch():
    result = reduced_child_routhian_solution(points=12001)
    assert result["finite_enclosure_minimum"]
    assert result["child_scale_x"] < 0.0
    assert result["child_curvature"] > 0.0
    assert result["omega_squared"] > 0.0
    assert abs(result["stationarity_residual"]) < 2e-4


def test_payload_is_deterministic_and_does_not_overclaim_completion():
    payload = completion_payload()
    assert payload["validation_passed"]
    assert payload["claim_boundary"]["stable_reduced_enclosure_derived"]
    assert payload["claim_boundary"]["physical_persistent_child_derived"] is False
    assert payload["FULL_BHSM_COMPLETE"] is False
    first = deterministic_json(payload)
    second = deterministic_json(completion_payload())
    assert first == second
    assert "NaN" not in first and "Infinity" not in first
