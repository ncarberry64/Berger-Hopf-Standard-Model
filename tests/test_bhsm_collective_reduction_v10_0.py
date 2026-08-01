from __future__ import annotations

import math

from bhsm.interface.envelopment import collective_reduction as reduction


def test_scaling_powers_follow_spatial_dimension_seven():
    row = reduction.scaling_derivation()
    assert row["spatial_dimension"] == 7
    assert row["eta_p2"] == "R^5"
    assert row["eta_p8"] == "R^-1"
    assert row["sigma_quartic_potential"] == "s^4 R^7"
    assert row["derived_from_action"] is True


def test_explicit_degree_one_profiles_define_every_coefficient():
    row = reduction.profile_integrals()
    required = {"A2", "A8", "B2", "B0", "B4", "C2", "C8", "D2", "D8", "E2", "E8", "S0", "S1", "S2"}
    assert set(row["values"]) == required
    assert set(row["coefficient_definitions"]) == required
    assert row["all_finite"] is True
    assert row["all_potential_coefficients_positive"] is True
    assert row["certified_relative_method_bound"] <= 2.0e-9
    assert row["physical_promotion"] is False
    assert row["values"]["B0"] == 0.5
    assert row["values"]["S1"] == -3.5


def test_p2_p8_equilibrium_stiffness_and_energy_are_exact():
    row = reduction.symbolic_reduction()
    assert row["stationarity_exact"] is True
    assert row["radial_stiffness_identity_exact"] is True
    assert row["energy_identity_exact"] is True
    assert row["R0"] == "(A8/(5 kappa1 A2))^(1/6)"
    assert row["quadratic_only_eta_finite_radius"] is False


def test_collective_metric_and_breathing_frequency_are_derived_conditionally():
    metric = reduction.collective_kinetic_metric()
    proxy = reduction.representative_reduction()
    assert "D8/R" in metric["M_RR"]
    assert metric["M_Rs"] == "-Zsigma s S1 R^6"
    assert proxy["R0"] > 0
    assert proxy["radial_stiffness"] > 0
    assert proxy["breathing_frequency_squared"] > 0
    assert math.isclose(proxy["breathing_frequency"] ** 2, proxy["breathing_frequency_squared"], rel_tol=1.0e-13)
    assert proxy["classification"] == "PROXY_ONLY"
    assert proxy["physical_orbit"] is False


def test_sigma_branch_is_fixed_R_only_and_does_not_insert_a_surface():
    row = reduction.sigma_formation_gate()
    assert row["fixed_R_branch"] == "s_*^2=-C_sigma(R)/(2 G0 B4 R^7)"
    assert row["surface_licensed_by_collective_branch_alone"] is False
    assert "d_R V" in row["full_branch_requirement"]


def test_global_scale_has_an_exact_remaining_dilation_family():
    row = reduction.global_scale_audit()
    assert row["natural_local_mass_scale"] == "mu_env=kappa1^(1/6)"
    assert row["dilation_family"]["X_eta^4 term"] == "invariant"
    assert row["closed_cosmic_solution_selected"] is False
    assert row["physical_eV_GeV_bridge"] is None
    assert row["status"] == "BHSM_GLOBAL_SCALE_REMAINS_UNDERDETERMINED_BY_CURRENT_ACTION"


def test_reduction_payload_passes_without_physical_promotion():
    payload = reduction.reduction_payload()
    assert payload["validation_passed"] is True
    assert payload["physical_promotion"] is False
