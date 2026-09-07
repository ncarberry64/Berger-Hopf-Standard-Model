"""Current-C2 fermion Hadamard-state existence and selection boundary.

The AE3.1 charged-lepton Dirac operator is already assembled on every
certified finite-core globally hyperbolic C2 member.  Standard Dirac-field
theory therefore supplies a nonempty Hadamard state class member by member.
This module records the stronger existence result and proves that none of the
retained BHSM structures selects one covariance from that class.
"""

from __future__ import annotations

from typing import Any


ACTION_VERSION = "BHSM-AE-3.1.0"
CLASSIFICATION = "CURRENT_C2_FERMION_HADAMARD_STATE_CLASS"
EXTERNAL_THEOREM_REFERENCES = (
    (
        "S_HOLLANDS_ADIABATIC_HADAMARD_STATES_FOR_DIRAC_QUANTUM_FIELDS_"
        "ON_CURVED_SPACE_ARXIV_GR_QC_9901069_THEOREM_VI_1"
    ),
    (
        "C_GERARD_AND_T_STOSKOPF_HADAMARD_STATES_FOR_QUANTIZED_DIRAC_"
        "FIELDS_ARXIV_2108_11630"
    ),
)


def hadamard_class_existence_theorem() -> dict[str, Any]:
    """State the familywise existence theorem at the current claim boundary."""

    return {
        "action_version": ACTION_VERSION,
        "background_class": (
            "EACH_CERTIFIED_FINITE_CORE_CURRENT_C2_OPEN_DEVELOPMENT_"
            "WITH_TOPOLOGY_I_tau_TIMES_S3"
        ),
        "globally_hyperbolic_member_by_member": True,
        "Cauchy_surfaces": "tau=constant_IS_DIFFEO_TO_S3",
        "operator": "D_l,C2=[[D_L,M_l],[M_l_dagger,D_R]]",
        "operator_type": "DIRAC_TYPE_WITH_SMOOTH_BOUNDED_ZERO_ORDER_MASS",
        "external_existence_theorems": EXTERNAL_THEOREM_REFERENCES,
        "advanced_retarded_Green_existence_inherited": True,
        "CAR_algebra_defined_from_causal_propagator": True,
        "quasifree_Hadamard_state_class_nonempty_member_by_member": True,
        "Hadamard_two_point_wavefront_condition": (
            "WF(omega_2)_HAS_THE_STANDARD_FUTURE_DIRECTED_NULL_"
            "BICHARACTERISTIC_POLARIZATION"
        ),
        "state_dependent_Feynman_two_point_distribution_exists": True,
        "Feynman_distribution_for_state": (
            "TIME_ORDERED_DISTRIBUTION_BUILT_FROM_omega_2_AND_THE_"
            "ACTION_OWNED_CAUSAL_SPLITTING"
        ),
        "any_two_Hadamard_two_point_functions_differ_by": (
            "A_SMOOTH_BISOLUTION_OF_THE_DIRAC_EQUATION"
        ),
        "local_Hadamard_singularity_class_is_state_independent": True,
        "smooth_state_dependent_part_is_fixed_by_action": False,
        "one_Hadamard_state_selected": False,
        "one_physical_C2_history_member_selected": False,
        "maximal_C2_continuation_certified": False,
        "global_stationarity_or_asymptotic_stationarity_derived": False,
        "global_frequency_poles_defined": False,
    }


def cauchy_covariance_selection_contract() -> dict[str, Any]:
    """Identify the exact datum needed to choose a quasifree fermion state."""

    return {
        "Cauchy_data_space": (
            "COMPLETION_OF_SMOOTH_COMPACT_SPINOR_DATA_ON_S3_IN_THE_"
            "ACTION_OWNED_DIRAC_INNER_PRODUCT"
        ),
        "causal_evolution_owned_by_action": True,
        "CAR_pairing_owned_by_action": True,
        "quasifree_state_datum": (
            "A_SELF_DUAL_CAR_CAUCHY_COVARIANCE_C_WITH_0_LE_C_LE_I_"
            "AND_C_PLUS_GAMMA_C_GAMMA=I"
        ),
        "self_dual_CAR_reality_constraint": "C+Gamma*C*Gamma=I",
        "pure_state_specialization": "C_SQUARED=C",
        "Hadamard_requirement": (
            "C_HAS_THE_POSITIVE_FREQUENCY_PRINCIPAL_SYMBOL_MODULO_"
            "SMOOTHING_TERMS"
        ),
        "action_and_domain_determine_principal_singularity": True,
        "action_and_domain_determine_smoothing_part": False,
        "reset_compatibility_required": "C_child=U_R*C_event*U_R_dagger",
        "family_projector_compatibility_required": True,
        "state_covariance_present_in_current_action": False,
        "new_continuous_temperature_or_Bogoliubov_coefficient_inserted": False,
        "exact_missing_object": (
            "ONE_ACTION_SELECTED_CURRENT_C2_CAUCHY_COVARIANCE_OR_"
            "EQUIVALENT_COMPLEX_STRUCTURE_COMPATIBLE_WITH_AE2_RESET_"
            "AND_CURRENT_C2_EVOLUTION__OR_A_MAXIMAL_ASYMPTOTIC_"
            "STATIONARITY_THEOREM_THAT_SELECTS_IT"
        ),
    }


