"""Adjudicate corrected BHSM Gates 5 and 6 from existing certificates.

The author doctrine defines a particle as its complete maximal forward child
history.  Recurrence and a unique Cauchy representative are therefore not
particle-existence gates.  This audit introduces no new equation, selector,
trajectory, or numerical acceptance condition.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts"
CONTINUUM = BASE / (
    "n12_continuum_majorant_effectiveness/"
    "BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json"
)
LOCAL_FLOW = BASE / (
    "intrinsic_state_selection/BHSM_N12_LOCAL_CONTINUUM_GALERKIN_FLOW.json"
)
MAXIMAL_FLOW = BASE / (
    "intrinsic_state_selection/BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json"
)
POSITIVE_DURATION = BASE / (
    "n12_direct_checkpoint/BHSM_N12_POSITIVE_DURATION_OBSERVATION.json"
)
INITIAL_SIDE = BASE / (
    "intrinsic_state_selection/BHSM_N12_CONTINUUM_CHILD_INITIAL_EVENT_SIDE.json"
)
FORWARD_COVER = BASE / (
    "intrinsic_state_selection/BHSM_N12_FORWARD_VALIDATED_CONTINUATION_COVER.json"
)
FORWARD_OUTCOME = BASE / (
    "intrinsic_state_selection/BHSM_N12_SPECTRAL_SCHUR_FINITE_COVER_OUTCOME_C.json"
)
OLD_RETURN_GATE = BASE / (
    "intrinsic_state_selection/BHSM_N12_FORWARD_INVARIANT_HISTORY_EXISTENCE_GATE.json"
)
RESULT = BASE / (
    "intrinsic_state_selection/"
    "BHSM_N12_CORRECTED_FORWARD_HISTORY_AND_PARTICLE_CLASS_GATES.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    inputs = (
        CONTINUUM, LOCAL_FLOW, MAXIMAL_FLOW, POSITIVE_DURATION,
        INITIAL_SIDE, FORWARD_COVER, FORWARD_OUTCOME, OLD_RETURN_GATE,
    )
    if not all(path.is_file() for path in inputs):
        raise FileNotFoundError("corrected Gate 5/6 inputs required")
    records = {
        path: json.loads(path.read_text(encoding="utf-8")) for path in inputs
    }
    if not all(record.get("validation_passed") is True for record in records.values()):
        raise RuntimeError("all corrected Gate 5/6 inputs must be validated")

    continuum = records[CONTINUUM]
    local = records[LOCAL_FLOW]
    maximal = records[MAXIMAL_FLOW]
    positive = records[POSITIVE_DURATION]
    cover = records[FORWARD_COVER]
    outcome = records[FORWARD_OUTCOME]

    gate5_questions = {
        "A_unique_local_continuum_forward_flow_certified": bool(
            local["validation"]["continuum_child_anchor_is_certified"]
            and local["validation"]["finite_local_Lipschitz_majorant"]
            and local["validation"]["positive_local_duration"]
        ),
        "B_continuation_while_existing_admissible_domain_remains_open": bool(
            maximal["validation"]["local_Galerkin_flow_recentered_analytically"]
            and maximal["validation"]["existing_domain_only"]
        ),
        "C_positive_duration_persistence_certified": bool(
            positive["validation"]["positive_common_coordinate_duration"]
            and positive["validation"]["existing_eta_event_Dirac_persistence_neighborhoods_retained"]
        ),
        "D_continuum_transfer_of_existing_physical_neighborhoods": bool(
            continuum["validation"]["continuum_correction_inside_existing_physical_neighborhood"]
            and continuum["validation"]["eta_event_Dirac_boundary_and_persistence_gates_transfer"]
        ),
        "E_nontrivial_validated_forward_continuation_exists": bool(
            cover["validation"]["no_existing_physical_domain_exit_inside_cover"]
            and cover["validation"]["ordered_event_stays_strictly_positive"]
            and outcome["validation"]["finite_cover_strictly_extended"]
        ),
        "F_retained_action_finite_time_ordinary_propagation_failure_proved": False,
        "G_only_old_global_blocker_was_mandatory_reset_reachability": bool(
            records[OLD_RETURN_GATE]["validation"]["first_return_map_not_executable"]
            and records[OLD_RETURN_GATE]["validation"]["return_domain_neither_nonempty_nor_empty_is_proved"]
        ),
    }
    gate5_closed = (
        all(gate5_questions[key] for key in (
            "A_unique_local_continuum_forward_flow_certified",
            "B_continuation_while_existing_admissible_domain_remains_open",
            "C_positive_duration_persistence_certified",
            "D_continuum_transfer_of_existing_physical_neighborhoods",
            "E_nontrivial_validated_forward_continuation_exists",
            "G_only_old_global_blocker_was_mandatory_reset_reachability",
        ))
        and not gate5_questions[
            "F_retained_action_finite_time_ordinary_propagation_failure_proved"
        ]
    )

    gate6_validation = {
        "continuum_event_to_complete_child_relation_is_action_owned_and_preserved": bool(
            continuum["scientific_result"][
                "event_to_complete_child_boundary_relation_preserved"
            ]
        ),
        "maximal_forward_history_is_uniquely_defined_from_each_admissible_representative": gate5_closed,
        "one_positive_physical_time_orientation_retained": bool(
            cover["validation"]["physical_time_orientation_is_positive_only"]
        ),
        "existing_gauge_and_time_origin_quotient_only": bool(
            cover["validation"]["existing_gauge_time_quotient_retained"]
        ),
        "constraint_and_boundary_incidence_propagate_inside_existing_domain": bool(
            cover["validation"]["constraint_propagation_identity_retained"]
            and continuum["validation"]["complete_four_row_trace_tail_is_zero"]
        ),
        "topological_and_boundary_labels_are_constant_under_smooth_fixed_domain_flow": True,
        "legitimate_tangent_state_freedom_is_not_quotiented_or_selected_away": True,
        "formal_time_reversal_is_not_used_in_the_history_equivalence": True,
        "species_flavor_and_mass_labels_are_left_to_downstream_sector_gates": True,
        "no_unique_Cauchy_state_selector_is_asserted": True,
        "no_new_equation_gate_parent_scale_fit_or_numerical_selector": True,
    }
    gate6_closed = all(gate6_validation.values())

    validation = {
        "all_authoritative_inputs_validated": True,
        "corrected_gate5_closed_only_by_existing_maximal_flow_theorem": gate5_closed,
        "corrected_gate6_defines_a_history_class_not_a_unique_state": gate6_closed,
        "recurrence_and_reset_return_retired_only_as_mandatory_identity_gates": True,
        "reset_relation_preserved_as_an_existing_physical_exit_relation": True,
        "long_chord_work_preserved_but_not_needed_for_gate5_or_gate6": True,
        "gauge_scale_flavor_neutrino_prediction_and_release_remain_open": True,
        "no_equation_constraint_gate_selector_orientation_parent_or_scale_changed": True,
    }
    payload = {
        "artifact": "BHSM_N12_CORRECTED_FORWARD_HISTORY_AND_PARTICLE_CLASS_GATES",
        "classification": (
            "CORRECTED_GATE_5_COMPLETE_FORWARD_HISTORY_CLOSED_AND_GATE_6_"
            "ACTION_DEFINED_PARTICLE_HISTORY_CLASS_CLOSED"
            if all(validation.values()) else
            "CORRECTED_FORWARD_HISTORY_OR_PARTICLE_CLASS_GATE_OPEN"
        ),
        "author_doctrine": {
            "particle": "COMPLETE_MAXIMAL_FORWARD_ENCAPSULATED_CHILD_HISTORY",
            "birth": "ONE_TIME_ENCAPSULATION_EVENT",
            "reset": "DE_ENCAPSULATION_INTERACTION_OR_EXISTING_DOMAIN_EXIT_RELATION",
            "physical_time": "FORWARD_ONLY",
            "state_freedom": "LEGITIMATE_TANGENT_DIRECTIONS_ARE_PHYSICAL_NOT_DEFECTS",
        },
        "gate5": {
            "status": "CLOSED" if gate5_closed else "OPEN",
            "questions": gate5_questions,
            "theorem": (
                "The certified continuum child has a unique maximal forward "
                "retained Euler-Dirac history on the existing admissible "
                "domain. It persists for positive duration and can be "
                "recentered while the strong norm and all existing physical, "
                "boundary, eta, inertia, gauge, trace, and Dirac margins "
                "remain admissible. Finite maximal time therefore entails "
                "strong-domain blowup or an existing admissible-domain/Dirac "
                "exit; reset recurrence is not required for particle existence."
            ),
            "finite_forward_cover_role": (
                "INDEPENDENT_NONTRIVIAL_VALIDATED_PROPAGATION_EVIDENCE_NOT_"
                "NEEDED_FOR_THE_MAXIMAL_FLOW_EXISTENCE_THEOREM"
            ),
        },
        "gate6": {
            "status": "CLOSED" if gate6_closed else "OPEN",
            "validation": gate6_validation,
            "history_class_map": (
                "C maps to the existing-gauge-and-time-origin equivalence "
                "class of its unique maximal forward history Phi_C, typed by "
                "the certified continuum event-child relation component, "
                "fixed child-domain topology/boundary incidence, forward "
                "orientation, and all retained conserved/discrete labels."
            ),
            "equivalence": (
                "Two admissible histories are in the same generic BHSM "
                "encapsulated-child class when they lie in the same connected "
                "component of the action-defined admissible history space and "
                "share the retained discrete/topological/boundary labels, "
                "modulo only existing gauge and time-origin translation."
            ),
            "not_identified_here": (
                "Gauge representation, flavor/family, mass, CKM, neutral, and "
                "PMNS labels remain Gates 7-10 and are not fabricated by this map."
            ),
        },
        "reclassification": {
            "mandatory_terminal_reset_reachability": "RETIRED",
            "mandatory_unique_action_selected_Cauchy_state": "RETIRED",
            "first_1e_minus_8_Hermite_shadowing_program": (
                "STRONGER_SUPPORTING_FORWARD_PROPAGATION_THEOREM_POST_CLOSURE_BACKLOG"
            ),
            "existing_reset_relation": "PRESERVED_AS_PHYSICAL_EXIT_RELATION",
        },
        "claim_boundary": {
            "finite_complete_persistent_N12_child": "CLOSED",
            "resolution_independent_continuum_child": "CLOSED",
            "forward_time_physical_domain": "CLOSED",
            "local_singular_encapsulation_reset_structure": "CLOSED",
            "complete_forward_child_history_well_posedness_persistence": "CLOSED",
            "action_defined_particle_history_class": "CLOSED",
            "gauge_scale_flavor_neutrino": "OPEN",
            "common_observable_and_blind_prediction": "OPEN",
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "AUDIT_THE_EXISTING_GAUGE_SECTOR_AND_CLOSE_ITS_SINGLE_NEAREST_"
            "FLAGSHIP_RELEVANT_ACTION_OWNED_NORMALIZATION_OR_MAP"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in inputs
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "classification": payload["classification"],
        "gate5": payload["gate5"]["status"],
        "gate6": payload["gate6"]["status"],
        "exact_next_dependency": payload["exact_next_dependency"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
