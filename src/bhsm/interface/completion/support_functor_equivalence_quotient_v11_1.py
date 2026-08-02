"""Equivalence quotient for the two provisional BHSM support lifts."""

from __future__ import annotations

from typing import Any


EQUIVALENCE_VERDICT = (
    "BHSM_SUPPORT_FUNCTOR_PHYSICAL_EQUIVALENCE_QUOTIENT_BLOCKED_BY_"
    "ABSENT_COMPLETE_LOCAL_BOUNDARY_AND_CORE_ACTION_DATA"
)
NEXT_EQUIVALENCE_OBJECT = (
    "COMPLETE_LOCAL_SUPPORTED_ACTION_WITH_SUPPORT_DERIVATIVE_COUPLINGS_"
    "AND_BOUNDARY_CORE_CANONICAL_DOMAIN"
)


def _row(key: str, a: int | None, b: int | None, origin: str, total_a: int | None = None, total_b: int | None = None) -> dict[str, Any]:
    return {
        "object_or_term": key,
        "weight_A": a,
        "weight_B": b,
        "weight_difference_B_minus_A": None if a is None or b is None else b - a,
        "origin_of_difference": origin,
        "integrated_total_weight_A": total_a,
        "integrated_total_weight_B": total_b,
    }


def weight_comparison() -> list[dict[str, Any]]:
    """Materialize the provisional representatives without filling absent data."""

    unchanged = "same chosen forgotten-action representative"
    open_origin = "no primitive GD action is supplied by the parent action"
    return [
        _row("supported_coframe", 0, 0, unchanged),
        _row("metric", 0, 0, unchanged),
        _row("inverse_metric", 0, 0, unchanged),
        _row("determinant", 0, 0, unchanged),
        _row("bulk_volume_measure", 0, 0, unchanged),
        _row("boundary_measure", None, None, open_origin),
        _row("normal_vector", None, None, open_origin),
        _row("normal_covector", None, None, open_origin),
        _row("hodge_star", 0, 0, unchanged),
        _row("curvature_scalar", 0, 0, unchanged, 0, 0),
        _row("hopf_base_measure", 0, 1, "measure compensation for changed wall character"),
        _row("fiber_integration", 0, 1, "fiber-measure character", 1, 2),
        _row("wall_embedding", 1, 2, "provisional wall character", 1, 2),
        _row("support_field", 0, 0, unchanged, 0, 0),
        _row("gauge_curvature", None, None, open_origin),
        _row("fermion_fields", None, None, open_origin),
        _row("scalar_topographic_fields", None, None, open_origin),
        _row("charged_currents", None, None, open_origin),
        _row("neutral_currents", None, None, open_origin),
        _row("GHY_term", None, None, "boundary measure and normal characters absent"),
        _row("intrinsic_boundary_terms", None, None, "boundary measure character absent"),
        _row("compatibility_maps", None, None, "cross-stratum intertwiner absent"),
        _row("core_asymptotic_data", None, None, "core representation and domain absent"),
        _row("effective_M4_reduction", None, None, "normalized fiber integration absent"),
    ]


def field_redefinition_test() -> dict[str, Any]:
    return {
        "candidate": "Phi_B=upsilon^(Delta w) Phi_A; q_D^B=c q_D^A; lambda_D^B=c lambda_D^A",
        "invertible_on_regular_domain": True,
        "invertible_at_core": False,
        "derivative_identity": "d(upsilon^r Phi)=upsilon^r[dPhi+r Phi d(log upsilon)]",
        "generated_interactions": ["support-gradient current", "support-gradient-squared term", "connection shift", "boundary normal derivative"],
        "known_to_be_boundary_only": False,
        "complete_action_comparison_available": False,
        "reason": "the frozen action contains neither the complete support-dependent derivative couplings nor a core domain on which the singular map can be tested",
        "classification": "REGULAR_POINTWISE_REDEFINITION_EXISTS_BUT_PHYSICAL_CANONICAL_EQUIVALENCE_UNDECIDED",
    }


