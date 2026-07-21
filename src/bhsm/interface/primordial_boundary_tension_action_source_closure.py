"""BHSM v5.12 primordial boundary-tension action-source closure audit.

The repository supplies a normalized boundary/collar architecture but not the
physical localization, coefficient normalization, or surface domain required
to evaluate a release radius.  Finite-dimensional examples below test the
competing-scaling theorem and are never promoted to BHSM coefficient values.
"""

from __future__ import annotations

import json
from math import sqrt
from pathlib import Path
from typing import Any


VERSION = "v5.12"
SPRINT = "bhsm-primordial-boundary-tension-action-source-closure-v5-12"
PRIMARY_RESULT = "BHSM_PRIMORDIAL_BOUNDARY_SOURCE_NOT_CLOSED"
RECYCLING_RESULT = "BHSM_SPACETIME_RECYCLING_CONSTRAINT_ARCHITECTURE_IDENTIFIED"
SIGMA_SCALE = 0.5

ARTIFACT_FILES = {
    "action_source": "BHSM_primordial_boundary_collar_action_source_v5_12.json",
    "dimension_localization": "BHSM_primordial_boundary_dimension_localization_v5_12.json",
    "stress_tensor": "BHSM_primordial_boundary_stress_tensor_v5_12.json",
    "normal_variation": "BHSM_primordial_normal_displacement_variations_v5_12.json",
    "pressure": "BHSM_primordial_inside_outside_pressure_v5_12.json",
    "curvature_coefficients": "BHSM_primordial_curvature_bending_coefficients_v5_12.json",
    "collar_stress": "BHSM_primordial_collar_jacobian_stress_v5_12.json",
    "shape_equation": "BHSM_primordial_normal_shape_equation_v5_12.json",
    "surface_hessian": "BHSM_primordial_surface_hessian_eigenproblem_v5_12.json",
    "release_threshold": "BHSM_primordial_release_threshold_crossing_v5_12.json",
    "absolute_one_scale": "BHSM_primordial_absolute_unit_one_scale_v5_12.json",
    "energy_conversion": "BHSM_primordial_release_energy_conversion_v5_12.json",
    "reduced_model": "BHSM_primordial_reduced_threshold_model_v5_12.json",
    "construction_report": "BHSM_primordial_boundary_tension_action_source_closure_report_v5_12.json",
    "recycling_action": "BHSM_spacetime_recycling_candidate_action_v5_12.json",
    "top_form_dimension": "BHSM_spacetime_recycling_top_form_dimension_degree_v5_12.json",
    "core_source": "BHSM_spacetime_recycling_core_source_flux_jump_v5_12.json",
    "recycling_stress": "BHSM_spacetime_recycling_stress_energy_pressure_v5_12.json",
    "causal_constraint": "BHSM_spacetime_recycling_causal_constraint_audit_v5_12.json",
    "zero_point_flux": "BHSM_spacetime_recycling_zero_point_flux_energy_v5_12.json",
    "recycling_regimes": "BHSM_spacetime_recycling_primordial_late_time_map_v5_12.json",
}

GUARDS = {
    "empirical_inputs_used": False,
    "measured_scale_used": False,
    "planck_electroweak_higgs_or_cosmology_scale_used": False,
    "natural_units_hide_missing_dimension": False,
    "renormalization_scale_promoted_to_L_c": False,
    "rho_star_promoted_to_physical_length": False,
    "minus_one_eighth_promoted_to_physical_tension": False,
    "v5_10_global_determinant_used_as_local_casimir_pressure": False,
    "primitive_tension_claimed_derived": False,
    "absolute_unit_claimed": False,
    "hot_plasma_production_claimed_derived": False,
    "particle_masses_derived": False,
    "gauge_couplings_derived": False,
    "ckm_completion_claimed": False,
    "rare_b_predictions_claimed": False,
    "full_bhsm_completion_claimed": False,
    "frozen_predictions_changed": False,
    "official_prediction_logic_changed": False,
    "existing_numerical_predictions_changed": False,
    "black_hole_observation_used": False,
    "present_hubble_rate_used": False,
    "arbitrary_flux_promoted_to_absolute_unit": False,
    "primitive_recycling_coefficient_claimed_derived": False,
    "information_erasure_claimed": False,
    "superluminal_signaling_claimed": False,
    "dark_energy_replacement_claimed": False,
    "inflation_or_horizon_problem_claimed_solved": False,
}

OPEN_GATES = (
    "OPEN_MISSING_PHYSICAL_BOUNDARY_DOMAIN_SIGNATURE",
    "OPEN_MISSING_ABSOLUTE_BOUNDARY_MEASURE_NORMALIZATION",
    "OPEN_MISSING_SCALAR_TOPOGRAPHIC_PHYSICAL_LOCALIZATION_MAP",
    "OPEN_MISSING_ABSOLUTE_BOUNDARY_TENSION_DENSITY_SOURCE",
    "OPEN_MISSING_COMPLETE_SCALAR_TOPOGRAPHIC_COLLAR_ACTION",
    "OPEN_MISSING_BOUNDARY_EMBEDDING_AND_SHAPE_VALUES",
    "OPEN_MISSING_BOUNDARY_SHAPE_COEFFICIENT_VALUES",
    "OPEN_MISSING_BULK_GEOMETRIC_ACTION_NORMALIZATION",
    "OPEN_MISSING_GHY_OR_VARIATIONAL_BOUNDARY_COMPLETION_THEOREM",
    "OPEN_MISSING_STATIC_INSIDE_OUTSIDE_PRESSURE_SOURCE",
    "OPEN_MISSING_NORMAL_DISPLACEMENT_DOMAIN_AND_SPECTRUM",
    "OPEN_MISSING_SURFACE_HESSIAN_SELF_ADJOINT_CLOSURE",
    "OPEN_MISSING_LOCAL_QUANTUM_SURFACE_STRESS",
    "OPEN_MISSING_PRIMORDIAL_RELEASE_ENERGY_CONVERSION",
    "OPEN_MISSING_GLOBAL_SCALE_MODULUS_ACTION_SOURCE",
    "OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR",
    "OPEN_MISSING_RECYCLING_BULK_ACTION_SOURCE",
    "OPEN_MISSING_RECYCLING_TOP_FORM_NORMALIZATION",
    "OPEN_MISSING_CONSERVED_CORE_WORLDVOLUME_CURRENT",
    "OPEN_MISSING_RECYCLING_BOUNDARY_ENSEMBLE",
    "OPEN_MISSING_RECYCLING_FLUX_INITIAL_DATA_OR_QUANTIZATION",
    "OPEN_MISSING_RECYCLING_TO_BOUNDARY_MODE_PROJECTION",
    "OPEN_MISSING_RECYCLING_ENERGY_TRANSFER_LAW",
    "FULL_BHSM_NOT_COMPLETE",
)


def _common(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "version": VERSION,
        "sprint": SPRINT,
        "primary_result": PRIMARY_RESULT,
        "recycling_result": RECYCLING_RESULT,
        "claim_boundary": (
            "v5.12 derives the strongest source-qualified boundary normal-stress "
            "and stability architecture. Physical localization, dimensions, "
            "coefficients, pressure, embedding, and domain remain insufficient "
            "to evaluate L_c or derive an absolute unit."
        ),
        **GUARDS,
    }


