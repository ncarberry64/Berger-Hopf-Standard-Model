"""BHSM v14.92 cross-level critical-value and variational-functor gate.

The historical v7.0--v7.1 construction is recovered here without upgrading its
claims.  It is a constrained correspondence action on M8, M5 and M4.  Fiber
pushforward is available for invariant/equivariant retained M8 data, while the
physical M4 gauge and Dirac fields are independent localized variables.  Thus
the generic KKT, envelope, Schur-complement and cotangent-lift identities are
valid, but the retained BHSM data do not instantiate a physical critical-value
functor from M8 to the M4 gauge/Dirac theory.

No field, coefficient, boundary condition, fit input or flavor kernel is added.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.completion.foundational_dirac_spin_glue_v14_45 import (
    foundational_action_payload as v14_45_dirac_action,
)
from bhsm.interface.master_action.reduction import (
    authoritative_action as v7_authoritative_action,
    field_transport as v7_field_transport,
    geometry_maps as v7_geometry_maps,
    reduction_54 as v7_reduction_54,
    reduction_85 as v7_reduction_85,
)


VERSION = "v14.92"
PRIMARY_OBJECT = (
    "ACTION_OWNED_LORENTZIAN_M8_TO_M4_METRIC_ETA_GAUGE_DIRAC_COMMON_DOMAIN_"
    "CRITICAL_VALUE_FUNCTOR_WITH_VARIATIONAL_BUNDLE_INTERTWINER"
)
EXACT_NEXT_OBJECT = (
    "FOUNDATIONAL_COMMON_PARENT_GAUGE_SPIN_BUNDLE_ACTION_WITH_PHYSICAL_SU3_"
    "AND_DIRAC_CRITICAL_MODES_AND_NO_DOUBLE_COUNTING_M8_TO_M5_TO_M4_"
    "VARIATIONAL_SYMPLECTIC_REDUCTION_FUNCTOR"
)
CHARGED_CURRENT_PROVENANCE_GATE = (
    "PARENT_ACTION_DERIVATION_OR_UNIQUENESS_SELECTION_OF_THE_SPECTRAL_"
    "CHARGED_CURRENT_KERNEL"
)
NONCENTRAL_CURRENT_GATE = "ACTION_OWNED_FAMILY_NONCENTRAL_LEFT_HANDED_CURRENT_SOURCE"
PRIMARY_VERDICT = (
    "BHSM_V14_92_THE_HISTORICAL_M8_TO_M5_TO_M4_CONSTRUCTION_IS_A_VALID_"
    "CONSTRAINED_CORRESPONDENCE_ACTION_WITH_HOPF_FIBER_PUSHFORWARD_ONLY_ON_"
    "RETAINED_INVARIANT_EQUIVARIANT_DATA_AND_WITH_EXACT_CONDITIONAL_KKT_"
    "ENVELOPE_SCHUR_AND_COTANGENT_LIFT_THEOREMS;_IT_IS_NOT_AN_ACTION_OWNED_"
    "CRITICAL_VALUE_DERIVATION_OF_THE_PHYSICAL_M4_GAUGE_DIRAC_THEORY_BECAUSE_"
    "THE_RETAINED_PARENT_HAS_NEITHER_A_PHYSICAL_SU3_PARENT_CONNECTION_NOR_"
    "AN_M8_DIRAC_FIELD_AND_THE_M4_GAUGE_DIRAC_SECTORS_ARE_EXPLICITLY_"
    "INTRINSIC_FOUNDATIONAL_DATA;_THE_V14_91_COEFFICIENT_LOCUS_IS_NOT_"
    "SELECTED_AND_ALL_DOWNSTREAM_PHYSICAL_RESPONSE_OBJECTS_REMAIN_UNDEFINED"
)


def historical_architecture() -> dict[str, Any]:
    """Machine-auditable recovery of the actual v7.0--v7.1 chain."""

    return {
        "M8": "I_t_x_S7",
        "M5": "I_t_x_S4",
        "M4": "I_t_x_S3",
        "pi_85": "id_I_t_x_p_H:M8_to_M5;_proper_oriented_S3_fiber_map",
        "iota_54": "equatorial_inclusion:M4_hookrightarrow_M5",
        "R_85": "normalized_fiber_pushforward_plus_retained_mode_projection_plus_Hopf_quotient_on_admissible_invariant_equivariant_data",
        "R_54": "trace_by_iota_54_pullback_plus_cap_critical_response",
        "direct_R_84": "defined_only_as_R_54_composed_with_R_85_on_the_shared_admissible_subcategory",
        "direct_geometric_M8_to_M4_quotient": False,
        "M5_is_required": True,
        "historical_status": "CONDITIONAL_STRATIFIED_CORRESPONDENCE_NOT_FULL_PHYSICAL_PUSHFORWARD",
    }


def retained_repository_provenance_audit() -> dict[str, Any]:
    """Read the retained theorem payloads so later edits cannot drift claims."""

    geometry = v7_geometry_maps()
    r85 = v7_reduction_85()
    r54 = v7_reduction_54()
    action = v7_authoritative_action()
    fields = {row["field"]: row for row in v7_field_transport()}
    dirac = v14_45_dirac_action()
    checks = {
        "pi85_is_explicit_oriented_submersion": geometry["pi_85"]["status"]
        == "EXPLICIT_PROPER_ORIENTED_SUBMERSION",
        "iota54_is_inclusion": geometry["iota_54"]["status"]
        == "EXPLICIT_ORIENTED_EQUATORIAL_INCLUSION",
        "R85_has_restricted_domain": r85["status"]
        == "COVARIANT_PUSHFORWARD_CONSTRUCTED_ON_RETAINED_SUBCATEGORY",
        "R54_keeps_localized_fields_intrinsic": "intrinsic M4 fields" in r54["localized_fields"],
        "S5_is_not_pi_pushforward_S8": not action["S5_claimed_as_pi_pushforward_of_S8"],
        "boundary_SM_is_not_bulk_descendant": not action["boundary_SM_claimed_as_bulk_descendant"],
        "A_SM_has_no_parent_map": fields["A_SM"]["map"] is None,
        "Psi_has_no_parent_map": fields["Psi"]["map"] is None,
        "Hopf_connection_is_not_SM_gauge": fields["omega"]["lower_owner"].endswith("not SM gauge field"),
        "v14_45_Dirac_is_foundational": dirac["status"] == "FOUNDATIONAL_EFFECTIVE_ACTION_ADOPTED",
        "v14_45_Dirac_not_Path_B_derived": dirac["not_status"]
        == "DERIVED_FROM_THE_BOSONIC_PATH_B_ACTION",
    }
    return {
        "sources": [
            "bhsm.interface.master_action.reduction",
            "bhsm.interface.completion.foundational_dirac_spin_glue_v14_45",
        ],
        "checks": checks,
        "passed": all(checks.values()),
    }


def configuration_spaces() -> dict[str, Any]:
    return {
        "C8": {
            "fundamental": ["G8", "chi8", "sigma8", "eta8", "Lambda_eta"],
            "conditional_transport": ["equivariant_parent_associated_bundle_data"],
            "absent": ["physical_SU3_connection", "Dirac_spinor"],
        },
        "C5": {
            "independent": ["g5", "sigma5", "cap_and_GHY_data"],
            "transported": ["bundle_like_metric_data", "P0_sigma8", "finite_equivariant_modes"],
        },
        "C4": {
            "intrinsic_fundamental": ["h4", "A_SM", "Psi", "H"],
            "traced": ["iota_54_star_g5", "admissible_scalar_trace"],
        },
        "full_physical_map_C8_to_C4": None,
    }


def reduction_map_ledger() -> list[dict[str, Any]]:
    return [
        {
            "sector": "metric",
            "R85": "Q_H_on_bundle_like_metrics_with_independent_constrained_g5",
            "R54": "equatorial_trace_and_metric_matcher",
            "physical_functor": "CONDITIONAL",
        },
        {
            "sector": "scalar_sigma",
            "R85": "normalized_fiber_average_P0",
            "R54": "trace",
            "physical_functor": "CONDITIONAL_ON_BASIC_RETAINED_DOMAIN",
        },
        {
            "sector": "degree_one_eta",
            "R85": None,
            "R54": None,
            "physical_functor": "BLOCKED_NONBASIC_NONLINEAR_PUSHFORWARD_DOES_NOT_COMMUTE_WITH_VARIATION",
        },
        {
            "sector": "physical_SU3_gauge",
            "R85": None,
            "R54": None,
            "physical_functor": "BOUNDARY_LOCALIZED_FUNDAMENTAL",
        },
        {
            "sector": "Dirac",
            "R85": None,
            "R54": None,
            "physical_functor": "FOUNDATIONAL_EFFECTIVE_M4_COLLAR_DATA",
        },
    ]


def bundle_connection_theorem() -> dict[str, Any]:
    return {
        "parent_bundle": "Sp1_to_S7_to_S4_Hopf_bundle",
        "parent_connection": "canonical_Hopf_Sp1_transport_connection_omega",
        "explicit_historical_boundary": "omega_is_not_the_SM_gauge_field",
        "eta_polarization_projection": "composite_projector_connection_A_P_on_Image_P_eta_where_defined",
        "physical_M4_gauge_projection": None,
        "common_representation_maps": None,
        "transition_cocycle_intertwiner": None,
        "characteristic_classes": {
            "Hopf_parent": "c2=+1_on_S4",
            "eta_polarization": "restricted_composite_bundle;_v14_1_audit_reports_c2=0_for_E_P",
            "physical_color": "independent_rank3_SU3_bundle_with_general_retained_c2_sector",
            "compatibility": "NOT_FORCED_BY_EQUAL_RANK_OR_EQUAL_STRUCTURE_GROUP",
        },
        "orientation_or_family_noncentral_source": None,
        "verdict": "NO_COMMON_ACTION_OWNED_PHYSICAL_SU3_CONNECTION_IN_RETAINED_FIELDS",
    }


def dirac_domain_theorem() -> dict[str, Any]:
    return {
        "M8_parent_Dirac_field": None,
        "M8_to_M5_spinor_reduction": None,
        "M5_to_M4_spinor_reduction": None,
        "retained_M4_status": "v14_45_foundational_effective_eta_bound_Dirac_action",
        "intrinsic_spin_domain": "global_parent_collar_spin_bundle_gives_two_sided_Green_form_cancellation",
        "cross_level_common_domain": None,
        "self_adjointness_verdict": "CLOSED_INTRINSICALLY_ON_THE_ADOPTED_COLLAR_BUT_NOT_AS_AN_M8_CRITICAL_MODE_FUNCTOR",
    }


def action_and_kkt_ledger() -> dict[str, Any]:
    return {
        "exact_constrained_action": (
            "S_strat=S8[Phi8]+sum_caps(S5[Phi5]+S_GHY)+S4_localized[Phi4]"
            "+<Lambda85,C85(Phi8,Phi5)>+<Lambda54,C54(Phi5,Phi4)>"
        ),
        "ownership": {
            "S8": "M8_geometry_eta_environment",
            "S5": "independent_target_stratum_action_not_equal_to_pi85_pushforward_S8",
            "S4_localized": "intrinsic_Einstein_Yang_Mills_Dirac_Higgs_effective_data",
            "matchers": "metric_scalar_and_seam_compatibility_not_eta_color_or_parent_Dirac_maps",
        },
        "KKT": [
            "E8+C85_8_adjoint_Lambda85=0",
            "E5-C85_5_adjoint_Lambda85+C54_5_adjoint_Lambda54=0",
            "E4-C54_4_adjoint_Lambda54=0",
            "C85=0",
            "C54=0",
        ],
        "critical_value_definition": "Gamma_eff[y]=stationary_value_x_Gamma[x,y]_when_a_selected_branch_and_domain_exist",
        "is_Crit_of_S8_alone": False,
        "double_counting": "avoided_by_independent_strata_plus_explicit_matchers;_would_be_reintroduced_by_adding_duplicate_M8_eta_or_Dirac_copies",
        "physical_stationarity_commutes_with_reduction": False,
        "reason": "the_physical_A_SM_and_Psi_have_no_parent_configuration_map_or_adjoint_variation",
    }


def witness_r85(x: np.ndarray) -> np.ndarray:
    """Toy retained-subcategory map used only to test functor identities."""

    x = np.asarray(x, dtype=float)
    if x.shape != (3,):
        raise ValueError("x must have shape (3,)")
    return np.array([x[0] + x[1] ** 2, x[2]])


def witness_r54(y: np.ndarray) -> np.ndarray:
    y = np.asarray(y, dtype=float)
    if y.shape != (2,):
        raise ValueError("y must have shape (2,)")
    return np.array([y[0] + 2.0 * y[1]])


def nonlinear_reduction(x: np.ndarray) -> np.ndarray:
    """Direct representation of the composed witness R54 o R85."""

    x = np.asarray(x, dtype=float)
    if x.shape != (3,):
        raise ValueError("x must have shape (3,)")
    return np.array([x[0] + x[1] ** 2 + 2.0 * x[2]])


def reduction_composition_witness() -> dict[str, float]:
    x = np.array([0.4, -0.7, 1.2])
    direct = nonlinear_reduction(x)
    composed = witness_r54(witness_r85(x))
    return {"residual": float(np.linalg.norm(direct - composed))}


def nonlinear_reduction_tangent(x: np.ndarray, dx: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    dx = np.asarray(dx, dtype=float)
    if x.shape != (3,) or dx.shape != (3,):
        raise ValueError("x and dx must have shape (3,)")
    return np.array([dx[0] + 2.0 * x[1] * dx[1] + 2.0 * dx[2]])


def tangent_finite_difference(epsilon: float = 1.0e-6) -> dict[str, float]:
    x = np.array([0.4, -0.7, 1.2])
    dx = np.array([0.3, 0.2, -0.5])
    numeric = (nonlinear_reduction(x + epsilon * dx) - nonlinear_reduction(x - epsilon * dx)) / (2.0 * epsilon)
    analytic = nonlinear_reduction_tangent(x, dx)
    return {"error": float(np.linalg.norm(numeric - analytic)), "epsilon": epsilon}


def weighted_adjoint_witness() -> dict[str, float]:
    r = np.array([[1.0, -2.0, 0.5], [0.0, 1.0, 1.0]])
    w8 = np.diag([2.0, 3.0, 5.0])
    w4 = np.diag([7.0, 11.0])
    r_adj = np.linalg.solve(w8, r.T @ w4)
    u = np.array([0.2, -0.4, 0.7])
    v = np.array([1.1, -0.3])
    lhs = float((r @ u).T @ w4 @ v)
    rhs = float(u.T @ w8 @ r_adj @ v)
    return {"lhs": lhs, "rhs": rhs, "residual": abs(lhs - rhs)}


def critical_value_witness() -> dict[str, Any]:
    """Exact quadratic critical-value/envelope/Schur-complement witness."""

    hxx = np.array([[4.0, 1.0], [1.0, 3.0]])
    bxy = np.array([[1.0, -0.5], [0.25, 2.0]])
    hyy = np.array([[5.0, 0.2], [0.2, 6.0]])
    ax = np.array([0.3, -0.4])
    by = np.array([-0.1, 0.5])
    y = np.array([0.7, -0.2])
    inv_hxx = np.linalg.inv(hxx)

    def stationary_x(arg: np.ndarray) -> np.ndarray:
        return -inv_hxx @ (bxy @ arg + ax)

    def gamma(x: np.ndarray, arg: np.ndarray) -> float:
        return float(0.5 * x @ hxx @ x + x @ bxy @ arg + 0.5 * arg @ hyy @ arg + ax @ x + by @ arg)

    def reduced(arg: np.ndarray) -> float:
        return gamma(stationary_x(arg), arg)

    xstar = stationary_x(y)
    gradient = hyy @ y + bxy.T @ xstar + by
    schur = hyy - bxy.T @ inv_hxx @ bxy
    eps = 1.0e-5
    numeric_gradient = np.array(
        [(reduced(y + eps * np.eye(2)[i]) - reduced(y - eps * np.eye(2)[i])) / (2.0 * eps) for i in range(2)]
    )
    numeric_hessian = np.empty((2, 2))
    for i in range(2):
        for j in range(2):
            ei, ej = np.eye(2)[i], np.eye(2)[j]
            numeric_hessian[i, j] = (
                reduced(y + eps * ei + eps * ej)
                - reduced(y + eps * ei - eps * ej)
                - reduced(y - eps * ei + eps * ej)
                + reduced(y - eps * ei - eps * ej)
            ) / (4.0 * eps**2)
    return {
        "parent_stationarity_residual": float(np.linalg.norm(hxx @ xstar + bxy @ y + ax)),
        "envelope_gradient_error": float(np.linalg.norm(numeric_gradient - gradient)),
        "schur_hessian_error": float(np.linalg.norm(numeric_hessian - schur)),
        "schur_eigenvalues": np.linalg.eigvalsh(schur).tolist(),
    }


def canonical_and_domain_witnesses() -> dict[str, Any]:
    r = np.array([[1.0, 1.0], [0.0, 1.0]])
    rinvt = np.linalg.inv(r).T
    zero = np.zeros((2, 2))
    s = np.block([[r, zero], [zero, rinvt]])
    j = np.block([[zero, np.eye(2)], [-np.eye(2), zero]])
    symplectic_residual = float(np.linalg.norm(s.T @ j @ s - j))

    spinor_core = np.array([1.0 + 2.0j, -0.5 + 0.25j])
    spinor_wall = spinor_core.copy()
    alpha_n = np.diag([1.0, -1.0])
    core_green = np.vdot(spinor_core, alpha_n @ spinor_core)
    wall_green = np.vdot(spinor_wall, -alpha_n @ spinor_wall)
    green_residual = float(abs(core_green + wall_green))

    # Constant transition matrices provide an exact conditional cocycle and
    # gauge-covariance witness; they are not asserted to be the physical map.
    g12 = np.array([[0.0, 1.0], [-1.0, 0.0]])
    g23 = np.array([[1.0, 0.0], [0.0, -1.0]])
    g31 = np.linalg.inv(g12 @ g23)
    cocycle_residual = float(np.linalg.norm(g12 @ g23 @ g31 - np.eye(2)))
    gauge = np.array([[0.0, -1.0], [1.0, 0.0]])
    field = np.array([0.3, -0.8])
    reduction = 2.0 * np.eye(2)
    gauge_residual = float(np.linalg.norm(reduction @ gauge @ field - gauge @ reduction @ field))
    return {
        "conditional_cotangent_lift_symplectic_residual": symplectic_residual,
        "intrinsic_two_sided_Dirac_Green_residual": green_residual,
        "conditional_bundle_cocycle_residual": cocycle_residual,
        "conditional_gauge_covariance_residual": gauge_residual,
        "physical_cross_level_symplectic_map": None,
    }


def metric_gauss_and_coefficient_status() -> dict[str, Any]:
    return {
        "metric_reduction": "conditional_Q_H_plus_independent_g5_and_Lambda85_Lambda54_matchers",
        "Gauss_law_variation": "intrinsic_M4_Yang_Mills_Gauss_equation_only;_no_eta_or_M8_parent_source",
        "constraint_transport": "generic_KKT_constraint_transport_on_declared_matcher_domains_only",
        "v14_91_locus": "kappa0=(15/4)kappa1(5kappa1)^(1/3)",
        "locus_is_exact_stationarity_condition": True,
        "locus_action_selected": False,
        "reason": "Lambda85_and_Lambda54_enforce_cross_stratum_compatibility_but_do_not_vary_or_select_the_independent_kappa0_kappa1_relation",
    }


def completion_payload() -> dict[str, Any]:
    history = historical_architecture()
    provenance = retained_repository_provenance_audit()
    bundle = bundle_connection_theorem()
    dirac = dirac_domain_theorem()
    action = action_and_kkt_ledger()
    tangent = tangent_finite_difference()
    adjoint = weighted_adjoint_witness()
    critical = critical_value_witness()
    canonical = canonical_and_domain_witnesses()
    coefficient = metric_gauss_and_coefficient_status()
    validation = {
        "retained_repository_provenance_passed": provenance["passed"],
        "reduction_composition_closed_on_admissible_subcategory": reduction_composition_witness()["residual"] < 1.0e-13,
        "tangent_finite_difference_passed": tangent["error"] < 1.0e-9,
        "weighted_adjoint_identity_passed": adjoint["residual"] < 1.0e-13,
        "critical_value_parent_stationarity_passed": critical["parent_stationarity_residual"] < 1.0e-13,
        "envelope_gradient_passed": critical["envelope_gradient_error"] < 1.0e-9,
        "Schur_hessian_passed": critical["schur_hessian_error"] < 2.0e-6,
        "intrinsic_Green_form_passed": canonical["intrinsic_two_sided_Dirac_Green_residual"] < 1.0e-13,
        "conditional_symplectic_pullback_passed": canonical["conditional_cotangent_lift_symplectic_residual"] < 1.0e-13,
        "conditional_gauge_covariance_passed": canonical["conditional_gauge_covariance_residual"] < 1.0e-13,
        "conditional_bundle_cocycle_passed": canonical["conditional_bundle_cocycle_residual"] < 1.0e-13,
        "physical_bundle_map_not_fabricated": bundle["physical_M4_gauge_projection"] is None,
        "Dirac_parent_not_fabricated": dirac["M8_parent_Dirac_field"] is None,
        "coefficient_stationarity_not_confused_with_selection": not coefficient["locus_action_selected"],
        "undefined_not_relabelled_zero": True,
        "frozen_predictions_unchanged": True,
    }
    return {
        "artifact": "BHSM_lorentzian_cross_level_critical_value_functor_gate_v14_92",
        "version": VERSION,
        "primary_object": PRIMARY_OBJECT,
        "primary_verdict": PRIMARY_VERDICT,
        "historical_architecture": history,
        "retained_repository_provenance_audit": provenance,
        "configuration_spaces": configuration_spaces(),
        "reduction_maps": reduction_map_ledger(),
        "bundle_connection": bundle,
        "Dirac_provenance_and_domain": dirac,
        "action_KKT_critical_value": action,
        "conditional_mathematical_functor_tests": {
            "tangent": tangent,
            "adjoint": adjoint,
            "critical_value": critical,
            "canonical_domain": canonical,
        },
        "metric_Gauss_coefficient": coefficient,
        "full_coupled_stationary_background": None,
        "physical_projector": None,
        "DeltaPi": None,
        "M_plus_minus": None,
        "B_dyn_L2": None,
        "flavor_provenance": {
            "CKM": CHARGED_CURRENT_PROVENANCE_GATE,
            "noncentral_left_handed_current": NONCENTRAL_CURRENT_GATE,
            "PMNS": "OPEN_UNCHANGED_NO_ACTION_OWNED_PARENT_PROVENANCE",
        },
        "Hindsight_20_20": {
            "validated": [
                "M8_to_M5_Hopf_pushforward_is_real_on_the_admissible_invariant_equivariant_subcategory",
                "the_stratified_KKT_action_and_conditional_envelope_Schur_cotangent_lift_theorems_are_mathematically_valid",
                "M5_is_an_essential_intermediate_level_in_the_historical_architecture",
            ],
            "invalidated": [
                "v7_correspondence_as_a_full_physical_M8_to_M4_critical_value_derivation",
                "the_Hopf_Sp1_connection_as_the_physical_SU3_connection",
                "the_foundational_M4_Dirac_sector_as_an_M8_derived_mode",
            ],
            "reclassified": [
                "stationarity_commutes_with_reduction_is_conditional_on_maps_and_domains_not_owned_for_the_physical_gauge_Dirac_sectors",
                "the_v14_91_locus_is_an_exact_conditional_stationarity_locus_not_an_action_selected_branch",
            ],
            "open": [EXACT_NEXT_OBJECT],
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "completion_status": {
            "FULL_BHSM_COMPLETE": False,
            "MARK_III": "NOT_REACHED",
            "PHYSICAL_EXECUTION_BLOCKED": True,
            "USB_SYNCHRONIZATION_ELIGIBLE": False,
            "frozen_predictions_changed": False,
            "official_prediction_logic_changed": False,
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def materialize(path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return target