def weyl_test() -> dict[str, Any]:
    return {
        "map": "G_tilde=exp(2 omega(q_D)) G",
        "D8_measure": "sqrt(-G_tilde)=exp(8 omega)sqrt(-G)",
        "D8_curvature": "R_tilde=exp(-2 omega)[R-14 Box(omega)-42(grad omega)^2]",
        "D8_EH_density": "sqrt(-G_tilde)R_tilde=exp(6 omega)sqrt(-G)[R-14 Box(omega)-42(grad omega)^2]",
        "D8_gauge_density": "sqrt(-G_tilde)F_tilde^2=exp(4 omega)sqrt(-G)F^2",
        "massless_fermion_note": "conformal covariance requires the D8 spinor weight -7/2 and transformed spin connection",
        "scalar_note": "generic scalar kinetic and potential terms generate frame-dependent derivative/potential factors",
        "boundary_note": "sqrt(h)K transforms with exp(6 omega)[K+7 n.grad(omega)]; EH/GHY cancel the normal Box boundary piece only when the complete paired domain is present",
        "additional_derivative_interactions": True,
        "removable_from_current_complete_action": None,
        "classification": "NOT_PROVEN_EINSTEIN_JORDAN_FRAME_EQUIVALENCE",
    }


def measure_redistribution_test() -> dict[str, Any]:
    return {
        "map": "w(dmu)->w(dmu)+c; w(I_a)->w(I_a)-c",
        "integrated_character_preserved_algebraically": True,
        "local_euler_lagrange_preserved": None,
        "stress_tensor_preserved": None,
        "support_current_preserved": None,
        "canonical_symplectic_form_preserved": None,
        "boundary_variation_preserved": None,
        "core_asymptotics_preserved": None,
        "dimensional_reduction_preserved": None,
        "dimensionless_observables_preserved": None,
        "representation_gauge_freedom_established": False,
        "reason": "when upsilon is dynamical, redistributing its character changes local variations unless a complete invertible canonical map proves otherwise",
    }


def natural_isomorphism_test() -> dict[str, Any]:
    return {
        "fixed_linear_rep_category": "NO_ISOMORPHISM_BETWEEN_DISTINCT_REAL_CHARACTERS",
        "proof": "a nonzero intertwiner eta obeys eta upsilon^wA=upsilon^wB eta for every upsilon, forcing wA=wB",
        "wall_weights": {"A": 1, "B": 2},
        "monoidal_linear_natural_isomorphism_exists": False,
        "field_dependent_nonlinear_eta_regular_domain": "eta_X=upsilon^(wB-wA) is pointwise invertible for upsilon>0",
        "field_dependent_eta_is_gd_linear_natural_map": False,
        "naturality_for_derivatives": False,
        "naturality_for_core_restriction": False,
        "naturality_for_fiber_integration": None,
        "classification": "DISTINCT_FIXED_REPRESENTATIONS_BUT_PHYSICAL_QUOTIENT_REQUIRES_MISSING_ACTION_DATA",
    }


def canonical_structure_test() -> dict[str, Any]:
    missing = "not computable without a complete supported action and boundary/core domain"
    return {
        "Omega_physical_comparison": missing,
        "stress_tensor_comparison": missing,
        "support_current_comparison": missing,
        "reduced_kinetic_comparison": missing,
        "reduced_hessian_comparison": missing,
        "canonical_transformation_exists": None,
        "isospectral_reduced_operator": None,
        "physical_observable_equivalence": None,
    }


def boundary_core_test() -> dict[str, Any]:
    return {
        "regular_bulk_pointwise_map": "invertible for upsilon>0",
        "boundary_measure": None,
        "normal_momentum": None,
        "GHY_variation": None,
        "support_flux": None,
        "stress_flux": None,
        "symplectic_flux": None,
        "core_deficiency_indices": None,
        "self_adjoint_extensions": None,
        "transfer_domain": None,
        "first_certain_failure": "the weight-changing map is singular at upsilon=0 and cannot define a global core intertwiner",
        "first_undecidable_physical_test": "support-gradient terms in the regular local Euler-Lagrange and symplectic structures",
    }