def action_source_payload() -> dict[str, Any]:
    terms = [
        {"term": "U_boundary", "stored_formula": "U_boundary(T,Phi)", "source": "v5.6 S_boundary candidate", "fields": ["T", "Phi", "h through measure"], "domain": "Sigma", "localization": "boundary candidate, unevaluated", "measure": "dA=dmu_h", "orientation": "measure independent; normal stress sign convention open", "coordinates": "normalized in v5.7", "coefficient": "implicit", "dimension": "[action] L^(-d_Sigma)", "coefficient_status": "OPEN_NO_LOCAL_DENSITY", "earlier_variation": "scalar variation only in reduced projection; metric/normal variation not evaluated"},
        {"term": "K", "stored_formula": "c_K K", "source": "v5.6 S_boundary candidate", "fields": ["h", "embedding", "normal"], "domain": "Sigma", "localization": "boundary", "measure": "dmu_h", "orientation": "K changes under normal reversal", "coordinates": "normalized geometry in v5.7", "coefficient": "c_K", "dimension": "[action] L^(1-d_Sigma)", "coefficient_status": "SYMBOLIC_UNSOURCED", "earlier_variation": "set to zero only for fixed-geometry scalar reduction"},
        {"term": "K_squared", "stored_formula": "c_K2 K^2", "source": "v5.6 S_boundary candidate", "fields": ["h", "embedding", "normal"], "domain": "Sigma", "localization": "boundary", "measure": "dmu_h", "orientation": "orientation even", "coordinates": "normalized geometry in v5.7", "coefficient": "c_K2", "dimension": "[action] L^(2-d_Sigma)", "coefficient_status": "SYMBOLIC_UNSOURCED", "earlier_variation": "set to zero only for fixed-geometry scalar reduction"},
        {"term": "shape_norm", "stored_formula": "c_S Tr(S^2)", "source": "v5.6 S_boundary candidate", "fields": ["h", "embedding", "normal"], "domain": "Sigma", "localization": "boundary", "measure": "dmu_h", "orientation": "orientation even", "coordinates": "normalized geometry in v5.7", "coefficient": "c_S", "dimension": "[action] L^(2-d_Sigma)", "coefficient_status": "SYMBOLIC_UNSOURCED", "earlier_variation": "set to zero only for fixed-geometry scalar reduction"},
        {"term": "standalone_J", "stored_formula": "c_J log J", "source": "v5.6 S_boundary candidate", "fields": ["shape operator", "rho"], "domain": "boundary/collar trace", "localization": "candidate duplicate of collar measure", "measure": "dmu_h", "orientation": "inherits J convention", "coordinates": "normalized", "coefficient": "c_J=0", "dimension": "would require [action] L^(-d_Sigma)", "coefficient_status": "ZERO_TO_PREVENT_DUPLICATION", "earlier_variation": "not varied independently"},
        {"term": "collar", "stored_formula": "integral_0^rho_star B_threshold[T,Phi,K,S,J;Y,rho] J(Y,rho) d rho", "source": "v5.6 S_collar candidate and v4.1 conditional measure", "fields": ["T", "Phi", "h", "K", "S", "J", "rho"], "domain": "Sigma x [0,rho_star]", "localization": "collar integrand open", "measure": "J dmu_h d rho", "orientation": "J=det(I +/- rho S), sign unresolved", "coordinates": "rho_star=1 is normalized coordinate", "coefficient": "B_threshold symbolic", "dimension": "[action] L^(-(d_Sigma+1)) if rho physical", "coefficient_status": "OPEN_LOCALIZABLE_NOT_COMPLETE", "earlier_variation": "zero contribution in v5.7 homogeneous normalized evaluation"},
        {"term": "v5.4_geometry", "stored_formula": "1/2 kappa_geom <delta h,L_geom(rho)delta h>_Sigma", "source": "v5.4 unified action candidate", "fields": ["delta h"], "domain": "relative Berger boundary", "localization": "already quadratic fluctuation slot, not foundational bulk gravity action", "measure": "sqrt(det h_rho) d^3x", "orientation": "boundary flux convention open", "coordinates": "ell_BH-normalized", "coefficient": "kappa_geom", "dimension": "ell_BH power -1 in v5.4 normalized table", "coefficient_status": "PROVISIONAL_SYMBOLIC", "earlier_variation": "symbolic geometry equation"},
    ]
    return {**_common("BHSM_primordial_boundary_collar_action_source_v5_12"), "status": "BOUNDARY_COLLAR_ARCHITECTURE_EXACT_SOURCES_PHYSICAL_COEFFICIENTS_OPEN", "canonical_boundary_action": "S_boundary=integral_Sigma dmu_h[U_boundary+c_K K+c_K2 K^2+c_S Tr(S^2)+c_J log J+L_boundary,other]", "canonical_collar_action": "S_collar=integral_Sigma integral_0^rho_star d rho dmu_h J B_collar[T,Phi,g,K,S,rho]", "terms": terms, "other_terms": "none physically normalized in the stored boundary source", "exact_complete_physical_action": False}


def dimension_localization_payload() -> dict[str, Any]:
    return {**_common("BHSM_primordial_boundary_dimension_localization_v5_12"), "status": "NORMALIZED_BOUNDARY_COORDINATE_DIMENSION_KNOWN_PHYSICAL_DOMAIN_OPEN", "domain_dimension": {"v5_4_coordinate_boundary_dimension": 3, "evidence": "dmu_Sigma,rho=sqrt(det h_rho)d^3x", "d_Sigma_physical": "symbolic", "d_collar_coordinate": 4, "d_bulk": None, "time_included": None, "signature": None, "Sigma_classification": "relative Berger/collar boundary; spatial versus spacetime versus Euclidean/canonical not fixed", "reason_symbolic": "coordinate count does not establish physical time/signature or the bulk-boundary relation"}, "dimension_rules": {"action": "[A]=[hbar] retained explicitly", "U_boundary": "[A] L^(-d_Sigma)", "c_K": "[A] L^(1-d_Sigma)", "c_K2": "[A] L^(2-d_Sigma)", "c_S": "[A] L^(2-d_Sigma)", "B_collar_physical_rho": "[A] L^(-(d_Sigma+1))", "B_collar_dimensionless_rho": "[A] L^(-d_Sigma) times an unresolved physical collar conversion", "stress_tau_AB": "[A] L^(-d_Sigma)", "normal_force_density": "[A] L^(-(d_Sigma+1))", "surface_hessian_density": "[A] L^(-(d_Sigma+2))"}, "candidate_d_Sigma_3_specialization": {"U_boundary": "[A] L^-3", "c_K": "[A] L^-2", "c_K2": "[A] L^-1", "c_S": "[A] L^-1", "B_collar_if_physical_rho": "[A] L^-4"}, "v5_4_dimension_table": {"convention": "powers of an unresolved ell_BH; action normalized to dimension zero", "physical_ell_BH_derived": False, "natural_units_used_to_close_source": False}, "reduced_localization": {"V_red": "-sigma^2+2 sigma^4", "V_red_at_half": -0.125, "classification": "coordinate-normalized mode-space functional value", "mode_normalization": "Q_ST[f_T,f_Phi]=1 with f_T=f_Phi=1/sqrt(2) in v5.7 normalized cell", "component_contributions": {"T_Phi_mixing": -3.0, "threshold_quadratic": -2.0, "quartic_boundary_collar_kernel": 8.0, "explicit_boundary": 0.0, "explicit_collar": 0.0, "geometry_measure": 0.0}, "Berger_volume": "normalized but no action-selected physical volume", "collar_measure": "rho_star=1,J=1 in reduced cell", "field_dimensions": "dimensionless before ell_star", "orientation": "positive scalar branch selected; physical normal sign not fixed", "map_to_U_boundary": None, "map_to_B_collar": None, "localization_closed": False, "reason": "the reduction combines threshold, mixing, and quartic-kernel data and supplies no inverse projection to a local density"}}


def recycling_action_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_spacetime_recycling_candidate_action_v5_12"),
        "status": "CANDIDATE_LOCAL_TOP_FORM_ACTION_CONSISTENT_BHSM_SOURCE_ABSENT",
        "action": "S_rec=-Z_F/(2 d_B!) integral_B sqrt|G| F_[d_B]^2+S_source+S_boundary,rec",
        "fields": {"potential": "C_[d_B-1]", "field_strength": "F_[d_B]=dC_[d_B-1]"},
        "four_dimensional_specialization": "C_3 and F_4=dC_3 only if d_B=4",
        "field_equation": "d(Z_F star F_[d_B])=J_core with source normalization/sign fixed by the source convention",
        "source_free_solution": "F_[d_B]=f vol_B and d(Z_F f)=0",
        "connected_region_result": "Z_F f is locally constant and globally constant on each connected smooth source-free component",
        "normalization": {"Z_F": None, "assumed_one": False, "existing_BHSM_source": None, "classification": "UNRESOLVED_SYMBOLIC_NORMALIZATION"},
        "boundary_term": {"formula": None, "required_role": "select fixed-f versus fixed-integrated-flux variational ensemble", "stored_in_BHSM": False},
        "source_search": [
            {"location": "v5.4-v5.12 unified/boundary/collar action", "top_form_term": False},
            {"location": "BHSM topology ledgers", "charged codimension_one_worldvolume": False},
            {"location": "black-hole/core action", "collapse_or_horizon_source": False},
            {"location": "quantum v5.10", "top_form_induction": False},
        ],
        "candidate_not_adopted_as_established_action": True,
    }


