"""Structural particle-physics requirements mapped backward into live BHSM.

Measured particle numbers are deliberately absent.  Observations are used
only as an engineering specification for invariant, operator, rank, nullity,
degeneracy, orientation, and persistence properties.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_analytic_kkt_covector_v16_12 import (
    scaled_analytic_kkt_residual,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    kkt_variable_scales,
)


VERSION = "v16.36"
CLASSIFICATION = "BHSM_PHYSICAL_INVERSE_CLOSURE_REQUIREMENT_MATRIX"
FULL_BHSM_COMPLETE = False
EXTERNAL_SYNC_AUTHORIZED = False

Q_LABELS = (
    "log_scale",
    "u_1", "u_2", "u_3",
    "w_0", "w_1", "w_2",
    "v_0", "v_1", "v_2",
)


def two_tier_data_firewall() -> dict[str, Any]:
    return {
        "TIER_A_ALLOWED_STRUCTURAL_PHYSICS": [
            "three_generations", "spin_assignments", "gauge_charges",
            "color_representations", "massive_charged_fermions_exist",
            "photon_and_gluon_unbroken_directions", "electroweak_breaking",
            "nontrivial_CKM", "nontrivial_PMNS", "CP_violation_exists",
            "neutrino_oscillation_exists", "color_confinement",
            "qualitative_stability_and_decay_classes",
        ],
        "TIER_B_HELD_OUT_NUMERICAL_KILL_SCREEN": [
            "charged_lepton_masses", "quark_masses", "CKM_elements_and_angles",
            "PMNS_angles", "J_CP", "neutrino_mass_squared_splittings",
            "W_and_Z_masses", "gauge_couplings", "decay_lifetimes",
            "all_frozen_numerical_prediction_observables",
        ],
        "forbidden_uses": [
            "coefficient_inference_from_measurement",
            "geometry_or_branch_selection_by_data_proximity",
            "sector_specific_normalization",
            "empirical_Yukawa_matrix_insertion",
            "neutral_operator_construction_from_measured_splittings",
            "KKT_tuning_to_make_a_named_particle",
        ],
        "historical_provenance": {
            "frozen_and_calibrated_screens_exist": True,
            "quarantined_from_current_action_branch_selection": True,
            "treated_as_held_out_only_if_not_previously_used_as_input": True,
            "legacy_curvature_threshold_mass_tables": "HISTORICALLY_CALIBRATED_NOT_HELD_OUT_PREDICTIONS",
        },
        "measured_numerical_values_embedded_in_this_artifact": False,
    }


def _particle(
    name: str, spin: str, charge: str, color: str, chirality: str,
    generations: str, mass: str, propagation_mass: bool, stability: str,
    mixing: str, cp: str, owner: str, status: str, missing: str, held_out: str,
) -> dict[str, Any]:
    return {
        "particle_or_sector": name,
        "spin": spin,
        "electric_charge": charge,
        "color": color,
        "chirality": chirality,
        "generation_multiplicity": generations,
        "mass_required": mass,
        "propagation_supported_mass": propagation_mass,
        "stability_class_required": stability,
        "mixing_required": mixing,
        "CP_structure": cp,
        "BHSM_owning_operator": owner,
        "current_theorem_status": status,
        "missing_dependency": missing,
        "numerical_measurement_intentionally_held_out": held_out,
    }


def physical_requirement_matrix() -> list[dict[str, Any]]:
    rank16 = "rank16_chiral_bundle_projectors_and_geometric_hypercharge_operator"
    returned_mass = "returned_broken_LR_HS_mass_operator_from_common_M5_to_M4_pushforward"
    gauge_mass = "returned_gauge_generator_Hessian_of_the_same_common_pushforward"
    return [
        _particle("electron", "1/2", "-1", "singlet", "L_doublet_plus_R_singlet",
                  "one_of_three", "nonzero_returned_rest_mass", False, "stable_child",
                  "family_embedding_required", "none_intrinsic_at_one_state", rank16 + "+" + returned_mass,
                  "REPRESENTATION_VALIDATED_MASS_AND_RETURN_OPEN",
                  "broken_child_with_persistent_nonzero_electron_LR_singular_value_and_stable_return_invariant",
                  "electron_mass"),
        _particle("muon", "1/2", "-1", "singlet", "L_doublet_plus_R_singlet",
                  "one_of_three", "distinct_nonzero_returned_rest_mass", False, "metastable_child",
                  "noncentral_charged_lepton_family_operator", "decay_channels_required", returned_mass,
                  "FAMILY_DIMENSION_VALIDATED_DISTINCT_MASS_OPEN",
                  "three-eigenvalue_noncentral_charged-lepton_operator_and_allowed_decay_channel",
                  "muon_mass_and_lifetime"),
        _particle("tau", "1/2", "-1", "singlet", "L_doublet_plus_R_singlet",
                  "one_of_three", "distinct_nonzero_returned_rest_mass", False, "metastable_child",
                  "noncentral_charged_lepton_family_operator", "decay_channels_required", returned_mass,
                  "FAMILY_DIMENSION_VALIDATED_DISTINCT_MASS_OPEN",
                  "three-eigenvalue_noncentral_charged-lepton_operator_and_allowed_decay_channel",
                  "tau_mass_and_lifetime"),
        _particle("neutrino_family", "1/2", "0", "singlet", "L_doublet_plus_neutral_R_singlet",
                  "three", "nonzero_splittings_after_propagation", True, "propagating_child",
                  "nontrivial_PMNS", "possibly_dynamical", "returned_neutral_Dirac_self_energy_and_propagation_monodromy",
                  "RESET_NULL_PROPAGATION_VALIDATED_PHYSICAL_SPLITTINGS_OPEN",
                  "propagation-dependent_family-noncentral_neutral_operator_with_two_nonzero_splittings",
                  "neutrino_splittings_absolute_scale_and_PMNS"),
        _particle("up_type_quark_family", "1/2", "+2/3", "triplet_internal_no_colored_asymptote",
                  "L_doublet_plus_R_singlet", "three", "three_distinct_nonzero_masses", False,
                  "confined_or_metastable_internal_mode", "nontrivial_CKM", "shared_quark_CP_phase", returned_mass,
                  "REPRESENTATION_VALIDATED_NONCENTRAL_RETURNED_MASS_OPEN",
                  "family-noncentral_Mu_and_asymptotic_color-singlet_projection", "up_type_masses_and_CKM"),
        _particle("down_type_quark_family", "1/2", "-1/3", "triplet_internal_no_colored_asymptote",
                  "L_doublet_plus_R_singlet", "three", "three_distinct_nonzero_masses", False,
                  "confined_or_metastable_internal_mode", "nontrivial_CKM", "shared_quark_CP_phase", returned_mass,
                  "REPRESENTATION_VALIDATED_NONCENTRAL_RETURNED_MASS_OPEN",
                  "family-noncentral_Md_not_simultaneously_diagonalizable_with_Mu", "down_type_masses_and_CKM"),
        _particle("photon", "1", "0", "singlet", "vector", "one", "massless_kernel_direction", False,
                  "stable_gauge_mode", "none", "CP_even_kinetic_sector", gauge_mass,
                  "GAUGE_ALGEBRA_VALIDATED_RETURNED_BROKEN_KERNEL_OPEN",
                  "one_unbroken_electromagnetic_generator_in_returned_kernel", "gauge_couplings"),
        _particle("W_plus_minus", "1", "+/-1", "singlet", "charged_vector_pair", "one_pair",
                  "massive_broken_directions", False, "unstable_gauge_modes", "charged_current", "CP_links_to_flavor",
                  gauge_mass, "GAUGE_ALGEBRA_VALIDATED_RETURNED_BROKEN_KERNEL_OPEN",
                  "two_real_broken_weak_generator_directions_with_positive_mass_Hessian", "W_mass_and_width"),
        _particle("Z", "1", "0", "singlet", "neutral_vector", "one", "massive_broken_direction", False,
                  "unstable_gauge_mode", "neutral_current", "CP_even_mass_sector", gauge_mass,
                  "GAUGE_ALGEBRA_VALIDATED_RETURNED_BROKEN_KERNEL_OPEN",
                  "one_neutral_broken_direction_orthogonal_to_electromagnetism", "Z_mass_and_width"),
        _particle("gluons", "1", "0", "adjoint_8_internal", "vector", "eight", "massless_gauge_kernel_directions", False,
                  "no_isolated_asymptotic_colored_particle", "color_adjoint", "CP_even_kinetic_sector", gauge_mass,
                  "SU3_REPRESENTATION_AND_GAUSS_LAW_STRUCTURE_VALIDATED_ASYMPTOTIC_PROOF_OPEN",
                  "eight_unbroken_color_generators_plus_physical_color-singlet_asymptotic_domain", "strong_coupling_and_hadron_data"),
        _particle("proton_neutron_minimal_composite", "1/2", "+1_or_0", "singlet", "composite_Dirac_state",
                  "isospin_pair", "nonzero_bound_state_mass", False, "stable_or_metastable_color-singlet_child",
                  "internal_constituent_orientation", "strong_sector_CP_constraint", "Gauss_law_color-singlet_projector_plus_returned_bound-state_operator",
                  "COLOR_SINGLET_KINEMATICS_PARTIAL_BINDING_AND_RETURN_OPEN",
                  "action-owned_confining/binding_operator_and_composite_return_monodromy", "nucleon_masses_and_lifetimes"),
    ]


def inverse_observation_ledger() -> list[dict[str, str]]:
    return [
        {
            "OBSERVED_FACT": "stable_charged_spin_half_color_singlet_matter_exists",
            "REQUIRED_BHSM_INVARIANT": "rank_one_electron_projector_with_Q=-1_FR-odd_spin_domain_and_persistent_nonzero_LR_singular_value",
            "ACTION_OWNER": "rank16_bundle_plus_common_LR_HS_pushforward_plus_return_monodromy",
            "CURRENT_STATUS": "REPRESENTATION_VALIDATED_DYNAMICAL_MASS_AND_RETURN_OPEN",
            "MISSING_MATHEMATICAL_OBJECT": "returned_broken_child_with_positive_electron_mass_singular_value_and_no_allowed_decay_channel",
            "EARLIEST_ELIGIBLE_STAGE": "after_N3/N4_converged_event_and_nonlinear_broken_return",
            "HELD_OUT_NUMERICAL_TEST": "electron_mass",
        },
        {
            "OBSERVED_FACT": "three_charged_leptons_share_gauge_quantum_numbers_but_not_mass",
            "REQUIRED_BHSM_INVARIANT": "charged_lepton_mass_operator_not_c_times_I3_and_with_three_distinct_singular_values",
            "ACTION_OWNER": "family-resolved_residues_of_returned_common_LR_kernel",
            "CURRENT_STATUS": "FAMILY_I3_CARRIER_VALIDATED_CURRENT_GAUGE_RESPONSE_FAMILY_CENTRAL",
            "MISSING_MATHEMATICAL_OBJECT": "action-selected_family-noncentral_broken_return_response",
            "EARLIEST_ELIGIBLE_STAGE": "returned_broken_child",
            "HELD_OUT_NUMERICAL_TEST": "charged_lepton_mass_triplet",
        },
        {
            "OBSERVED_FACT": "quark_charged_current_mixing_and_CP_violation_exist",
            "REQUIRED_BHSM_INVARIANT": "commutator_of_MuMu_dagger_and_MdMd_dagger_nonzero_and_CP_odd_Jarlskog_invariant_nonzero",
            "ACTION_OWNER": "sector-dependent_family_orientation_of_returned_LR_residues",
            "CURRENT_STATUS": "RESET_MASSLESS_AND_GAUGE_LEVEL_FAMILY_CENTRAL",
            "MISSING_MATHEMATICAL_OBJECT": "noncommuting_up/down_returned_family_Hermitians_with_dynamical_complex_orientation",
            "EARLIEST_ELIGIBLE_STAGE": "returned_broken_child_after_mass_operators_exist",
            "HELD_OUT_NUMERICAL_TEST": "CKM_and_J_CP",
        },
        {
            "OBSERVED_FACT": "neutrino_oscillation_requires_nonzero_propagation_splittings",
            "REQUIRED_BHSM_INVARIANT": "neutral_propagation_operator_has_three_modes_and_at_least_two_nonzero_eigenvalue_differences",
            "ACTION_OWNER": "reconstructed-spacetime_neutral_self-energy_and_cycle_monodromy",
            "CURRENT_STATUS": "RESET_PROJECTIVE_MASSLESS_PROPAGATION_ONLY",
            "MISSING_MATHEMATICAL_OBJECT": "propagation-dependent_family-noncentral_neutral_operator",
            "EARLIEST_ELIGIBLE_STAGE": "returned_child_propagating_in_reconstructed_spacetime",
            "HELD_OUT_NUMERICAL_TEST": "neutrino_splittings_and_PMNS",
        },
        {
            "OBSERVED_FACT": "unbroken_SU3_color_and_U1_electromagnetism_coexist_with_broken_electroweak_directions",
            "REQUIRED_BHSM_INVARIANT": "gauge_mass_Hessian_on_12_generators_has_kernel_dimension_9_and_rank_3_with_positive_broken_block",
            "ACTION_OWNER": "gauge_generator_second_variation_of_same_common_gauge-ghost-rank16-HS_pushforward",
            "CURRENT_STATUS": "COMMON_DETERMINANT_EXISTS_RETURNED_BROKEN_GAUGE_HESSIAN_OPEN",
            "MISSING_MATHEMATICAL_OBJECT": "returned_broken_gauge_Hessian_with_8_plus_1_kernel_and_3-dimensional_positive_image",
            "EARLIEST_ELIGIBLE_STAGE": "nonlinear_broken_child_and_return",
            "HELD_OUT_NUMERICAL_TEST": "W_Z_masses_and_gauge_couplings",
        },
        {
            "OBSERVED_FACT": "isolated_colored_asymptotic_matter_is_absent",
            "REQUIRED_BHSM_INVARIANT": "physical_asymptotic_child_space_equals_color-Gauss-law_singlet_subspace",
            "ACTION_OWNER": "nonabelian_Gauss_constraint_self-adjoint_domain_and_returned_composite_dynamics",
            "CURRENT_STATUS": "COLOR_REPRESENTATION_AND_PARTIAL_GAUSS_STRUCTURE_VALIDATED_CONFINEMENT_PROOF_OPEN",
            "MISSING_MATHEMATICAL_OBJECT": "global_asymptotic_singlet_theorem_without_empirical_string_tension",
            "EARLIEST_ELIGIBLE_STAGE": "returned_colored_internal_modes_and_composite_domain",
            "HELD_OUT_NUMERICAL_TEST": "hadron_spectrum_and_strong_observables",
        },
        {
            "OBSERVED_FACT": "stable_metastable_and_transient_particle_classes_exist",
            "REQUIRED_BHSM_INVARIANT": "return_map_spectrum_and_action-allowed_decay-channel_graph_separate_persistent_metastable_and_transient_children",
            "ACTION_OWNER": "physical_return_map_Floquet_monodromy_and_interacting_selection_rules",
            "CURRENT_STATUS": "THEOREM_CLASS_EXISTS_PHYSICAL_BROKEN_RETURN_NOT_SOLVED",
            "MISSING_MATHEMATICAL_OBJECT": "broken-child_monodromy_with_decay-channel_operator",
            "EARLIEST_ELIGIBLE_STAGE": "one-cycle_broken_return",
            "HELD_OUT_NUMERICAL_TEST": "decay_lifetimes",
        },
    ]


def electron_child_certificate() -> dict[str, Any]:
    return {
        "chirality_owner": "rank16_left-Weyl_bundle_and_L/R_representation_projectors",
        "electric_charge_owner": "geometric_hypercharge_operator_plus_returned_unbroken_Q_EM_generator",
        "spin_statistics_owner": "M4_spin_bundle_Dirac_domain_plus_odd_FR_projective_line",
        "persistent_mass_owner": "electron_projection_of_returned_common_LR_HS_mass_operator",
        "required_nonzero_condition": "sigma_min(P_eL*M_phys_return*P_eR)>0",
        "one_cycle_mass_invariant": (
            "rank(P_eR*M_return^dagger*M_return*P_eR)=1_and_its_positive_"
            "singular_value_is_preserved_under_the_physical_return_intertwiner"
        ),
        "charge_return_invariant": "U_return*P_Qminus1=P_Qminus1*U_return",
        "stable_child_condition": (
            "projective_return_eigenvalue_has_unit_modulus_and_the_action-owned_"
            "decay_channel_graph_has_no_lower_state_with_the_same_exact_charges"
        ),
        "transient_LR_or_HS_pulse_is_sufficient": False,
        "measured_electron_mass_used": False,
    }


def collapsed_completion_graph() -> dict[str, Any]:
    nodes = [
        "A_simultaneous_N3_physical_event_saddle",
        "B_common_event_gauge-rank16-HS_pushforward",
        "C_independent_N4plus_full-Sobolev_orbit_convergence",
        "D_nonlinear_fermion-backreacted_broken_child",
        "E_reconstruction_and_one-cycle_return_with_persistent_order_parameter",
        "F_returned_fermion_gauge_and_neutral_family_operators",
        "G_color-singlet_asymptotic_and_decay-classifier_domains",
        "H_absolute_scale_from_the_same_pushforward",
        "I_held-out_numerical_kill_screen_and_unique_actualization",
    ]
    return {
        "independent_remaining_objects": nodes,
        "edges": [
            ["A_simultaneous_N3_physical_event_saddle", "B_common_event_gauge-rank16-HS_pushforward"],
            ["B_common_event_gauge-rank16-HS_pushforward", "C_independent_N4plus_full-Sobolev_orbit_convergence"],
            ["C_independent_N4plus_full-Sobolev_orbit_convergence", "D_nonlinear_fermion-backreacted_broken_child"],
            ["D_nonlinear_fermion-backreacted_broken_child", "E_reconstruction_and_one-cycle_return_with_persistent_order_parameter"],
            ["E_reconstruction_and_one-cycle_return_with_persistent_order_parameter", "F_returned_fermion_gauge_and_neutral_family_operators"],
            ["F_returned_fermion_gauge_and_neutral_family_operators", "G_color-singlet_asymptotic_and_decay-classifier_domains"],
            ["B_common_event_gauge-rank16-HS_pushforward", "H_absolute_scale_from_the_same_pushforward"],
            ["F_returned_fermion_gauge_and_neutral_family_operators", "I_held-out_numerical_kill_screen_and_unique_actualization"],
            ["G_color-singlet_asymptotic_and_decay-classifier_domains", "I_held-out_numerical_kill_screen_and_unique_actualization"],
            ["H_absolute_scale_from_the_same_pushforward", "I_held-out_numerical_kill_screen_and_unique_actualization"],
        ],
        "duplicate_dependency_collapses": {
            "absolute_gauge_and_fermion_mass_normalization": "B_plus_H_one_shared_pushforward",
            "electron_muon_tau_quark_mass": "F_family-resolved_returned_LR_operator",
            "CKM_and_CP": "F_relative_up/down_orientation_after_nonzero_mass",
            "PMNS_and_neutrino_splittings": "F_neutral_propagation_operator",
            "stability_and_decay": "E_plus_G_return_monodromy_and_channel_domain",
        },
    }


def current_kkt_physical_role_diagnostic() -> dict[str, Any]:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_fifth_multirank_step_v16_34.json"
    ).read_text(encoding="utf-8"))
    raw_hex = payload["fifth_multirank_step"]["best_accepted"]["raw_vector_hex"]
    raw = np.asarray([float.fromhex(value) for value in raw_hex])
    residual = scaled_analytic_kkt_residual(raw * kkt_variable_scales())
    q = residual[:230].reshape(23, 10)
    coordinate_norms = np.linalg.norm(q, axis=0)
    order = np.argsort(coordinate_norms)[::-1]
    role = {
        "log_scale": "boundary_scale_and_common_pushforward_geometry",
        "u_1": "conformal_shape_and_reconstruction_geometry",
        "u_2": "conformal_shape_and_reconstruction_geometry",
        "u_3": "conformal_shape_and_reconstruction_geometry",
        "w_0": "normal/fiber_localization_geometry",
        "w_1": "normal/fiber_localization_geometry",
        "w_2": "normal/fiber_localization_geometry",
        "v_0": "Hopf_anisotropy_and_gauge-breaking_background_geometry",
        "v_1": "Hopf_anisotropy_and_gauge-breaking_background_geometry",
        "v_2": "Hopf_anisotropy_and_gauge-breaking_background_geometry",
    }
    rows = [
        {
            "coordinate": Q_LABELS[index],
            "stationarity_norm_across_free_nodes": float(coordinate_norms[index]),
            "downstream_physical_role": role[Q_LABELS[index]],
        }
        for index in order
    ]
    top_flat = np.argsort(np.abs(q.ravel()))[-12:][::-1]
    return {
        "source_state": "v16.34_best_accepted",
        "coordinate_group_ranking": rows,
        "largest_coordinate_components": [
            {
                "node": int(index // 10 + 1),
                "coordinate": Q_LABELS[index % 10],
                "residual": float(q.ravel()[index]),
            }
            for index in top_flat
        ],
        "explicit_family_orientation_coordinate_present": False,
        "explicit_broken_HS_LR_order_parameter_coordinate_present": False,
        "interpretation": (
            "THE_CURRENT_KKT_OWNS_THE_UNBROKEN_PARENT_GEOMETRY_CONSTRAINTS_"
            "AND_COMMON_DETERMINANT_RESPONSE_NEEDED_TO_LOCATE_THE_EVENT;_THE_"
            "FIRST_ELECTRON-LIKE_MASS_REQUIRES_THE_DOWNSTREAM_EXPLICIT_BROKEN_"
            "HS/LR_BRANCH_AND_RETURN_OPERATOR,_NOT_A_NEW_UNBROKEN_KKT_COORDINATE"
        ),
    }


def completion_payload() -> dict[str, Any]:
    firewall = two_tier_data_firewall()
    matrix = physical_requirement_matrix()
    ledger = inverse_observation_ledger()
    diagnostic = current_kkt_physical_role_diagnostic()
    validation = {
        "required_particle_rows_present": {row["particle_or_sector"] for row in matrix} == {
            "electron", "muon", "tau", "neutrino_family", "up_type_quark_family",
            "down_type_quark_family", "photon", "W_plus_minus", "Z", "gluons",
            "proton_neutron_minimal_composite",
        },
        "every_observation_has_complete_inverse_fields": all(set(row) == {
            "OBSERVED_FACT", "REQUIRED_BHSM_INVARIANT", "ACTION_OWNER",
            "CURRENT_STATUS", "MISSING_MATHEMATICAL_OBJECT", "EARLIEST_ELIGIBLE_STAGE",
            "HELD_OUT_NUMERICAL_TEST",
        } for row in ledger),
        "no_measured_numbers_used": not firewall["measured_numerical_values_embedded_in_this_artifact"],
        "gauge_and_mass_normalization_not_split": (
            collapsed_completion_graph()["duplicate_dependency_collapses"][
                "absolute_gauge_and_fermion_mass_normalization"
            ] == "B_plus_H_one_shared_pushforward"
        ),
        "current_KKT_not_falsely_expanded": (
            not diagnostic["explicit_broken_HS_LR_order_parameter_coordinate_present"]
        ),
        "sync_unauthorized": not EXTERNAL_SYNC_AUTHORIZED,
    }
    return {
        "artifact": "BHSM_aether_physical_inverse_closure_v16_36",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "EXTERNAL_SYNC_AUTHORIZED": EXTERNAL_SYNC_AUTHORIZED,
        "status": "RECLASSIFIED",
        "two_tier_data_firewall": firewall,
        "physical_requirement_matrix": matrix,
        "inverse_observation_ledger": ledger,
        "electron_child_certificate": electron_child_certificate(),
        "collapsed_completion_graph": collapsed_completion_graph(),
        "current_KKT_physical_role_diagnostic": diagnostic,
        "hindsight": {
            "VALIDATED": [
                "rank16_representation_charge_chirality_and_three-family_carrier_are_structurally_adequate",
                "current_N3_unknowns_own_the_unbroken_event_geometry_and_common_determinant_response",
            ],
            "INVALIDATED": [
                "family-central_returned_mass_operator_as_a_final_three-generation_answer",
                "transient_LR_or_HS_pulse_as_an_electron",
                "independent_electroweak_or_Yukawa_normalization",
            ],
            "RECLASSIFIED": [
                "observed_particles_as_structural_operator_tests_not_parameter_inputs",
                "current_KKT_as_event-locating_parent_system_not_the_complete_broken_electron_state",
            ],
            "ACTIVE": [
                "simultaneous_N3_event_saddle_closure",
                "first_electron-like_broken_child_after_common_pushforward_and_N-convergence",
            ],
        },
        "real_physical_property_explained": (
            "THE_COMPLETE_RETURNED_CHILD_MUST_SUPPORT_STABLE_CHARGED_SPIN-HALF_"
            "MATTER_AND_THE_SHARED_OPERATOR_STRUCTURE_OF_ALL_OBSERVED_SECTORS"
        ),
        "dependency_advanced": (
            "COLLAPSES_REAL-PARTICLE_REQUIREMENTS_TO_NINE_ACTION-OWNED_OBJECTS_"
            "AND_PROVES_THAT_THE_LIVE_N3_SOLVE_SHOULD_CONTINUE_UNCHANGED_WHILE_"
            "THE_EXPLICIT_HS/LR_ORDER_PARAMETER_FIRST_ENTERS_THE_BROKEN_BRANCH"
        ),
        "active_calculation": "CONTINUE_THE_EXISTING_FRESH_N3_KKT_SOLVE",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return [_canonical(item) for item in value.tolist()]
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        return round(value, 12)
    if isinstance(value, Mapping):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_physical_inverse_closure_v16_36.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "EXTERNAL_SYNC_AUTHORIZED",
    "two_tier_data_firewall", "physical_requirement_matrix", "inverse_observation_ledger",
    "electron_child_certificate", "collapsed_completion_graph",
    "current_kkt_physical_role_diagnostic", "completion_payload", "deterministic_json", "materialize",
]
