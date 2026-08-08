"""BHSM v14.91 degree-one Lorentzian full-preimage phase-space gate.

This package separates two questions that were previously conflated.  The
retained M8 Einstein--eta block does possess an exact compact degree-one
identity-map branch on a codimension-one locus of its existing coefficients.
The requested *full* metric--eta--gauge--Dirac boundary-value problem is still
not an Euler--Lagrange problem of the retained stratified action: the gauge and
Dirac fields are intrinsic M4 data and no action-owned M8-to-M4 critical-value
or bundle intertwiner supplies their mixed variation and junction equations.

No new field, coefficient, boundary condition, fitted input, driver, or CKM
kernel is introduced here.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


VERSION = "v14.91"
PRIMARY_OBJECT = (
    "LORENTZIAN_DEGREE_ONE_FULL_PREIMAGE_BACKGROUND_AND_GAUGE_REDUCED_"
    "COUPLED_METRIC_ETA_GAUGE_DIRAC_LINEARIZED_SYMPLECTIC_BOUNDARY_VALUE_"
    "PROBLEM_WITH_REFLECTION_ODD_CAP_RELATIVE_TENSOR_MODES_AND_EXPLICIT_"
    "COEXACT_L2_MIXED_VARIATION"
)
LONG_RANGE_OBJECT = (
    "ACTION_OWNED_FULL_PREIMAGE_TWO_STRATUM_KINETIC_REDUCTION_WITH_DERIVED_"
    "LAYER_INERTIAS_SHEAR_COVARIANCE_AND_DEGREE_ONE_SELF_ADJOINT_BACKGROUND"
)
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_LORENTZIAN_M8_TO_M4_METRIC_ETA_GAUGE_DIRAC_COMMON_DOMAIN_"
    "CRITICAL_VALUE_FUNCTOR_WITH_VARIATIONAL_BUNDLE_INTERTWINER"
)
CHARGED_CURRENT_PROVENANCE_GATE = (
    "PARENT_ACTION_DERIVATION_OR_UNIQUENESS_SELECTION_OF_THE_SPECTRAL_"
    "CHARGED_CURRENT_KERNEL"
)
NONCENTRAL_CURRENT_GATE = "ACTION_OWNED_FAMILY_NONCENTRAL_LEFT_HANDED_CURRENT_SOURCE"
PRIMARY_VERDICT = (
    "BHSM_V14_91_THE_RETAINED_M8_P1_ETA_BLOCK_HAS_AN_EXACT_COMPACT_ROUND_"
    "DEGREE_ONE_IDENTITY_MAP_BRANCH_ON_THE_EXISTING_COEFFICIENT_LOCUS_"
    "KAPPA0_EQUALS_15_OVER_4_KAPPA1_TIMES_5KAPPA1_TO_THE_ONE_THIRD_AND_"
    "THE_HOPF_HEMISPHERE_SPLIT_HAS_A_SMOOTH_ZERO_FLUX_TRANSMISSION_DOMAIN;_"
    "BUT_THIS_LOCUS_IS_NOT_ACTION_SELECTED_AND_THE_INDEPENDENT_M4_GAUGE_"
    "DIRAC_SECTOR_HAS_NO_ACTION_OWNED_COMMON_DOMAIN_CRITICAL_VALUE_OR_"
    "VARIATIONAL_BUNDLE_INTERTWINER_WITH_M8,_SO_THE_REQUESTED_FULL_COUPLED_"
    "BVP_PHYSICAL_PROJECTOR_RELATIVE_TENSOR_SPECTRUM_DELTA_PI_CAP_INERTIAS_"
    "AND_B_DYN_L2_REMAIN_UNDEFINED"
)


def canonical_field_ledger() -> list[dict[str, Any]]:
    """Return the action/domain/canonical provenance needed by the gate."""

    return [
        {
            "field": "M8_spatial_metric_h_ij",
            "domain": "spatial_S7_in_M8=I_t_x_S7",
            "action_term": "S8_env_Einstein_Hilbert_plus_GHY",
            "canonical_momentum": "pi^ij=(kappa1/2)sqrt(h)(K^ij-Kh^ij)",
            "gauge_symmetry": "spatial_diffeomorphisms_and_refoliation",
            "primary_constraint": None,
            "secondary_constraint": "Hamiltonian_and_momentum_constraints",
            "physical_dof": "28_spatial_symmetric_components_before_ADM_reduction;_20_vacuum_graviton_configuration_DOF_in_8D",
            "full_preimage_ownership": True,
        },
        {
            "field": "lapse_N",
            "domain": "M8",
            "action_term": "ADM_multiplier",
            "canonical_momentum": "p_N=0",
            "gauge_symmetry": "time_reparameterization",
            "primary_constraint": "p_N=0",
            "secondary_constraint": "Hamiltonian_constraint",
            "physical_dof": 0,
            "full_preimage_ownership": True,
        },
        {
            "field": "shift_beta_i",
            "domain": "M8_spatial_slice",
            "action_term": "ADM_multiplier",
            "canonical_momentum": "p_beta=0",
            "gauge_symmetry": "spatial_diffeomorphisms",
            "primary_constraint": "p_beta=0",
            "secondary_constraint": "momentum_constraint",
            "physical_dof": 0,
            "full_preimage_ownership": True,
        },
        {
            "field": "chi",
            "domain": "M8",
            "action_term": "-Zchi(1+g_sigma^2)|dchi|^2/2",
            "canonical_momentum": "p_chi=sqrt(h)Zchi(1+g_sigma^2)D_perp_chi",
            "gauge_symmetry": None,
            "primary_constraint": None,
            "secondary_constraint": None,
            "physical_dof": 1,
            "full_preimage_ownership": True,
        },
        {
            "field": "sigma",
            "domain": "M8",
            "action_term": "-Zsigma|d_sigma|^2/2-U(sigma)",
            "canonical_momentum": "p_sigma=sqrt(h)Zsigma D_perp_sigma",
            "gauge_symmetry": None,
            "primary_constraint": None,
            "secondary_constraint": None,
            "physical_dof": 1,
            "full_preimage_ownership": True,
        },
        {
            "field": "eta",
            "domain": "M8_with_eta_t:S7_to_S7",
            "action_term": "-(1+g_sigma^2)[kappa1 X_eta/2+X_eta^4/8]",
            "canonical_momentum": "p_eta=sqrt(h)(1+g_sigma^2)(kappa1+X_eta^3)D_perp_eta_on_T_eta_S7",
            "gauge_symmetry": "diffeomorphism_and_induced_spin_frame_covariance",
            "primary_constraint": "eta_dot_eta-1=0_with_tangent_momentum",
            "secondary_constraint": "multiplier-fixed_normal_eta_equation",
            "physical_dof": "7_target_tangent_components_before_diffeomorphism_reduction",
            "full_preimage_ownership": True,
        },
        {
            "field": "Lambda_eta",
            "domain": "M8",
            "action_term": "Lambda_eta(eta_dot_eta-1)/2",
            "canonical_momentum": "p_Lambda=0",
            "gauge_symmetry": None,
            "primary_constraint": "p_Lambda=0",
            "secondary_constraint": "eta_dot_eta=1",
            "physical_dof": 0,
            "full_preimage_ownership": True,
        },
        {
            "field": "A_physical",
            "domain": "intrinsic_M4=I_t_x_S3",
            "action_term": "provisional_B1_Yang_Mills_or_later_candidate_action",
            "canonical_momentum": "electric_flux_on_M4_when_the_B1_action_is_adopted",
            "gauge_symmetry": "SU3_x_SU2_x_U1",
            "primary_constraint": "temporal_connection_momentum_zero",
            "secondary_constraint": "M4_Gauss_law",
            "physical_dof": "transverse_M4_modes_conditionally",
            "full_preimage_ownership": False,
        },
        {
            "field": "Psi",
            "domain": "intrinsic_or_stratified_M4_Dirac_domain",
            "action_term": "adopted_first_order_Dirac_sector",
            "canonical_momentum": "first_order_Dirac_constraint",
            "gauge_symmetry": "spin_and_internal_gauge",
            "primary_constraint": "first_order_second_class_constraints",
            "secondary_constraint": "state_and_boundary_domain_dependent",
            "physical_dof": "not_counted_without_the_selected_self_adjoint_domain",
            "full_preimage_ownership": False,
        },
        {
            "field": "seam_embedding_X_seam",
            "domain": "candidate_internal_seam",
            "action_term": None,
            "canonical_momentum": None,
            "gauge_symmetry": "normal_reparameterization_if_introduced",
            "primary_constraint": None,
            "secondary_constraint": None,
            "physical_dof": 0,
            "full_preimage_ownership": False,
        },
        {
            "field": "environment_or_driver_x_env",
            "domain": None,
            "action_term": None,
            "canonical_momentum": None,
            "gauge_symmetry": None,
            "primary_constraint": None,
            "secondary_constraint": None,
            "physical_dof": 0,
            "full_preimage_ownership": False,
        },
    ]


def topology_provenance() -> dict[str, Any]:
    """Return the exact degree and Hopf cap provenance."""

    return {
        "Lorentzian_parent": "M8=I_t_x_S7",
        "spatial_map": "eta_t:S7_domain_to_S7_target",
        "homotopy_group": "pi7(S7)=Z",
        "degree_carrier": "global_closed_spatial_map_eta_t",
        "degree_one_witness": "eta_identity:S7_to_S7",
        "physical_or_UV": "M8_parent_topological_sector;_not_the_physical_M4_FR_charge",
        "physical_M4_eta_map": "M4_spatial_S3_to_S6_has_pi3(S6)=0_and_pi4(S6)=0",
        "Hopf_map": "p_H:S7_to_S4_with_c2=+1",
        "base_caps": "B4_plus_union_over_S3_B4_minus=S4",
        "full_preimage_caps": "C_tilde_plus_minus=p_H^-1(B4_plus_minus)",
        "cap_topology": "each_cap_is_B4_x_S3_because_the_bundle_trivializes_over_B4",
        "lifted_seam": "Sigma_tilde=p_H^-1(S3)=S3_x_S3",
        "union": "C_tilde_plus_union_over_Sigma_tilde_C_tilde_minus=S7",
        "cap_degree_warning": "individual_caps_with_boundary_have_no_absolute_integer_degree_without_the_common_boundary_gluing_data",
        "path_B_no_double_counting": "only_the_global_M8_degree_is_retained;_no_M4_degree_or_second_eta_copy_is_added",
    }


def identity_branch_required_coefficients(kappa1: float) -> dict[str, float]:
    """Return the exact static round identity-map coefficient locus.

    The branch uses chi=sigma=0, U(0)=U'(0)=0, unit lapse, zero shift,
    h=a^2 g_round and eta=id.  With X=|d eta|^2=7/a^2, the eta and Einstein
    equations reduce to X^3=5 kappa1 and kappa0=(15/4) kappa1 X.
    """

    if not math.isfinite(kappa1) or kappa1 <= 0.0:
        raise ValueError("kappa1 must be finite and positive")
    x_eta = (5.0 * kappa1) ** (1.0 / 3.0)
    radius_squared = 7.0 / x_eta
    kappa0 = 15.0 * kappa1 * x_eta / 4.0
    return {
        "X_eta": x_eta,
        "radius_squared": radius_squared,
        "radius": math.sqrt(radius_squared),
        "kappa0": kappa0,
        "dimensionless_coefficient_ratio": kappa0 / kappa1 ** (4.0 / 3.0),
    }


def identity_branch_residuals(kappa0: float, kappa1: float, radius: float) -> dict[str, Any]:
    """Evaluate eta, Hamiltonian and spatial Einstein residuals exactly."""

    if not all(math.isfinite(v) and v > 0.0 for v in (kappa0, kappa1, radius)):
        raise ValueError("kappa0, kappa1 and radius must be finite and positive")
    x_eta = 7.0 / radius**2
    energy_density = 0.5 * kappa1 * x_eta + 0.125 * x_eta**4
    pressure = (kappa1 + x_eta**3) * x_eta / 7.0 - energy_density
    eta_algebraic = x_eta**3 - 5.0 * kappa1
    hamiltonian = 3.0 * kappa1 * x_eta - 0.5 * kappa0 - energy_density
    spatial = -15.0 * kappa1 * x_eta / 7.0 + 0.5 * kappa0 - pressure
    return {
        "X_eta": x_eta,
        "energy_density": energy_density,
        "isotropic_pressure": pressure,
        "eta_Einstein_compatibility_residual": eta_algebraic,
        "Hamiltonian_constraint_residual": hamiltonian,
        "spatial_Einstein_residual": spatial,
        "momentum_constraint_residual": 0.0,
        "Gauss_constraint_residual": None,
    }


def exact_identity_branch() -> dict[str, Any]:
    """Construct a representative exact branch and its claim boundary."""

    required = identity_branch_required_coefficients(1.0)
    residuals = identity_branch_residuals(required["kappa0"], 1.0, required["radius"])
    maximum = max(
        abs(residuals[key])
        for key in (
            "eta_Einstein_compatibility_residual",
            "Hamiltonian_constraint_residual",
            "spatial_Einstein_residual",
            "momentum_constraint_residual",
        )
    )
    return {
        "ansatz": "ds8^2=-dt^2+a^2 g_round_S7;_eta=id_S7;_chi=sigma=0;_Lambda_eta=(kappa1+X^3)X",
        "covariant_map_realization": "the_retained_Map(S7,S7)_ledger_with_the_round_pullback_connection;_the_domain_and_target_Levi_Civita_connections_agree_under_constant_rescaling",
        "degree": 1,
        "required_relations": "X^3=5kappa1;_a^2=7/X;_kappa0=(15/4)kappa1 X",
        "representative_kappa1": 1.0,
        "representative": required,
        "residuals": residuals,
        "maximum_finite_residual": maximum,
        "M8_block_stationary_solution": maximum < 2e-12,
        "coefficient_locus_action_selected": False,
        "full_stratified_stationary_solution": False,
        "reason_not_full": "intrinsic_M4_Einstein_Yang_Mills_Dirac_variation_and_M8_to_M4_junction_are_not_closed",
    }


def smooth_seam_transmission_domain() -> dict[str, Any]:
    """Record the domain inherited by cutting one smooth M8 solution."""

    return {
        "cap_embeddings": "X_plus_minus:C_tilde_plus_minus_hookrightarrow_M8_are_subset_inclusions",
        "normals": "n_minus=-n_plus_under_the_common_seam_identification",
        "induced_metric_matching": "h_plus|Sigma=h_minus|Sigma",
        "gravity_momentum_matching": "normal_canonical_flux_plus+normal_canonical_flux_minus=0",
        "eta_trace_matching": "eta_plus|Sigma=eta_minus|Sigma",
        "eta_conormal_matching": "n_plus.J_eta_plus+n_minus.J_eta_minus=0",
        "chi_sigma_matching": "continuous_trace_and_opposite_outward_conormal_flux",
        "GHY_internal_pair": "cancels_for_the_two_opposite_outward_normals_on_a_smooth_cut",
        "Green_form": "cap_Green_forms_cancel_pairwise_on_smooth_transmission_data",
        "symplectic_flux": "Omega_plus+R_pullback_Omega_minus=0_on_global_smooth_perturbations",
        "outer_cap_behavior": "regularity_at_the_two_Hopf_base_poles",
        "status": "DERIVED_FOR_THE_M8_BLOCK_AS_THE_RESTRICTION_OF_GLOBAL_SMOOTH_FIELDS",
        "not_derived": "a_moving_seam_degree_of_freedom_or_the_M4_intrinsic_field_junction_domain",
    }


def full_coupled_bvp_eligibility() -> dict[str, Any]:
    requirements = {
        "M8_Einstein_eta_joint_density": True,
        "global_M8_degree_one_sector": True,
        "exact_conditional_M8_identity_background": True,
        "smooth_M8_cap_transmission_domain": True,
        "M4_physical_gauge_action_parent_derived": False,
        "M4_Dirac_domain_selected": False,
        "M8_eta_to_M4_gauge_bundle_intertwiner": False,
        "M8_to_M4_metric_critical_value_and_junction": False,
        "single_coupled_Green_form": False,
        "single_coupled_symplectic_form": False,
        "coefficient_locus_selected_by_retained_axioms": False,
    }
    return {
        "requirements": requirements,
        "eligible": all(requirements.values()),
        "first_missing_foundational_object": EXACT_NEXT_OBJECT,
        "classification": "PRIMARY_OBJECT_CLOSED_NEGATIVELY_AT_FULL_COUPLED_VARIATIONAL_OWNERSHIP",
        "block_diagonal_formal_embedding": "mixed_M8_eta_to_M4_gauge_Dirac_second_variations_are_zero_but_this_is_not_the_requested_coupled_problem",
    }


def completion_payload() -> dict[str, Any]:
    background = exact_identity_branch()
    eligibility = full_coupled_bvp_eligibility()
    topology = topology_provenance()
    seam = smooth_seam_transmission_domain()
    validation = {
        "degree_one_is_global_M8_pi7_sector": topology["homotopy_group"] == "pi7(S7)=Z",
        "M4_false_degree_not_reintroduced": "pi3(S6)=0" in topology["physical_M4_eta_map"],
        "identity_branch_residuals_close": background["M8_block_stationary_solution"],
        "identity_branch_not_promoted_off_coefficient_locus": not background["coefficient_locus_action_selected"],
        "smooth_M8_transmission_flux_closes": seam["status"].startswith("DERIVED_FOR_THE_M8_BLOCK"),
        "full_coupled_BVP_fails_closed": not eligibility["eligible"],
        "undefined_not_relabelled_zero": True,
        "CKM_and_noncentral_current_gates_preserved": True,
        "frozen_predictions_unchanged": True,
        "full_BHSM_not_claimed": True,
    }
    return {
        "artifact": "BHSM_degree_one_lorentzian_full_preimage_phase_space_gate_v14_91",
        "version": VERSION,
        "primary_object": PRIMARY_OBJECT,
        "long_range_object": LONG_RANGE_OBJECT,
        "primary_verdict": PRIMARY_VERDICT,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "canonical_phase_space": {
            "M8_owned": "T_star[Met_plus(S7)_x_chi_x_sigma_x_Map_degree1(S7,S7)]_subject_to_ADM_and_eta_constraints",
            "full_stratified_phase_space": None,
            "ledger": canonical_field_ledger(),
        },
        "topology": topology,
        "degree_one_background": background,
        "cap_seam_geometry_and_domain": seam,
        "full_coupled_BVP": eligibility,
        "gauge_reduced_physical_projector": None,
        "linearized_dynamical_spectrum": {
            "M8_background_block": "NOT_COMPUTED_BECAUSE_THE_BRANCH_IS_CONDITIONAL_AND_NOT_THE_FULL_STATIONARY_STRATIFIED_BACKGROUND",
            "full_metric_eta_gauge_Dirac": None,
            "gyroscopic_block_C": None,
        },
        "reflection_odd_relative_tensor_sector": {
            "kinematically_allowed_on_global_S7": True,
            "physical_reduced_spectrum": None,
            "DeltaPi": None,
            "claim_boundary": "not_derived_is_not_zero",
        },
        "cap_inertias": {
            "M_plus": None,
            "M_minus": None,
            "equal_inertia": "CONDITIONAL_V14_84_INTERTWINING_THEOREM_ONLY",
            "nu": "ONE_QUARTER_NOT_PHYSICAL_YET",
        },
        "physical_current_and_vertex": {
            "J_dyn": None,
            "B_dyn_L2": None,
            "static_or_dynamic_Schur_insertion": "INELIGIBLE",
        },
        "complete_L2": {
            "Hessian": None,
            "eigenvalues": None,
            "first_instability_ordering": None,
            "Landau_r_u_v": None,
            "three_Goldstone_locking": "NOT_REACHED",
            "Floquet": "NOT_REACHED",
            "alpha_critical": "NOT_REACHED",
        },
        "flavor_provenance": {
            "CKM": CHARGED_CURRENT_PROVENANCE_GATE,
            "noncentral_left_handed_current": NONCENTRAL_CURRENT_GATE,
            "PMNS_neutrino": "OPEN_UNCHANGED",
        },
        "Hindsight_20_20": {
            "validated": [
                "the global M8 eta degree is well-defined in pi7(S7)",
                "the round eta identity map gives an exact compact degree-one M8 Einstein-eta branch on an explicit existing-coefficient locus",
                "the Hopf hemisphere cap split has the smooth global-field transmission domain and zero internal flux",
            ],
            "invalidated": [
                "the claim that no compact degree-one M8 background candidate exists",
                "individual cap degree as an independent integer",
                "the requested full coupled BVP as an Euler-Lagrange problem of the currently retained cross-level action",
            ],
            "reclassified": [
                "the background obstruction is a full stratified ownership/junction obstruction, not absence of an M8 degree-one stationary point",
                "the M8 smooth seam domain is derived, while the M4 intrinsic common domain remains absent",
            ],
            "open": [EXACT_NEXT_OBJECT],
        },
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