def top_form_dimension_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_spacetime_recycling_top_form_dimension_degree_v5_12"),
        "status": "TOP_DEGREE_RULE_DERIVED_PHYSICAL_BULK_DIMENSION_OPEN",
        "d_B": None,
        "degree_rule": {"potential_degree": "d_B-1", "field_strength_degree": "d_B", "matches_top_degree": True},
        "candidate_d_B_4": {"potential": "C_3", "field_strength": "F_4", "adopted_as_physical_dimension": False},
        "dimensions": {
            "C": "[C] retained symbolically",
            "F": "[C] L^-1",
            "Z_F": "[A] L^(2-d_B) [C]^-2",
            "rho_rec": "[A] L^-d_B for a spacetime action density",
            "integrated_flux_Q": "[C] L^(d_B-1)",
            "codimension_one_charge_q_rec": "[A] [C]^-1 L^(-(d_B-1))",
        },
        "source_worldvolume": "C_[d_B-1] couples electrically to a (d_B-1)-dimensional worldvolume, i.e. a spatial (d_B-2)-brane",
        "black_hole_worldline_matches_source": False,
        "bulk_domain_obstruction": "v5.12 does not fix Lorentzian signature, time inclusion, or d_B",
        "natural_units_close_missing_dimensions": False,
    }


def core_source_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_spacetime_recycling_core_source_flux_jump_v5_12"),
        "status": "CORE_SOURCE_COUPLING_UNSUPPORTED_JUMP_CONDITIONAL",
        "candidate_couplings": ["q_rec integral_W_core C_[d_B-1]", "integral_B C_[d_B-1] wedge J_core"],
        "required_worldvolume_dimension": "d_B-1",
        "d_B_4_interpretation": "a 2-brane with a three-dimensional worldvolume; a point-core worldline is not the electric source of C_3",
        "BHSM_support": {"core_worldvolume": False, "horizon_action_boundary": False, "conserved_top_form_current": False, "topological_charge": False, "membrane_source": False},
        "current_conservation": "dJ_core=0 is required by C -> C+dLambda gauge invariance, modulo declared boundary/end-point inflow",
        "source_conservation_derived_for_BHSM_core": False,
        "conditional_jump": "Z_F(f_plus-f_minus)=orientation*q_rec for a thin charged codimension-one source",
        "f_behavior": {"source_free": "constant per connected component", "with_thin_source": "piecewise constant", "continuous": False, "jump_requires_supported_source": True},
        "quantization": {"automatic": False, "requirements": ["compact higher-form gauge group", "large-gauge consistency", "allowed charged worldvolume", "normalized charge lattice"], "BHSM_proof": False},
        "q_rec": {"value": None, "classification": "UNSUPPORTED", "inferred_from_black_hole_mass": False},
        "information_doctrine": {
            "preserved": ["energy-momentum", "angular momentum", "gauge charge", "protected topological data", "complete-state correlations"],
            "reduced_loss": "bound-state and local-history labels may leave the effective exterior variables",
            "fundamental_information_destroyed": False,
            "unitarity_status": "open; no nonunitary source is introduced",
            "invalid_if": ["gauge current is not conserved", "diffeomorphism constraints fail", "complete evolution is nonunitary without an explicit theory"],
        },
        "interpretation_ledger": {"deconstruction": "coarse-grained loss of externally accessible bound-state structure only", "instantaneous_response": "replaced by a global constraint solution; not a signal-propagation claim"},
    }


def recycling_stress_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_spacetime_recycling_stress_energy_pressure_v5_12"),
        "status": "TOP_FORM_STRESS_DERIVED_FOR_CANDIDATE_ACTION_PHYSICAL_SIGN_ENSEMBLE_OPEN",
        "stress_tensor": "T_AB=Z_F/(d_B-1)! F_A... F_B^...-Z_F/(2 d_B!) G_AB F^2",
        "lorentzian_top_form_identity": {"F": "f vol_B", "F_squared": "-d_B! f^2 for one timelike direction", "T_AB": "-(Z_F f^2/2)G_AB"},
        "energy_density": "rho_rec=Z_F f^2/2 for a unit timelike observer and Z_F>0",
        "isotropic_pressure": "p_rec=-rho_rec in the fixed local-f Lorentzian stress tensor",
        "equation_of_state": "p/rho=-1 where Lorentzian energy and pressure are defined",
        "normal_projection": "n^A n^B T_AB=-epsilon_n rho_rec",
        "outward_pressure_proved": False,
        "orientation_dependence": "F orientation reverses f but stress depends on f^2; normal projection depends on epsilon_n",
        "bulk_dimension_dependence": "factorials cancel in the top-form solution; density dimension retains d_B",
        "dimensions": {"rho_and_pressure": "[A] L^-d_B", "f": "[C]L^-1", "Z_F": "[A]L^(2-d_B)[C]^-2"},
        "boundary_ensemble": {
            "fixed_local_f": {"E_rec": "rho_rec V", "p_mechanical": "-partial E/partial V=-rho_rec", "direct_delta_p": 0.0},
            "fixed_integrated_flux_Q": {"f": "Q/V", "E_rec": "Z_F Q^2/(2V)", "p_mechanical": "+Z_F Q^2/(2V^2)", "response": "rank-one global volume response"},
            "reason_for_difference": "the boundary Legendre term and fixed data differ",
            "BHSM_choice": None,
        },
    }


def causal_constraint_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_spacetime_recycling_causal_constraint_audit_v5_12"),
        "status": "LOCAL_CAUSAL_TOP_FORM_CONSTRAINT_ARCHITECTURE_NO_CORE_REALIZATION",
        "canonical_decomposition": {
            "canonical_coordinate": "spatial top component C_i1...i_(d_B-1)",
            "canonical_momentum": "electric top-form density pi proportional to Z_F star F",
            "primary_constraints": "momenta of components containing a time index vanish",
            "secondary_constraint": "spatial Gauss law d_space pi=J_core",
            "local_degrees_of_freedom": 0,
            "global_degree_of_freedom": "one global flux/integration-constant sector per connected compact component, subject to boundary data and charge jumps",
        },
        "classification": ["local covariant action", "Gauss-law-type constraint", "top-form with no local propagating polarizations", "collective flux variable"],
        "nonlocal_action_required": False,
        "characteristic_propagation": "no ordinary local top-form wave; charged sources and all other local fields still obey the causal initial-value structure",
        "causal_interpretation": "constraint data correlate a compact slice but do not provide a controllable faster-than-causal communication channel",
        "superluminal_signal": False,
        "no_signal_test": {"local_control_of_global_flux_without_conserved_source": False, "local_observable_transmits_message_outside_causal_domain": False, "passes_candidate_level": True},
        "homogeneous_response": {"source_free_connected_region": True, "initial_condition_independent": False, "anisotropy_suppression_derived": False, "inflation_replaced": False, "horizon_problem_solved": False},
    }


def zero_point_flux_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_spacetime_recycling_zero_point_flux_energy_v5_12"),
        "status": "VACUUM_FLOOR_DISTINGUISHED_FROM_POSITIVE_FLUX_SECTOR",
        "definition": "E_0=min_allowed_bulk_state E_bulk",
        "continuous_positive_Z_model": {"minimum_flux": 0.0, "relative_E_0": 0.0, "nonzero_f": "excited structureless flux sector above the minimum"},
        "quantized_or_theta_shifted_model": "minimum depends on an unproved charge lattice, boundary term, and possible branch offset",
        "E_ZPV": "vacuum floor after allowed-state minimization",
        "E_rec": "Z_F f^2 V/2 or the ensemble-equivalent flux energy",
        "E_total": "E_ZPV+E_rec+other sectors",
        "energy_returned_to_exact_floor_while_stored_as_positive_pressure": False,
        "reset_interpretation": "particle-specific structure may be absent from reduced variables while energy occupies a universal nonminimal flux sector",
        "zpv_reset_established": False,
        "local_interference": {"baseline": "homogeneous f where the source-free constraint applies", "boundary_perturbations": ["extrinsic curvature/shear", "frame-dragging geometry", "electromagnetic stress", "radiation/accretion stress", "scalar/topographic modes"], "separate_expansion_bubbles_derived": False},
    }


def recycling_regimes_payload() -> dict[str, Any]:
    return {
        **_common("BHSM_spacetime_recycling_primordial_late_time_map_v5_12"),
        "status": "PRIMORDIAL_AND_LATE_TIME_REGIMES_SEPARATED_BOTH_UNDERIVED",
        "primordial": {"initial_flux": None, "boundary_tension_competition": "source open", "surface_crossing": None, "outward_instability": False, "plasma_conversion": False},
        "late_time": {"black_hole_formation_or_accretion_source": None, "incremental_flux_jump": None, "homogeneous_pressure_change": None, "boundary_expansion_response": None},
        "same_candidate_action_different_initial_data_possible": True,
        "same_action_established_in_BHSM": False,
        "regimes_identified": False,
        "expansion_claims": {"black_holes_cause_expansion": False, "dark_energy_replaced": False, "Hubble_law_derived": False, "cosmological_parameters_used": False},
        "required_future_audits": ["perturbation evolution", "causal initial-value problem", "homogeneous-flux stability", "Berger anisotropy response", "boundary spectrum", "energy-transfer source"],
    }