def retained_state_selector_audit() -> dict[str, Any]:
    """Classify retained structures that could be mistaken for a state."""

    rows = [
        {
            "candidate": "AE2_RESET_LIFT",
            "owned_result": "SPIN_GAUGE_TRACE_DOMAIN_AND_CAUSAL_GLUING",
            "missing": "POSITIVE_FREQUENCY_COVARIANCE_ON_ONE_CAUCHY_SURFACE",
            "selects_state": False,
        },
        {
            "candidate": "CURRENT_C2_TIME_ORIENTATION",
            "owned_result": "FUTURE_CAUSAL_SUPPORT_AND_ADVANCED_RETARDED_LABELS",
            "missing": "COMPLEX_STRUCTURE_OR_SPECTRAL_POSITIVITY_SPLITTING",
            "selects_state": False,
        },
        {
            "candidate": "HADAMARD_MICROLOCAL_CONDITION",
            "owned_result": "UNIVERSAL_SHORT_DISTANCE_SINGULARITY_CLASS",
            "missing": "SMOOTH_BISOLUTION_PART_OF_THE_TWO_POINT_FUNCTION",
            "selects_state": False,
        },
        {
            "candidate": "INSTANTANEOUS_HAMILTONIAN_DIAGONALIZATION",
            "owned_result": "NONE_ON_A_SELECTED_PHYSICAL_SLICE",
            "missing": "ACTION_SELECTED_SLICE_AND_TIME_DEPENDENT_COMPLEX_STRUCTURE",
            "selects_state": False,
        },
        {
            "candidate": "FINITE_ORDER_ADIABATIC_VACUUM",
            "owned_result": "NONE",
            "missing": "ADIABATIC_ORDER_REFERENCE_SLICE_AND_SMOOTH_COMPLETION",
            "selects_state": False,
        },
        {
            "candidate": "KMS_OR_THERMAL_STATE",
            "owned_result": "NONE",
            "missing": "STATIONARY_TIME_FLOW_AND_ACTION_OWNED_INVERSE_TEMPERATURE",
            "selects_state": False,
        },
        {
            "candidate": "EUCLIDEAN_CAP_OR_REFLECTION_POSITIVITY",
            "owned_result": "NONE_ON_CURRENT_C2",
            "missing": "ACTION_SELECTED_EUCLIDEAN_CONTINUATION_AND_CAP_DOMAIN",
            "selects_state": False,
        },
        {
            "candidate": "IN_OUT_ASYMPTOTIC_VACUUM",
            "owned_result": "NONE",
            "missing": "MAXIMAL_CONTINUATION_WITH_ASYMPTOTIC_STATIONARITY",
            "selects_state": False,
        },
        {
            "candidate": "PROPER_HISTORY_RESOLVENT_PARAMETER_z",
            "owned_result": "A_NONLORENTZIAN_PRODUCT_DIRAC_RESOLVENT_COORDINATE",
            "missing": "IDENTIFICATION_WITH_PHYSICAL_p_SQUARED_AND_STATE_DATA",
            "selects_state": False,
        },
    ]
    return {
        "rows": rows,
        "candidate_count": len(rows),
        "selected_candidate_count": sum(row["selects_state"] for row in rows),
        "retained_action_selects_unique_Feynman_state": False,
        "arbitrary_vacuum_choice_forbidden": True,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "FINITE_CORE_CURRENT_C2_HADAMARD_STATE_CLASS_NONEMPTY_FAMILYWISE": True,
        "STATE_DEPENDENT_FEYNMAN_TWO_POINT_DISTRIBUTION_EXISTS_FAMILYWISE": True,
        "LOCAL_HADAMARD_SINGULARITY_CLASS_DERIVED": True,
        "CURRENT_C2_ACTION_SELECTED_HADAMARD_STATE_DERIVED": False,
        "CURRENT_C2_ACTION_OWNED_FEYNMAN_TWO_POINT_FUNCTION_DERIVED": False,
        "CURRENT_C2_GLOBAL_FREQUENCY_DIAGONALIZATION_DERIVED": False,
        "CURRENT_C2_DRESSED_CHARGED_LEPTON_POLES_DERIVED": False,
        "CURRENT_C2_PHYSICAL_MUON_POLE_DERIVED": False,
        "MUON_MAGNETIC_MOMENT_DERIVED": False,
        "new_state_parameter_inserted": False,
        "particle_spectrum_rebuilt": False,
        "exact_next_operator": (
            "ACTION_SELECTED_CURRENT_C2_CAUCHY_COVARIANCE_OR_COMPLEX_"
            "STRUCTURE_COMPATIBLE_WITH_AE2_RESET_AND_CURRENT_C2_"
            "EVOLUTION__OR_MAXIMAL_ASYMPTOTIC_STATIONARITY"
        ),
        "FULL_BHSM_COMPLETE": False,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "EXTERNAL_THEOREM_REFERENCES",
    "cauchy_covariance_selection_contract",
    "claim_boundary",
    "hadamard_class_existence_theorem",
    "retained_state_selector_audit",
]
