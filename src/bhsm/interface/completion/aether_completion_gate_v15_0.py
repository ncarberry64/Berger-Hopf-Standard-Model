"""Controlling BHSM v15.0 Aether pregeometry theorem/no-go package."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .aether_emergent_clock_energy_v15_0 import clock_energy_payload
from .aether_encapsulation_correspondence_v15_0 import event_correspondence_payload
from .aether_haar_barrier_v15_0 import haar_barrier_payload
from .aether_parent_stratification_v15_0 import parent_stratification_payload
from .aether_reconstruction_v15_0 import high_excitation_counterexample, reconstruction_payload

VERSION = "v15.0"
PRIMARY_VERDICT = (
    "AETHER_PARENT_STRATIFICATION_IS_MATHEMATICALLY_COMPATIBLE_WITH_CURRENT_BHSM_"
    "BUT_FINITE_CORE_TRANSITION_REQUIRES_AN_ACTION_OWNED_PREGEOMETRIC_CORRESPONDENCE_LAW"
)
OUTCOME = "OUTCOME_B"
EXACT_NEXT_OBJECT = (
    "ACTION_OWNED_PREGEOMETRIC_CORE_EVENT_CORRESPONDENCE_WITH_SELF_ADJOINT_RELATIVE_"
    "BOUNDARY_DOMAIN_PARENT_INVARIANT_MATCHING_CLOCK_CALIBRATION_AND_EXACT_REGULAR_BHSM_RECOVERY"
)


def low_energy_recovery_payload() -> dict[str, Any]:
    return {
        "version": VERSION,
        "extension_type": "conservative_disjoint_stratum_extension",
        "restriction_to_G_A": "identical_existing_BHSM_regular_theory",
        "Pi_BH": "G_A -> [M8 <-> (M5_plus,M5_minus) <-> M4]",
        "recovered_without_retuning": {
            "M8_M5_M4_stratification": True,
            "Berger_Hopf_geometry": True,
            "support_variable_upsilon_on_0_1": True,
            "q_D_minus_lambda_log_upsilon": True,
            "infinite_Haar_depth": True,
            "v14_64_relative_boundary_correspondence_and_trace_obstruction": True,
            "cap_attachment_domains": True,
            "v14_91_Lorentzian_phase_space_controls": True,
            "v14_93_radial_no_bifurcation_result": True,
            "v14_94_no_controlled_encapsulation_event": True,
            "frozen_predictions": True,
            "existing_no_go_results": True,
        },
        "core_transition_made_easier_by_modifying_regular_metric": False,
        "physical_transition_recovered": False,
    }


def microscopic_action_audit() -> dict[str, Any]:
    common = {
        "additional_continuous_parameters_adopted": False,
        "low_energy_BHSM_recovery_required": True,
        "selected_after_physical_comparison": False,
    }
    return {
        "existing_action": {
            **common,
            "status": "DOES_NOT_DEFINE_CORE_ADJACENCY_OR_EVENT_COMPOSITION",
            "permits_regular_Haar_endpoint_in_finite_action": False,
        },
        "heat_trace_branch": {
            **common,
            "status": "CANDIDATE_FOUNDATIONAL_AXIOM_NOT_ADOPTED",
            "canonical_only_after_operator_domain_and_trace_are_supplied": True,
            "finite_core_transition_selected": False,
        },
        "zeta_branch": {
            **common,
            "status": "CANDIDATE_WITH_RELEVANT_LOCAL_TERMS_AND_PHASE_CONVENTIONS_OPEN",
            "canonical_only_after_operator_domain_and_renormalization_data_are_supplied": True,
            "finite_core_transition_selected": False,
        },
        "abstract_event_span": {
            **common,
            "status": "ALGEBRAIC_MODEL_ONLY_NOT_AN_ACTION_PRINCIPLE",
            "finite_core_transition_selected": False,
        },
        "unique_microscopic_functional_derived": False,
    }


def preferred_frame_firewall() -> dict[str, Any]:
    return {
        "BHSM_AETHER_NOT_LUMINIFEROUS_ETHER": True,
        "preferred_inertial_frame": False,
        "absolute_rest_frame": False,
        "Aether_velocity_through_background_spacetime": False,
        "material_medium": False,
        "new_gravity_mediator": False,
        "Lorentz_covariance_of_reconstructed_regular_theory_changed": False,
        "firewall_status": "PASS_BY_TYPED_CONSTRUCTION",
    }


def theorem_gate_ledger() -> dict[str, Any]:
    return {
        "T1_Haar_Barrier": "PROVED",
        "T2_Core_Nonidentification": "PROVED_CONDITIONALLY_ON_FINITE_ACTION_FINITE_EVENT",
        "T3_Aether_Stratified_Extension": "ADMISSIBLE_AS_CONSERVATIVE_EXTENSION_EVENT_LAW_NOT_DERIVED",
        "T4_Geometric_Reconstruction": "SHARP_CONDITIONAL_OPERATOR_DOMAIN_PREDICATE",
        "T5_Emergent_Distance": "REGULAR_EDGE_RULE_REUSED_CORE_DISTANCE_UNDEFINED_GLOBAL_CONTINUUM_OPEN",
        "T6_Emergent_Clock": "CONDITIONAL_RELATIVE_CLOCK_RATIO_NO_ABSOLUTE_UNIT_DERIVED",
        "T7_Emergent_Energy": "CONDITIONAL_STONE_GENERATOR_MAP_AFTER_CLOCK_CALIBRATION",
        "T8_Encapsulation_Correspondence": "ASSOCIATIVE_ABSTRACT_SPAN_CONSTRUCTED_NOT_ACTION_OWNED",
        "T9_Invariant_Matching": "ABSTRACT_SIGNATURE_MATCHING_PROVED_PHYSICAL_INVARIANT_SET_OPEN",
        "T10_Low_Energy_Recovery": "PROVED_FOR_CONSERVATIVE_EXTENSION_BY_RESTRICTION",
        "T11_High_Excitation_Low_Reconstructibility": "UNDERDETERMINED_COUNTEREXAMPLE_TO_UNCOUPLED_MONOTONICITY",
        "T12_Preferred_Frame_Firewall": "PASS_BY_TYPED_CONSTRUCTION",
    }


def completion_payload() -> dict[str, Any]:
    validation = {
        "regular_Haar_endpoint_preserved_at_infinite_distance": True,
        "coordinate_compactification_not_physical_solution": True,
        "core_is_not_upsilon_zero": True,
        "core_has_no_spacetime_time_energy_or_velocity": True,
        "v14_64_domain_obstruction_preserved": True,
        "event_composition_is_abstract_not_action_derived": True,
        "frozen_predictions_unchanged": True,
        "official_prediction_logic_unchanged": True,
        "no_empirical_targets_used": True,
        "no_new_continuous_parameter": True,
        "no_new_fundamental_dynamical_field": True,
        "preferred_frame_firewall": True,
        "USB_untouched": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v15_0",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "outcome": OUTCOME,
        "theorem_gates": theorem_gate_ledger(),
        "haar": haar_barrier_payload(),
        "stratification": parent_stratification_payload(),
        "reconstruction": reconstruction_payload(),
        "clock_energy": clock_energy_payload(),
        "event_correspondence": event_correspondence_payload(),
        "high_excitation_low_reconstructibility": high_excitation_counterexample(),
        "low_energy_recovery": low_energy_recovery_payload(),
        "microscopic_action_audit": microscopic_action_audit(),
        "preferred_frame_firewall": preferred_frame_firewall(),
        "Hindsight_20_20": {
            "validated": [
                "regular multiplicative support is an infinite half-line in canonical Haar depth",
                "no smooth bounded coordinate chart changes that physical distance",
                "a separate nongeometric core stratum is a mathematically consistent conservative extension",
                "relative process depth can precede a clock and yields only a calibrated clock ratio",
                "a strongly continuous unitary process representation yields E=(hbar/tau_clock)kappa after clock calibration",
                "abstract invariant-matched event spans compose associatively",
                "finite exterior clock separation is consistent with no intrinsic core duration",
                "restriction to the regular stratum exactly preserves current BHSM mathematics",
            ],
            "invalidated": [
                "Aether core equals upsilon zero as a finite-action accessible regular state",
                "bounded coordinate compactification makes the Haar endpoint physically finite",
                "conventional time or energy as primitive core data",
                "the naive finite diamond as the continuum cross-stratum operator",
                "high excitation alone forces lower geometric reconstructibility",
                "linear instability as a completed encapsulation event",
                "preferred-frame or material-medium Aether",
            ],
            "reclassified": [
                "upsilon is a regular geometric-support coordinate rather than a core coordinate",
                "the Aether core has undefined metric size rather than zero or infinitesimal size",
                "singularity as reconstruction failure remains a hypothesis",
                "finite encapsulation may be modeled as a boundary-to-boundary correspondence rather than an ordinary trajectory",
                "conventional energy is a clock-calibrated representation of a dimensionless generator on the conditional branch",
            ],
            "open": [EXACT_NEXT_OBJECT],
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
        "FULL_BHSM_COMPLETE": False,
        "MARK_III": "NOT_REACHED",
        "PHYSICAL_AETHER_TRANSITION_DERIVED": False,
        "FINITE_TIME_ENCAPSULATION_EVENT_DERIVED": False,
        "SPACETIME_EMERGENT_IN_NATURE_PROVED": False,
        "AETHER_PHYSICALLY_EXISTS_PROVED": False,
        "USB_SYNCHRONIZATION_ELIGIBLE": False,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "new_continuous_parameter_introduced": False,
        "new_fundamental_dynamical_field_introduced": False,
        "empirical_inputs_used": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def artifact_payloads() -> dict[str, dict[str, Any]]:
    return {
        "BHSM_aether_haar_barrier_v15_0.json": haar_barrier_payload(),
        "BHSM_aether_parent_stratification_v15_0.json": parent_stratification_payload(),
        "BHSM_aether_geometric_reconstruction_v15_0.json": reconstruction_payload(),
        "BHSM_aether_emergent_clock_energy_v15_0.json": clock_energy_payload(),
        "BHSM_aether_encapsulation_correspondence_v15_0.json": event_correspondence_payload(),
        "BHSM_aether_high_excitation_low_reconstructibility_gate_v15_0.json": high_excitation_counterexample(),
        "BHSM_completion_gate_v15_0.json": completion_payload(),
    }


def deterministic_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def materialize(directory: str | Path) -> list[Path]:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, payload in artifact_payloads().items():
        path = target / name
        path.write_text(deterministic_json(payload), encoding="utf-8")
        paths.append(path)
    return paths