def stress_tensor_payload() -> dict[str, Any]:
    rows = [
        {"source": "U_boundary", "tangential_stress": "tau_U^AB=(2/sqrt|h|)delta integral sqrt|h| U/delta h_AB; equals U h^AB only if U has no explicit metric dependence under the selected sign convention", "trace": "d_Sigma U plus explicit metric response", "normal_force": "epsilon_n K U+normal field/support variation", "L_scaling": "requires U localization", "a_sigma_rho": "U(T_vac,Phi_vac;a,rho) open", "status": "FORMAL_LOCALIZATION_OPEN"},
        {"source": "c_K K", "tangential_stress": "orientation-dependent Brown-York-type metric variation plus embedding terms", "trace": "not evaluated", "normal_force": "epsilon_n[c_K K^2+D_K^dagger c_K]", "L_scaling": "c_K L^-2 in normal-force density architecture", "a_sigma_rho": "shape dependent", "status": "COEFFICIENT_AND_EMBEDDING_OPEN"},
        {"source": "c_K2 K^2", "tangential_stress": "metric and derivative bending stress", "trace": "not evaluated", "normal_force": "epsilon_n[c_K2 K^3+D_K^dagger(2c_K2 K)]", "L_scaling": "c_K2 L^-3 in force architecture", "a_sigma_rho": "shape dependent", "status": "COEFFICIENT_AND_EMBEDDING_OPEN"},
        {"source": "c_S Tr(S^2)", "tangential_stress": "shape-norm metric and derivative stress", "trace": "not evaluated", "normal_force": "epsilon_n[c_S K Tr(S^2)+D_Q^dagger c_S]", "L_scaling": "c_S L^-3 in force architecture", "a_sigma_rho": "shape dependent", "status": "COEFFICIENT_AND_EMBEDDING_OPEN"},
        {"source": "collar", "tangential_stress": "(2/sqrt|h|)delta S_collar/delta h_AB", "trace": "open", "normal_force": "E_J+E_collar", "L_scaling": "depends on physical rho and B_collar", "a_sigma_rho": "all dependencies explicit but unevaluated", "status": "COLLAR_ACTION_OPEN"},
        {"source": "scalar gradients/potential", "tangential_stress": "standard metric variation only after local T/Phi action and support close", "trace": "open", "normal_force": "p_ST", "L_scaling": "open", "a_sigma_rho": "sigma=1/2 retained; localization open", "status": "REDUCED_ON_SHELL_LOCAL_STRESS_OPEN"},
        {"source": "v5.10 quantum", "tangential_stress": None, "trace": "global one-mode scale response only", "normal_force": None, "L_scaling": "dGamma/dL=-1/L globally", "a_sigma_rho": "homogeneous diagnostic", "status": "NOT_LOCALIZABLE_NO_SURFACE_STRESS"},
    ]
    return {**_common("BHSM_primordial_boundary_stress_tensor_v5_12"), "status": "VARIATIONAL_STRESS_DEFINITION_DERIVED_COMPONENT_VALUES_OPEN", "convention": "delta S_boundary=(1/2)integral dmu_h tau_boundary^AB delta h_AB+field variations", "definition": "tau_boundary^AB=(2/sqrt|h|)delta S_boundary/delta h_AB", "sign_note": "the user-selected positive convention is used; opposite stress conventions must flip consistently", "rows": rows, "complete_numeric_stress": False}


def normal_variation_payload() -> dict[str, Any]:
    return {**_common("BHSM_primordial_normal_displacement_variations_v5_12"), "status": "STANDARD_NORMAL_VARIATION_IDENTITIES_CONDITIONAL_ON_BHSM_EMBEDDING", "displacement": "delta X=xi_perp n", "reference_convention": "K_AB=(1/2)L_n h_AB and outward n; epsilon_n=+1. Opposite normal flips orientation-odd quantities consistently.", "identities": {"delta_h_AB": "2 xi_perp K_AB", "delta_sqrt_abs_h": "K xi_perp sqrt|h|", "delta_dmu_h": "K xi_perp dmu_h", "delta_K_AB": "-nabla_A nabla_B xi_perp+xi_perp(K_A^C K_CB-R_nAnB) under the declared curvature convention", "delta_K": "-Delta_Sigma xi_perp-(Tr(S^2)+Ric(n,n))xi_perp", "delta_K_squared": "2K delta K", "delta_TrS2": "2 Tr(S delta S) plus the inverse-metric variation; equivalently D_Q xi_perp", "delta_J": "J Tr[(I+rho S)^(-1)rho delta S] for the plus collar convention", "delta_log_J": "Tr[(I+rho S)^(-1)rho delta S]", "delta_collar_measure": "delta(J dmu_h d rho)=J[K xi_perp+delta log J]dmu_h d rho plus endpoint variation if rho_star moves"}, "actual_BHSM_orientation_fixed": False, "reason": "v4.1 stores J=det(I +/- rho S); v5.7 selects outward language but does not evaluate the embedding/sign map", "tangential_gauge_distinct": True, "xi_perp_physical_candidate": True}


def pressure_payload() -> dict[str, Any]:
    rows = [
        {"sector": "scalar/topographic vacuum", "inside": "normal variation of localized U and collar threshold", "outside": "not specified", "threshold": "p_ST open", "status": "LOCALIZATION_OPEN"},
        {"sector": "scalar gradients", "inside": "zero in v5.7 homogeneous coordinate reduction", "outside": "not specified", "threshold": "physical gradient stress not established", "status": "REDUCED_ZERO_NOT_PHYSICAL_PRESSURE_THEOREM"},
        {"sector": "gauge", "inside": "zero conditionally at A0=0 and no current", "outside": "not specified", "threshold": "open if excitations present", "status": "CONDITIONAL_BACKGROUND_ZERO"},
        {"sector": "fermion", "inside": "zero conditionally at psi0=0", "outside": "not specified", "threshold": "open", "status": "CONDITIONAL_BACKGROUND_ZERO"},
        {"sector": "charged composite", "inside": "zero conditionally with psi0=0", "outside": "not independent", "threshold": "no independent pressure", "status": "COMPOSITE"},
        {"sector": "neutral response", "inside": "zero only if N0=0 solves sourced equation", "outside": "not specified", "threshold": "normalization open", "status": "CONDITIONAL"},
        {"sector": "collar energy", "inside": "delta S_collar/delta normal volume", "outside": "collar matching open", "threshold": "E_collar open", "status": "ACTION_INTEGRAND_OPEN"},
        {"sector": "geometric vacuum", "inside": None, "outside": None, "threshold": "no normalized bulk vacuum action", "status": "SOURCE_OPEN"},
        {"sector": "quantum", "inside": "global dGamma/dL=-1/L only", "outside": None, "threshold": "not a local pressure", "status": "LOCALIZATION_OPEN"},
        {"sector": "spacetime recycling top form", "inside": "n^A n^B T_AB=-epsilon_n Z_F f^2/2 for the candidate Lorentzian fixed-f solution", "outside": "flux sector and matching unspecified", "threshold": "fixed-f versus fixed-Q boundary ensemble changes the pressure response", "status": "CANDIDATE_STRESS_DERIVED_BHSM_SOURCE_AND_ENSEMBLE_OPEN"},
        {"sector": "primordial excitation", "inside": None, "outside": None, "threshold": "not a stored action term", "status": "SOURCE_OPEN"},
    ]
    return {**_common("BHSM_primordial_inside_outside_pressure_v5_12"), "status": "PRESSURE_JUMP_DEFINITION_EXACT_CONTRIBUTIONS_OPEN", "definition": "Delta p=p_inside-p_outside from the coefficient of xi_perp in the total normal variation", "external_pressure_assumed_zero": False, "static_compact_pressure": "open", "release_threshold_pressure": "open", "post_release_plasma_pressure": "not derived", "late_time_cosmological_pressure": "out of scope and not imported", "hot_plasma_equation_of_state_used": False, "rows": rows}