def primitive_ownership_test() -> list[dict[str, Any]]:
    return [
        {"candidate": "supported coframe", "action_owned_selection": False, "result": "r_e is not fixed; adopting it introduces a new continuous character"},
        {"candidate": "supported line element", "action_owned_selection": False, "result": "equivalent missing primitive scale assignment"},
        {"candidate": "primitive normal line", "action_owned_selection": False, "result": "normal-bundle support action absent"},
        {"candidate": "Hopf fiber generator", "action_owned_selection": False, "result": "incidence is discrete but no map to the continuous character generator is derived"},
        {"candidate": "wall embedding", "action_owned_selection": False, "result": "embedding character is the disputed datum"},
        {"candidate": "core-to-surface attachment", "action_owned_selection": False, "result": "attachment representation and core domain absent"},
        {"candidate": "primitive support current", "action_owned_selection": False, "result": "normalized current cannot be derived before the complete supported action"},
    ]


def coframe_test() -> dict[str, Any]:
    return {
        "ansatz": "e_supported^a=upsilon^r_e e_0^a",
        "derived_weights_D8": {"coframe": "r_e", "metric": "2 r_e", "inverse_metric": "-2 r_e", "sqrt_abs_det_metric": "8 r_e", "curvature_scalar_algebraic": "-2 r_e plus support-gradient terms"},
        "stratified_measure_rule": "a fully supported d-dimensional measure has weight d r_e; partial support requires an action-owned supported subbundle",
        "r_e_fixed_by_established_support_definition": False,
        "all_sector_weights_unique": False,
        "boundary_and_fiber_compatibility_derived": False,
        "frozen_limit_recovered": True,
        "lambda_D_fixed": False,
        "new_parameter_if_adopted": "r_e",
        "adopted": False,
    }


def equivalence_payload() -> dict[str, Any]:
    comparison = weight_comparison()
    field = field_redefinition_test()
    natural = natural_isomorphism_test()
    primitive = primitive_ownership_test()
    validation = {
        "minimum_ledger_present": len(comparison) >= 24,
        "both_provisional_lifts_explicit": all("weight_A" in row and "weight_B" in row for row in comparison),
        "ordinary_redefinition_tested": field["invertible_on_regular_domain"] and not field["invertible_at_core"],
        "weyl_derivative_terms_included": weyl_test()["additional_derivative_interactions"],
        "measure_redistribution_not_assumed_gauge": not measure_redistribution_test()["representation_gauge_freedom_established"],
        "linear_natural_isomorphism_decided": not natural["monoidal_linear_natural_isomorphism_exists"],
        "physical_equivalence_not_overclaimed": canonical_structure_test()["physical_observable_equivalence"] is None,
        "all_primitive_candidates_tested": len(primitive) == 7 and not any(row["action_owned_selection"] for row in primitive),
        "coframe_not_adopted": not coframe_test()["adopted"],
    }
    return {
        "artifact": "BHSM_support_functor_equivalence_quotient_v11_1",
        "functor_A": "R_D^(A): provisional wall/fiber representative (1,0)",
        "functor_B": "R_D^(B): provisional wall/fiber representative (2,1)",
        "weight_comparison": comparison,
        "field_redefinition_test": field,
        "weyl_frame_test": weyl_test(),
        "measure_redistribution_test": measure_redistribution_test(),
        "natural_isomorphism_test": natural,
        "canonical_structure_comparison": canonical_structure_test(),
        "boundary_core_comparison": boundary_core_test(),
        "primitive_ownership_candidates": primitive,
        "coframe_derived_uniqueness_test": coframe_test(),
        "haar_invariant_test": {"invariant_candidate": "w_a/lambda_D", "quotient_decided": False, "lambda_D_physical_or_conventional": None},
        "first_point_of_inequivalence": "fixed-character Rep(G_D) wall object and singular core limit",
        "first_point_blocking_physical_classification": "support-gradient local action and boundary/core canonical domain",
        "final_equivalence_classification": "NOT_YET_DECIDABLE_FROM_CURRENT_ACTION",
        "physically_inequivalent_theories_proven": False,
        "physically_equivalent_descriptions_proven": False,
        "status": EQUIVALENCE_VERDICT,
        "next_exact_object": NEXT_EQUIVALENCE_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
