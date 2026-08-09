import json
import math

from bhsm.interface.completion.degree_one_lorentzian_full_preimage_phase_space_v14_91 import (
    EXACT_NEXT_OBJECT,
    canonical_field_ledger,
    completion_payload,
    exact_identity_branch,
    full_coupled_bvp_eligibility,
    identity_branch_required_coefficients,
    identity_branch_residuals,
    materialize,
    smooth_seam_transmission_domain,
    topology_provenance,
)


def test_field_ledger_separates_m8_phase_space_from_intrinsic_m4_fields() -> None:
    rows = {row["field"]: row for row in canonical_field_ledger()}
    assert rows["M8_spatial_metric_h_ij"]["full_preimage_ownership"] is True
    assert rows["eta"]["full_preimage_ownership"] is True
    assert rows["A_physical"]["full_preimage_ownership"] is False
    assert rows["Psi"]["full_preimage_ownership"] is False
    assert rows["seam_embedding_X_seam"]["action_term"] is None
    assert rows["lapse_N"]["physical_dof"] == 0
    assert rows["shift_beta_i"]["physical_dof"] == 0


def test_topology_assigns_degree_only_to_global_m8_map() -> None:
    topology = topology_provenance()
    assert topology["homotopy_group"] == "pi7(S7)=Z"
    assert topology["degree_one_witness"] == "eta_identity:S7_to_S7"
    assert "pi3(S6)=0" in topology["physical_M4_eta_map"]
    assert "no_absolute_integer_degree" in topology["cap_degree_warning"]
    assert topology["union"].endswith("=S7")


def test_static_identity_branch_coefficient_locus_is_exact() -> None:
    branch = identity_branch_required_coefficients(1.0)
    assert math.isclose(branch["X_eta"] ** 3, 5.0, rel_tol=2e-15)
    assert math.isclose(branch["radius_squared"] * branch["X_eta"], 7.0, rel_tol=2e-15)
    assert math.isclose(branch["kappa0"], 15.0 * branch["X_eta"] / 4.0, rel_tol=2e-15)
    residuals = identity_branch_residuals(branch["kappa0"], 1.0, branch["radius"])
    for key in (
        "eta_Einstein_compatibility_residual",
        "Hamiltonian_constraint_residual",
        "spatial_Einstein_residual",
        "momentum_constraint_residual",
    ):
        assert abs(residuals[key]) < 2e-12
    assert residuals["Gauss_constraint_residual"] is None


def test_identity_branch_is_conditional_not_full_stratified_solution() -> None:
    branch = exact_identity_branch()
    assert branch["degree"] == 1
    assert branch["M8_block_stationary_solution"] is True
    assert branch["coefficient_locus_action_selected"] is False
    assert branch["full_stratified_stationary_solution"] is False


def test_off_locus_identity_ansatz_fails_field_equations() -> None:
    residuals = identity_branch_residuals(kappa0=1.0, kappa1=1.0, radius=1.0)
    assert abs(residuals["eta_Einstein_compatibility_residual"]) > 1.0
    assert abs(residuals["Hamiltonian_constraint_residual"]) > 1.0


def test_smooth_cap_cut_has_zero_flux_transmission_domain_only_for_m8_block() -> None:
    domain = smooth_seam_transmission_domain()
    assert domain["status"].startswith("DERIVED_FOR_THE_M8_BLOCK")
    assert domain["GHY_internal_pair"].startswith("cancels")
    assert domain["symplectic_flux"].endswith("global_smooth_perturbations")
    assert "M4_intrinsic" in domain["not_derived"]


def test_full_coupled_bvp_fails_at_variational_ownership() -> None:
    eligibility = full_coupled_bvp_eligibility()
    assert eligibility["eligible"] is False
    assert eligibility["requirements"]["M8_Einstein_eta_joint_density"] is True
    assert eligibility["requirements"]["M8_eta_to_M4_gauge_bundle_intertwiner"] is False
    assert eligibility["first_missing_foundational_object"] == EXACT_NEXT_OBJECT


def test_payload_preserves_undefined_zero_and_completion_boundaries() -> None:
    payload = completion_payload()
    assert payload["validation_passed"] is True
    assert payload["degree_one_background"]["M8_block_stationary_solution"] is True
    assert payload["gauge_reduced_physical_projector"] is None
    assert payload["reflection_odd_relative_tensor_sector"]["DeltaPi"] is None
    assert payload["physical_current_and_vertex"]["B_dyn_L2"] is None
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["completion_status"]["FULL_BHSM_COMPLETE"] is False
    assert payload["completion_status"]["USB_SYNCHRONIZATION_ELIGIBLE"] is False


def test_materializer_is_deterministic_and_strict_json(tmp_path) -> None:
    target = tmp_path / "v14_91.json"
    first = materialize(target).read_bytes()
    second = materialize(target).read_bytes()
    assert first == second
    assert json.loads(first) == completion_payload()