def curvature_coefficients_payload() -> dict[str, Any]:
    rows = []
    for symbol, term, dimension in (("c_K","K","[A] L^(1-d_Sigma)"),("c_K2","K^2","[A] L^(2-d_Sigma)"),("c_S","Tr(S^2)","[A] L^(2-d_Sigma)")):
        rows.append({"symbol": symbol, "term": term, "dimension": dimension, "existing_unified_action_source": "symbol appears only in v5.6 boundary candidate", "derived_from_unified_action": False, "fixed_by_well_posedness": False, "counterterm_required_and_value_derived": False, "topologically_quantized": False, "quantum_induced": False, "dimensionless_after_scale": "possible only after unresolved ell_BH", "classification": "UNRESOLVED_PRIMITIVE_COEFFICIENT_NOT_YET_ACCEPTED_AS_INPUT", "v5_7_zero": "fixed-geometry scalar-reduction choice, not a geometric theorem"})
    return {**_common("BHSM_primordial_curvature_bending_coefficients_v5_12"), "status": "CURVATURE_BENDING_COEFFICIENT_SOURCES_NOT_CLOSED", "rows": rows, "kappa_geom_relation": "no stored theorem maps provisional kappa_geom L_geom to c_K,c_K2,c_S", "GHY_audit": {"explicit_bulk_Einstein_Hilbert_term": False, "bulk_gravity_normalization": None, "GHY_like_completion_may_be_required": "undecidable without a foundational bulk action and variational data", "standard_gravitational_coefficient_imported": False}, "source_hierarchy_exhausted": ["existing term: symbols only", "variational completion: bulk source absent", "scalar localization: open", "collar integration: open", "topological quantization: none established", "quantum induction/counterterm: v5.10 insufficient", "symmetry/regularity: no values", "primitive scale: not invoked as derived"]}


def collar_stress_payload() -> dict[str, Any]:
    return {**_common("BHSM_primordial_collar_jacobian_stress_v5_12"), "status": "COLLAR_MEASURE_IDENTITY_CONDITIONAL_STRESS_SOURCE_OPEN", "action": "S_collar=integral_Sigma integral_0^rho_star B_collar J d rho dmu_h", "Jacobian": "J(Y,rho)=det(I+epsilon_n rho S(Y))=sqrt(det h(Y,rho)/det h(Y,0))", "epsilon_n": "+/- unresolved orientation", "boundary_value": "J(Y,0)=1 exactly", "variation": {"delta_log_J": "Tr[(I+epsilon_n rho S)^(-1)epsilon_n rho delta S]", "delta_J": "J delta log J", "delta_measure": "J[K xi_perp+delta log J]dmu_h d rho in the plus reference convention", "collar_stress": "metric/shape variation of B_collar J; cannot evaluate without B_collar and embedding"}, "rho_star": {"value_in_v5_7": 1.0, "classification": "dimensionless normalized coordinate endpoint", "physical_thickness": None, "unit_anchor": False, "endpoint_variation": "transversality term B_collar J delta rho_star if rho_star is dynamical"}, "shape_dependence": "exact determinant identity conditional on S", "c_J_zero_meaning": "prevents a duplicate standalone log J term", "J_removed_from_measure": False}


def shape_equation_payload() -> dict[str, Any]:
    terms = [
        {"name":"area/tension","formula":"epsilon_n K T_boundary","source":"localized U_boundary plus collar density","dimension":"[A]L^(-(d_Sigma+1))","sign":"epsilon_n and physical density sign","L_scaling":"T_boundary/L","background":None,"status":"LOCALIZATION_OPEN"},
        {"name":"K","formula":"epsilon_n[c_K K^2+D_K^dagger c_K]","source":"v5.6 c_K K candidate","dimension":"[A]L^(-(d_Sigma+1))","sign":"orientation odd/even combination convention-dependent","L_scaling":"c_K/L^2","background":None,"status":"COEFFICIENT_EMBEDDING_OPEN"},
        {"name":"K2","formula":"epsilon_n[c_K2 K^3+D_K^dagger(2c_K2 K)]","source":"v5.6 c_K2 K^2 candidate","dimension":"[A]L^(-(d_Sigma+1))","sign":"orientation from normal force","L_scaling":"c_K2/L^3","background":None,"status":"COEFFICIENT_EMBEDDING_OPEN"},
        {"name":"shape_norm","formula":"epsilon_n[c_S K Tr(S^2)+D_Q^dagger c_S]","source":"v5.6 c_S Tr(S^2) candidate","dimension":"[A]L^(-(d_Sigma+1))","sign":"orientation from normal force","L_scaling":"c_S/L^3","background":None,"status":"COEFFICIENT_EMBEDDING_OPEN"},
        {"name":"Jacobian","formula":"E_J from delta log J","source":"v4.1/v5.6 collar measure","dimension":"[A]L^(-(d_Sigma+1)) after physical lift","sign":"epsilon_n open","L_scaling":"depends on rho physical scaling","background":None,"status":"B_COLLAR_AND_S_OPEN"},
        {"name":"collar","formula":"E_collar from delta B_collar and endpoint terms","source":"v5.6 symbolic collar action","dimension":"[A]L^(-(d_Sigma+1))","sign":"action variation","L_scaling":"open","background":None,"status":"INTEGRAND_OPEN"},
        {"name":"scalar_pressure","formula":"p_ST","source":"localized scalar/topographic action","dimension":"[A]L^(-(d_Sigma+1))","sign":"inside-minus-outside convention","L_scaling":"open","background":None,"status":"LOCALIZATION_OPEN"},
        {"name":"quantum","formula":"E_quantum","source":"no local source; v5.10 is global only","dimension":"open","sign":"not available","L_scaling":"global Hessian 1/L^2 only","background":None,"status":"OPEN_NOT_RETAINED_AS_DERIVED_LOCAL_TERM"},
        {"name":"recycling_pressure","formula":"-Delta p_rec in the current Delta p=p_inside-p_outside convention","source":"candidate top-form metric variation; no stored BHSM source","dimension":"[A]L^-d_B as bulk stress before boundary projection","sign":"p_rec=-rho_rec at fixed local f; fixed-Q mechanical ensemble differs; epsilon_n and boundary term open","L_scaling":"fixed f is constant density; fixed Q scales as V^-2 before mode normalization","background":None,"status":"CANDIDATE_DERIVED_SOURCE_ENSEMBLE_AND_PROJECTION_OPEN"},
        {"name":"pressure_jump","formula":"-Delta p","source":"total inside/outside action variation","dimension":"[A]L^(-(d_Sigma+1))","sign":"Delta p=p_inside-p_outside","L_scaling":"open","background":None,"status":"SOURCE_OPEN"},
    ]
    return {**_common("BHSM_primordial_normal_shape_equation_v5_12"), "status": "SOURCE_SEPARATED_SHAPE_ARCHITECTURE_DERIVED_PHYSICAL_EQUATION_OPEN", "formula": "E_perp=epsilon_n K F_boundary+D_K^dagger(c_K+2c_K2 K)+D_Q^dagger(c_S)+E_J+E_collar+p_ST+E_quantum-Delta p_other-Delta p_rec", "F_boundary": "T_boundary+c_K K+c_K2 K^2+c_S Tr(S^2)", "pressure_decomposition": "p_ST remains the v5.11 signed normal-force label; Delta p_other excludes ST and recycling. If localization later identifies p_ST as an inside thermodynamic pressure, it must be absorbed into Delta p_total and removed as a separate term.", "recycling_addition": "-Delta p_rec; not +p_rec by hand", "equation": "E_perp=0", "terms": terms, "all_named_terms_have_source_or_open_status": True, "background_residual": None, "background_on_shell": False, "complete_physical_equation_derived": False}


def surface_hessian_payload() -> dict[str, Any]:
    return {**_common("BHSM_primordial_surface_hessian_eigenproblem_v5_12"), "status": "SURFACE_HESSIAN_ARCHITECTURE_DERIVED_OPERATOR_DOMAIN_OPEN", "definition": "H_surface=delta E_perp/delta xi_perp at B0", "eigenproblem": "H_surface xi_n=lambda_n xi_n", "principal_symbol": "B_eff(a,sigma,rho;c_K2,c_S)|k|^4+T_eff(a,sigma,rho;T_boundary,c_K)|k|^2", "B_eff": "linear combination of c_K2,c_S with embedding-dependent contractions", "T_eff": "localized tension plus K-sector contributions", "potential": "curvature cubics, Ric(n,n), pressure derivatives, collar and scalar response", "curvature_terms": "delta D_K and delta D_Q", "collar_terms": "delta(E_J+E_collar)", "scalar_terms": "delta p_ST", "pressure_terms": "-delta(Delta p_other+Delta p_rec)", "recycling_terms": {"definition":"H_rec=-delta Delta p_rec/delta xi_perp in the current pressure convention", "fixed_local_f":"direct delta p_rec=0; the constant pressure shifts the background equilibrium and affects the combined Hessian only through that on-shell background", "fixed_Q":"delta p_rec=(dp/dV) integral_Sigma xi dA, a rank-one global response", "uniform_radial_mode":"nonzero mean and therefore can couple", "Berger_anisotropic_modes":"only their volume-changing mean component couples directly", "higher_zero_mean_modes":"zero direct rank-one projection", "localized_core_adjacent_modes":"not derivable without a local source/matching solution", "mode_independent_shift":False, "sign":"ensemble, orientation, and boundary term dependent"}, "quantum_terms": "OPEN; global v5.10 projection not local", "lowest_eigenvalue": "lambda_surface(L,a,sigma,rho_star,f;c)=min_n lambda_n after proven gauge/Killing projections", "scaling_architecture": "T_boundary q_tau/L^2+c_K q_K/L^3+(c_K2 q_K2+c_S q_S)/L^4+lambda_collar+lambda_ST+lambda_rec+lambda_quantum", "scaling_origins": {"L^-2":"two derivatives/curvatures in the tension area-Jacobi Hessian", "L^-3":"one K density plus its second normal variation", "L^-4":"bending/shape densities with two curvatures and two further variation derivatives", "collar":"not assignable until physical rho and B_collar localize", "scalar_topographic":"not assignable until local stress response closes", "recycling":"fixed f and fixed Q give distinct volume laws; conversion to an eigenvalue requires V(L,a), the boundary ensemble, and mode normalization", "quantum":"global 1/L^2 diagnostic cannot be inserted locally"}, "Berger_dependence": "q functions, volume v(a), and curvature potential depend on a; not evaluated", "sigma_dependence": "through localized U,p_ST and background sigma=1/2; map open", "rho_star_dependence": "through collar integral and endpoint; rho_star=1 only normalized", "flux_dependence": "f^2 at fixed local flux or Q^2/V^2 at fixed integrated flux", "field_space": "real normal sections xi_perp", "inner_product": "integral_Sigma xi eta dmu_h times unresolved normalization", "candidate_domain": "H^4(Sigma) for nonzero bending symbol, H^2(Sigma) for purely second order", "boundary_conditions": "if closed Berger Sigma has no edge, integration boundary form vanishes formally; collar and top-form ensemble/matching conditions remain open", "formal_closed_surface_boundary_form_zero": True, "physical_domain_closed": False, "self_adjoint": False, "strongly_elliptic": False, "uniform_mode_only_assumed": False, "zero_modes": "isometries/gauge projection and collective radial mode classification open", "negative_modes": "not computable"}


def reduced_lambda(L: float, A2: float, A3: float, A4: float) -> float:
    if L <= 0.0:
        raise ValueError("L must be positive")
    return A2 / L**2 + A3 / L**3 + A4 / L**4


def reduced_lambda_derivative(L: float, A2: float, A3: float, A4: float) -> float:
    if L <= 0.0:
        raise ValueError("L must be positive")
    return -2.0*A2/L**3-3.0*A3/L**4-4.0*A4/L**5


def top_form_local_degrees_of_freedom(d_bulk: int) -> int:
    """Local polarizations of a massless (d_bulk-1)-form in d_bulk dimensions."""
    if d_bulk < 2:
        raise ValueError("d_bulk must be at least two")
    return 0


def top_form_degrees(d_bulk: int) -> tuple[int, int]:
    if d_bulk < 2:
        raise ValueError("d_bulk must be at least two")
    return d_bulk - 1, d_bulk


def top_form_lorentzian_stress_data(Z_F: float, f: float) -> dict[str, float]:
    """Vacuum-like stress data for F=f vol with one timelike direction."""
    rho = 0.5 * Z_F * f**2
    return {"metric_coefficient": -rho, "energy_density": rho, "pressure": -rho}


def top_form_energy(
    L: float,
    Z_F: float,
    amplitude: float,
    volume_coefficient: float,
    volume_power: float,
    ensemble: str,
) -> float:
    """Reduced positive-Z top-form energy for fixed f or fixed Q."""
    if L <= 0.0 or volume_coefficient <= 0.0 or volume_power <= 0.0:
        raise ValueError("L, volume_coefficient, and volume_power must be positive")
    volume = volume_coefficient * L**volume_power
    if ensemble == "fixed_f":
        return 0.5 * Z_F * amplitude**2 * volume
    if ensemble == "fixed_Q":
        return 0.5 * Z_F * amplitude**2 / volume
    raise ValueError("ensemble must be fixed_f or fixed_Q")


def top_form_pressure(
    L: float,
    Z_F: float,
    amplitude: float,
    volume_coefficient: float,
    volume_power: float,
    ensemble: str,
) -> float:
    """Mechanical pressure -dE/dV in the declared reduced ensemble."""
    if L <= 0.0 or volume_coefficient <= 0.0 or volume_power <= 0.0:
        raise ValueError("L, volume_coefficient, and volume_power must be positive")
    volume = volume_coefficient * L**volume_power
    if ensemble == "fixed_f":
        return -0.5 * Z_F * amplitude**2
    if ensemble == "fixed_Q":
        return 0.5 * Z_F * amplitude**2 / volume**2
    raise ValueError("ensemble must be fixed_f or fixed_Q")


def top_form_radial_force_and_stiffness(
    L: float,
    Z_F: float,
    amplitude: float,
    volume_coefficient: float,
    volume_power: float,
    ensemble: str,
) -> tuple[float, float]:
    """Return -dE/dL and d2E/dL2 for the reduced collective mode."""
    energy = top_form_energy(L, Z_F, amplitude, volume_coefficient, volume_power, ensemble)
    if ensemble == "fixed_f":
        force = -volume_power * energy / L
        stiffness = volume_power * (volume_power - 1.0) * energy / L**2
    else:
        force = volume_power * energy / L
        stiffness = volume_power * (volume_power + 1.0) * energy / L**2
    return force, stiffness


def conditional_flux_jump(f_minus: float, q_rec: float, Z_F: float, orientation: float = 1.0) -> float:
    """Thin codimension-one source jump Z_F(f_plus-f_minus)=orientation*q_rec."""
    if Z_F == 0.0:
        raise ValueError("Z_F must be nonzero")
    return f_minus + orientation * q_rec / Z_F


def homogeneous_pressure_hessian(mode_volume_overlaps: list[float], dp_dV: float) -> list[list[float]]:
    """Rank-one fixed-Q pressure response in a normal-mode basis."""
    return [[dp_dV * left * right for right in mode_volume_overlaps] for left in mode_volume_overlaps]


def closed_energy_balance(*reservoir_changes: float) -> float:
    """Residual of the closed-system energy-transfer ledger."""
    return sum(reservoir_changes)


def pure_tension_stress(U: float, inverse_metric: list[list[float]]) -> list[list[float]]:
    """Metric-independent density contribution under the declared positive convention."""
    size=len(inverse_metric)
    if any(len(row)!=size for row in inverse_metric):
        raise ValueError("inverse metric must be square")
    return [[U*inverse_metric[i][j] for j in range(size)] for i in range(size)]


def collar_log_jacobian_variation(rho: float, shape_eigenvalues: list[float], variations: list[float]) -> float:
    """Diagonal check of Tr[(I+rho S)^-1 rho delta S]."""
    if len(shape_eigenvalues)!=len(variations):
        raise ValueError("shape and variation lists must match")
    denominators=[1.0+rho*value for value in shape_eigenvalues]
    if any(abs(value)<1e-15 for value in denominators):
        raise ValueError("collar Jacobian is singular")
    return sum(rho*delta/denom for delta,denom in zip(variations,denominators))


def reduced_normal_force(xi_perp: float, L: float, A2: float, A3: float, A4: float) -> float:
    """Linear normal equation for the deterministic uniform-mode diagnostic."""
    return reduced_lambda(L,A2,A3,A4)*xi_perp


def positive_roots(A2: float, A3: float, A4: float, tolerance: float = 1e-12) -> list[float]:
    """Solve A2 L^2+A3 L+A4=0 for positive isolated roots."""
    if abs(A2) <= tolerance:
        if abs(A3) <= tolerance:
            return []
        root = -A4/A3
        return [root] if root > tolerance else []
    disc = A3*A3-4.0*A2*A4
    if disc < -tolerance:
        return []
    disc = max(0.0, disc)
    roots = [(-A3-sqrt(disc))/(2.0*A2), (-A3+sqrt(disc))/(2.0*A2)]
    result: list[float] = []
    for root in sorted(roots):
        if root > tolerance and all(abs(root-old)>tolerance for old in result):
            result.append(root)
    return result


def classify_crossing(root: float, A2: float, A3: float, A4: float, tolerance: float = 1e-9) -> str:
    slope = reduced_lambda_derivative(root,A2,A3,A4)
    if abs(slope) <= tolerance:
        return "TANGENTIAL_TOUCH"
    eps = min(root*1e-5,1e-5)
    before = reduced_lambda(root-eps,A2,A3,A4)
    after = reduced_lambda(root+eps,A2,A3,A4)
    if before > 0.0 and after < 0.0:
        return "STABLE_TO_UNSTABLE_FOR_INCREASING_L"
    if before < 0.0 and after > 0.0:
        return "UNSTABLE_TO_STABLE_FOR_INCREASING_L"
    return "NUMERICALLY_UNRESOLVED_CROSSING"


def release_threshold_payload() -> dict[str, Any]:
    return {**_common("BHSM_primordial_release_threshold_crossing_v5_12"), "status": "RELEASE_CONDITION_DEFINED_NO_PHYSICAL_ROOT_EVALUABLE", "definition": "lambda_surface(L,a,sigma,rho_star,f;c)=min spec'(H_surface)", "condition": "lambda_surface(L_c)=0", "requirements": ["L_c>0", "real physical mode", "self-adjoint operator", "finite sourced coefficients", "on-shell background", "no gauge contamination"], "finite_L_c": None, "number_of_roots": None, "crossing_direction": None, "stable_before": None, "unstable_after": None, "unique": None, "physical": False, "action_derived": False, "energy_threshold": {"E_break": None, "relation_to_tension": "could be integral of localized surface density or a normal-mode barrier, not yet distinguishable", "relation_to_L_c": None, "barrier_interpretation": "open"}, "competing_scaling_theorem": {"statement": "A single nonzero homogeneous term A L^-p has no isolated positive finite zero.", "necessary_conditions": ["at least two nonzero contributions", "different scale powers or non-polynomial dependence unless coefficients themselves vary", "opposing signs somewhere on the physical branch", "valid coefficient sources", "valid physical mode/domain"], "proof": "L^-p is nonzero for finite positive L, so A L^-p=0 implies A=0; A=0 is an identically flat direction, not an isolated threshold.", "classification_current": "IMPOSSIBLE_TO_CLASSIFY_PHYSICALLY_SOURCE_OPEN"}, "recycling_competing_scaling": {"volume_law":"V(L,a)=v(a)L^nu with nu not fixed until the physical canonical domain closes", "fixed_f_energy":"E_rec=(Z_F f^2/2)v(a)L^nu", "fixed_f_radial_stiffness":"proportional to L^(nu-2)", "fixed_Q_energy":"E_rec=Z_F Q^2/[2v(a)L^nu]", "fixed_Q_radial_stiffness":"proportional to L^(-nu-2)", "eigenvalue_conversion":"requires the xi_perp inner-product normalization and on-shell background", "candidate_root_formula":None, "reason_no_root":"Z_F, f or Q, boundary ensemble, tension, volume exponent, mode projection, and signs are not jointly action-derived", "absolute":False}, "illustrative_cases": [{"A2":-1.0,"A3":0.0,"A4":1.0,"roots":[1.0],"classification":"STABLE_TO_UNSTABLE_FOR_INCREASING_L"},{"A2":1.0,"A3":-2.0,"A4":1.0,"roots":[1.0],"classification":"TANGENTIAL_TOUCH"},{"A2":1.0,"A3":-3.0,"A4":2.0,"roots":[1.0,2.0],"classification":"MULTIPLE_CROSSINGS"}], "illustrative_values_are_BHSM_coefficients": False}


def absolute_one_scale_payload() -> dict[str, Any]:
    return {**_common("BHSM_primordial_absolute_unit_one_scale_v5_12"), "status": "ABSOLUTE_UNIT_NOT_DERIVED_MINIMAL_ONE_SCALE_THEOREM_NOT_YET_AVAILABLE", "absolute_test": {"finite_L_c": None, "measured_input": False, "arbitrary_mu": False, "box_size": False, "rho_star_as_length": False, "wavepacket_width": False, "reference_radius": False, "inserted_gravity_or_electroweak_scale": False, "arbitrary_initial_flux": False, "unproved_flux_quantum": False, "black_hole_mass_input": False, "present_expansion_rate_input": False, "passes": False}, "recycling_sources": {"Z_F_derived":False,"q_rec_derived_or_quantized":False,"flux_quantum_normalized":False,"initial_f_action_selected":False,"boundary_ensemble_fixed":False,"tension_and_flux_competition_closed":False}, "outputs": {"ell_star": None, "M_star": None, "M_BH": None, "R_BH": None}, "relative_results_preserved": {"sigma_scale":"1/2","M_BH_over_M_star":"1/2","R_BH_over_ell_star":"2"}, "minimal_one_scale": {"primitive_tension_required": "a dimensionful source is necessary for physical localization but sufficiency is not proved", "primitive_breaking_energy_required": "alternative open route", "primitive_recycling_candidates":["boundary tension quantum","top-form flux quantum","core conversion charge","universal recycling-energy quantum"], "candidate_selected":None, "all_dimensionless_ratios_derived": False, "one_scale_theorem": False, "candidate_if_future_ratios_close": "L_c=C_L([hbar]/T_primitive)^(1/d_Sigma) or a dimensionally derived tension/flux ratio law after both source dimensions close", "exponent_currently_derived_as_physical_BHSM_law": False, "classification": "NOT_READY_FOR_BHSM_MINIMAL_ONE_SCALE_BOUNDARY_PRINCIPLE_REQUIRED"}, "hidden_scale": None}


def energy_conversion_payload() -> dict[str, Any]:
    return {**_common("BHSM_primordial_release_energy_conversion_v5_12"), "status": "PRIMORDIAL_AND_RECYCLING_ENERGY_CONVERSION_LEDGERS_CONDITIONAL_NOT_DERIVED", "time_split_available": False, "reason": "the boundary action does not decide whether Sigma includes time, so a Hamiltonian surface energy is not localized", "conservation_template": "E_initial=E_expansion+E_plasma+E_residual", "ledger": {"initial_boundary_energy": None, "initial_interior_field_energy": None, "released_geometric_energy": None, "normal_mode_kinetic_energy": None, "expansion_energy": None, "particle_radiation_or_plasma_energy": None, "residual_boundary_topographic_memory": None}, "recycling_global_ledger": {"equation":"d/dt(E_matter+E_BH+E_rec+E_boundary+E_ST+E_radiation)=declared_external_flux", "closed_external_flux":0.0,"component_values":None,"action_derived_transfer":False}, "core_event_ledger": {"equation":"dot E_infall=dot E_BH_stored+dot E_rec+dot E_radiation+dot E_other","infall_energy":None,"black_hole_retained_energy":None,"bulk_recycling_energy":None,"boundary_work":None,"radiation":None,"residual":None,"epsilon_rec":None,"epsilon_rec_status":"UNRESOLVED_NOT_FITTED"}, "charge_information_entropy": {"exact_charges_erased":False,"complete_state_unitarity":None,"coarse_grained_irreversibility":None,"conditional_inequality":"Delta S_accessible+Delta S_BH+Delta S_rec>=0","entropy_destroyed":False,"topological_sector_change":None}, "conservation_status": "FORMAL_IDENTITY_ONLY_NO_CORE_TRANSFER_MECHANISM", "temperature": None, "abundance": None, "baryogenesis": None, "reheating": None, "pilot_wave_connection": {"marginal_surface_mode": "candidate lambda_surface=0", "outgoing_guidance": "v5.9 d ln L/dtau=k is outward only on an outgoing k>0 branch", "outgoing_branch_selected_by_action": False, "surface_threshold_in_v5_9_Hamiltonian": False, "pilot_wave_generates_threshold": False, "recycling_generates_threshold":False, "double_counting_avoided": True, "expanding_trajectory": "conditional after an independently derived threshold"}}


def reduced_model_payload() -> dict[str, Any]:
    cases = []
    for label, coefficients in (("stable_to_unstable",(-1.0,0.0,1.0)),("tangent",(1.0,-2.0,1.0)),("multiple",(1.0,-3.0,2.0)),("single",(1.0,0.0,0.0))):
        roots = positive_roots(*coefficients)
        cases.append({"label":label,"A2":coefficients[0],"A3":coefficients[1],"A4":coefficients[2],"roots":roots,"crossings":[classify_crossing(root,*coefficients) for root in roots]})
    return {**_common("BHSM_primordial_reduced_threshold_model_v5_12"), "status": "DETERMINISTIC_BOUNDARY_AND_RECYCLING_MODELS_EXACT_COEFFICIENTS_ILLUSTRATIVE", "variables": ["L","a_Berger","sigma_scale=1/2","rho_star","uniform xi_perp","tau","f_or_Q","Z_F","q_rec"], "local_model": "lambda_red=A2/L^2+A3/L^3+A4/L^4", "coefficient_map": {"A2":"localized tension/scalar/collar second-order combination", "A3":"c_K shape combination", "A4":"c_K2 and c_S bending combination"}, "recycling_model": {"volume":"V=v(a)L^nu", "fixed_f_energy":"Z_F f^2 v(a)L^nu/2", "fixed_Q_energy":"Z_F Q^2/[2v(a)L^nu]", "flux_jump":"f_plus=f_minus+orientation*q_rec/Z_F", "fixed_f_pressure":"-Z_F f^2/2", "fixed_Q_pressure":"+Z_F Q^2/(2V^2)", "surface_correction":"zero direct delta-p at fixed f; rank-one mean-mode response at fixed Q", "boundary_tension_scalar_pressure_and_collar":"remain symbolic additive sectors"}, "expansion_equation": {"candidate_reduced_action":"S_L=integral dt[(1/2)M_L(L)dot L^2-V_boundary(L)-E_rec(L)]", "euler_lagrange":"M_L ddot L+(1/2)M_L'(dot L)^2+V_boundary'(L)+E_rec'(L)=0", "M_L_action_derived":False,"actual_BHSM_evolution_equation_derived":False,"static_branch":None,"expanding_branch":None,"acceleration":None,"monotonic":None,"runaway":None,"boundedness":"E_rec is nonnegative for Z_F>0, but total boundedness requires V_boundary and the ensemble","Hubble_law_postulated":False}, "valid_global_quantum_diagnostic": {"formula":"d2 Gamma_perp/dL2=1/L^2","stored_separately":True,"added_to_local_A2":False,"reason":"no xi_perp localization map"}, "representative_cases": cases, "single_term_has_positive_root": False, "root_polynomial": "A2 L^2+A3 L+A4=0", "scale_covariance": "boundary roots and recycling scales remain covariant when every dimensionful coefficient and flux transforms with its physical dimension", "primitive_scale_dependence": "f or Q is arbitrary initial data unless a normalized charge lattice and source law are derived; it cannot anchor L", "illustrative_coefficients_promoted": False}


def construction_report_payload() -> dict[str, Any]:
    return {**_common("BHSM_primordial_boundary_tension_action_source_closure_report_v5_12"), "status": PRIMARY_RESULT, "central_answer": "The current BHSM boundary/collar action does not contain enough physically normalized structure to select a finite L_c. A mathematically consistent top-form constraint architecture exists as a recycling candidate, but BHSM supplies neither its action normalization nor a conserved black-hole/core codimension-one source, boundary ensemble, or flux initial-data law.", "artifact_status": {key: f"artifacts/{name}" for key,name in ARTIFACT_FILES.items() if key != "construction_report"}, "derived": ["v5.4 normalized boundary coordinate count d^3x separated from unresolved physical domain/signature", "coefficient dimension rules for symbolic d_Sigma with hbar retained", "proof that -1/8 is a normalized mixed mode-space value without a local inverse map", "variational stress definition and convention-controlled normal displacement identities", "source-separated pressure, shape equation, collar variation, and surface-Hessian architecture", "competing-scaling theorem and exact reduced root/crossing classifier", "general d_B top-form field equation, vacuum-like candidate stress, zero local polarization count, ensemble-dependent pressure, and mean-mode projection theorem"], "conditionally_established": ["formal closed-surface integration has no edge boundary form, while collar matching remains open", "different sourced scale powers with opposing signs can generate a finite root", "an outgoing v5.9 branch has outward guidance if k>0 after an independently generated threshold", "a source-free top form is constant per connected component and can carry a global flux variable", "a conserved codimension-one source would make the flux piecewise constant with Z_F Delta f=orientation*q_rec", "fixed-Q homogeneous pressure gives a rank-one volume-mode Hessian rather than an equal shift of every normal harmonic"], "invalidated_or_ruled_out": ["-1/8 is not a physical boundary tension", "v5.7 c_K=c_K2=c_S zeros are not geometric theorems", "kappa_geom does not source a GHY coefficient or bending coefficients", "a single homogeneous tension term cannot create an isolated finite release root", "rho_star=1 is not a physical collar thickness", "mu cannot become L_c", "v5.10 global response is not local Casimir pressure", "the current data do not prove a minimal one-scale theorem", "a black-hole worldline is not automatically the electric source for C_[d_B-1]", "homogeneous constraint data do not permit controllable superluminal signaling", "nonzero f^2 energy is not the pristine vacuum floor", "black holes are not proved to cause expansion", "dark energy or inflation is not replaced", "the old curvature-threshold mass-gap theorem remains invalidated"], "still_requiring_new_mathematics": list(OPEN_GATES), "absolute_unit": {"ell_star":None,"M_star":None,"M_BH":None,"R_BH":None}, "black_hole_spacetime_recycling_candidate": {"result_label":RECYCLING_RESULT,"bulk_dimension":None,"candidate_top_form":"C_[d_B-1], F_[d_B]=dC","normalization":None,"local_degrees_of_freedom":0,"global_flux_degree":"conditional one per connected compact component","core_source":None,"flux_jump":"conditional only","stress_tensor":"-(Z_F f^2/2)G_AB in the Lorentzian candidate","p_recycle":"-rho_rec at fixed local f; fixed-Q mechanical ensemble differs","lambda_recycle":None,"expansion_equation":"formal collective equation only","zpv_reset":False,"energy_transfer_closed":False,"absolute_unit_contribution":None}, "claim_safe_conclusion": "BHSM v5.12 derives a source-qualified primordial surface-stability architecture and identifies a viable candidate top-form constraint mechanism, but neither the physical boundary source nor the recycling source closes. No physical L_c, absolute unit, black-hole-driven expansion, ZPV reset, rupture history, hot plasma, Casimir energy, mass, coupling, CKM result, rare-B prediction, or BHSM completion follows.", "recommended_next_construction_sprint": "bhsm-scalar-topographic-physical-localization-v5-13"}


def build_artifact_payloads(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    _ = repo_root
    return {"action_source":action_source_payload(),"dimension_localization":dimension_localization_payload(),"stress_tensor":stress_tensor_payload(),"normal_variation":normal_variation_payload(),"pressure":pressure_payload(),"curvature_coefficients":curvature_coefficients_payload(),"collar_stress":collar_stress_payload(),"shape_equation":shape_equation_payload(),"surface_hessian":surface_hessian_payload(),"release_threshold":release_threshold_payload(),"absolute_one_scale":absolute_one_scale_payload(),"energy_conversion":energy_conversion_payload(),"reduced_model":reduced_model_payload(),"construction_report":construction_report_payload(),"recycling_action":recycling_action_payload(),"top_form_dimension":top_form_dimension_payload(),"core_source":core_source_payload(),"recycling_stress":recycling_stress_payload(),"causal_constraint":causal_constraint_payload(),"zero_point_flux":zero_point_flux_payload(),"recycling_regimes":recycling_regimes_payload()}


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=False)+"\n"


def materialize_artifacts(root: Path) -> list[Path]:
    target=root/"artifacts"; target.mkdir(parents=True,exist_ok=True)
    payloads=build_artifact_payloads(root); written=[]
    for key,name in ARTIFACT_FILES.items():
        path=target/name; path.write_text(deterministic_json(payloads[key]),encoding="utf-8"); written.append(path)
    return written


def boundary_tension_status_report(repo_root: Path | None = None) -> dict[str, Any]:
    _=repo_root
    report=construction_report_payload(); report["artifacts"]={key:f"artifacts/{name}" for key,name in ARTIFACT_FILES.items()}
    return report


def boundary_tension_status_to_markdown(report: dict[str, Any]) -> str:
    return "\n".join(["# BHSM v5.12 Primordial Boundary-Tension Action Source Closure","",f"Primary result: `{report['primary_result']}`.",f"Recycling result: `{report['recycling_result']}`.","",report["central_answer"],"","The normalized vacuum value `-1/8` is not a physical tension, `rho_star=1` is not a length, the v5.10 global diagnostic is not a local pressure, and an arbitrary top-form flux is not an absolute unit.","","## Open gates","",*[f"- `{gate}`" for gate in report["still_requiring_new_mathematics"]]])+"\n"
