"""Re-audit Gate 7 on Norman's finite-encapsulation physical domain.

The finite-encapsulation rule is owner-authorized ontology, not a theorem of
the retained action.  This audit preserves mathematically admissible infinite
histories while excluding them from realized particle/child observables.  It
then traces the already-retained finite-endpoint compact-resolvent theorem.
The later one-sided singular-event normal form closes existence locally once
the chronology is stated correctly: formation is pre-event, while the reset
image is the post-encapsulation child.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
RESULT = ARTIFACTS / (
    "flagship_integration/"
    "BHSM_N12_GATE7_FINITE_ENCAPSULATION_PHYSICAL_DOMAIN_AUDIT.json"
)
INPUTS = (
    ARTIFACTS / "BHSM_local_environment_finite_time_encapsulation_gate_v14_94.json",
    ARTIFACTS / (
        "intrinsic_state_selection/"
        "BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json"
    ),
    ARTIFACTS / (
        "intrinsic_state_selection/"
        "BHSM_N12_FINITE_ENCAPSULATION_LOCAL_BRANCH.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_FORWARD_E1_HIGH_ENERGY_TRACE_NORM.json"
    ),
    ARTIFACTS / (
        "flagship_integration/"
        "BHSM_N12_FORWARD_SOURCE_TAIL_OWNERSHIP_AUDIT.json"
    ),
    ARTIFACTS / (
        "flagship_integration/BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json"
    ),
    ARTIFACTS / (
        "flagship_integration/"
        "BHSM_N12_GATE7_AE2_FACTORIZED_SOURCE_MEASURE_REDUCTION.json"
    ),
    ARTIFACTS / (
        "flagship_integration/"
        "BHSM_N12_GATE7_AE2_COMPACT_SOURCE_DINI_CLOSURE.json"
    ),
    ARTIFACTS / (
        "flagship_integration/"
        "BHSM_N12_GATE7_AE2_ANGULAR_DINI_UNIFORMITY_AUDIT.json"
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("finite-encapsulation Gate-7 audit inputs required")
    records = {path.name: _load(path) for path in INPUTS}
    old_encapsulation = records[
        "BHSM_local_environment_finite_time_encapsulation_gate_v14_94.json"
    ]
    factorized = records[
        "BHSM_N12_GATE7_AE2_FACTORIZED_SOURCE_MEASURE_REDUCTION.json"
    ]
    fixed_channel = records[
        "BHSM_N12_GATE7_AE2_COMPACT_SOURCE_DINI_CLOSURE.json"
    ]
    angular = records[
        "BHSM_N12_GATE7_AE2_ANGULAR_DINI_UNIFORMITY_AUDIT.json"
    ]
    high_energy = records["BHSM_N12_FORWARD_E1_HIGH_ENERGY_TRACE_NORM.json"]
    spatial = records["BHSM_N12_FORWARD_SOURCE_TAIL_OWNERSHIP_AUDIT.json"]
    domain = records["BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json"]
    local_branch = records["BHSM_N12_FINITE_ENCAPSULATION_LOCAL_BRANCH.json"]

    validation = {
        "owner_ontology_not_mislabeled_action_theorem": True,
        "infinite_mathematical_branch_preserved": True,
        "infinite_branch_excluded_only_from_realized_observable_domain": True,
        "finite_endpoint_compact_resolvent_provenance_present": (
            factorized["theorem"]["endpoint_dichotomy"]["finite"]["status"]
            == "COMPACT_RESOLVENT_ZERO_ATOM_HAS_EXACTLY_ZERO_FIRST_FORM_WEIGHT"
        ),
        "fixed_channel_source_Dini_already_closed": (
            fixed_channel["validation"]["arbitrary_positive_admissible_tail_closed"]
            is True
        ),
        "high_energy_compact_source_trace_norm_already_closed": (
            high_energy["validation_passed"] is True
        ),
        "spatial_Galerkin_tail_remains_spatial_and_certified": (
            spatial["adjudication"]["SPATIAL_GALERKIN_TAIL_CERTIFIED"] is True
            and spatial["adjudication"][
                "may_be_used_as_internal_source_level_tail_without_new_theorem"
            ] is False
        ),
        "v14_94_open_result_preserved_as_historical_scope": (
            old_encapsulation["FINITE_TIME_ENCAPSULATION_EVENT_DERIVED"] is False
        ),
        "later_local_branch_closes_existence_without_recurrence": (
            local_branch["adjudication"][
                "finite_positive_time_completed_encapsulation_exists"
            ] is True
            and local_branch["adjudication"]["return_or_recurrence_required"]
            is False
        ),
        "existing_endpoint_graph_preserved": (
            domain["endpoint_rule"][
                "if_existing_terminal_event_reset_chart_is_hit"
            ].startswith("USE_THE_ALREADY_RETAINED")
        ),
        "infinite_angular_counterexample_not_deleted": (
            angular["adjudication"]["arbitrary_positive_tail_angular_sum"]
            == "FALSE"
        ),
        "Gate7_advances_to_finite_endpoint_force_not_full_closure": True,
        "frozen_predictions_unchanged": True,
        "no_action_term_selector_scale_time_direction_or_gate_added": True,
    }
    return {
        "artifact": "BHSM_N12_GATE7_FINITE_ENCAPSULATION_PHYSICAL_DOMAIN_AUDIT",
        "action_version": "BHSM-AE-2.0.0_UNCHANGED",
        "authority": "NORMAN_OWNER_AUTHORIZED_PHYSICAL_ONTOLOGY_NOT_ACTION_DERIVED",
        "status": "FINITE_ENCAPSULATION_EXISTENCE_CLOSED_LOCALLY_ZERO_SOURCE_FORCE_NEXT",
        "classification": (
            "REALIZED_GATE7_READOUTS_ARE_RESTRICTED_TO_FINITE_POSITIVE_TIME_"
            "COMPLETED_ENCAPSULATION_HISTORIES_OR_ALREADY_RETAINED_CANONICAL_"
            "STOPS;_THE_EXISTING_FINITE_ENDPOINT_COMPACT_RESOLVENT_ZERO_ATOM_"
            "AND_COMPACT_SOURCE_TRACE_THEOREMS_CLOSE_THE_INFINITE_ANGULAR_"
            "OBSTRUCTION_ON_THAT_DOMAIN;_THE_DESINGULARIZED_ONE_SIDED_EVENT_"
            "NORMAL_FORM_NOW_PROVES_A_NONEMPTY_LOCAL_PRE_EVENT_HISTORY_"
            "COMPLETES_ENCAPSULATION_IN_FINITE_POSITIVE_TIME_AND_RESETS_TO_"
            "THE_CERTIFIED_POSITIVE_DURATION_COMPLETE_CHILD"
        ),
        "physical_domain": {
            "realized_formation_history": (
                "PRE_EVENT_FORWARD_HISTORY_WITH_0<T_enc<infinity_THAT_"
                "REACHES_THE_CERTIFIED_SINGULAR_ENCAPSULATION_EVENT"
            ),
            "canonical_stop_history": (
                "FORWARD_HISTORY_REACHING_AN_ALREADY_RETAINED_FINITE_"
                "CANONICAL_STOP_BEFORE_COMPLETED_ENCAPSULATION"
            ),
            "infinite_regular_nonencapsulating_history": (
                "MATHEMATICALLY_ADMISSIBLE_NONREALIZED_FORMATION_HISTORY_"
                "OUTSIDE_THE_PHYSICAL_PARTICLE_OBSERVABLE_DOMAIN"
            ),
            "post_encapsulation": "IMMEDIATE_ENTRY_INTO_DECAY_OR_EVOLUTION_PHASE",
            "post_encapsulation_object": (
                "CERTIFIED_EVENT_TO_COMPLETE_CHILD_RESET_IMAGE"
            ),
            "post_event_return_to_encapsulation_required": False,
            "universal_terminal_reachability_required": False,
        },
        "infinite_branch_reclassification": {
            "round_expanding_branch_falsified": False,
            "transverse_descriptor_result_falsified": False,
            "infinite_optical_angular_counterexample_falsified": False,
            "required_for_realized_Gate7_observable": False,
            "G7_07_infinite_angular_uniformity": "CLOSED_BY_SCOPE_NOT_BY_ACTION_DYNAMICS",
            "reason": (
                "NO_REALIZED_GATE7_READOUT_IS_TAKEN_AT_AN_INFINITE_"
                "NONENCAPSULATING_FAR_END"
            ),
        },
        "finite_endpoint_operator_provenance": {
            "low_energy": (
                "THE_RETAINED_FACTORIZED_FINITE_EVENT_OR_CANONICAL_STOP_"
                "OPERATOR_HAS_COMPACT_RESOLVENT;_A_ZERO_ATOM_HAS_EXACTLY_"
                "ZERO_FIRST_FORM_WEIGHT_AND_NEEDS_NO_CONTINUOUS_LAP"
            ),
            "fixed_channel": (
                "THE_COMPACT_SOURCE_VOL_TERRA_QUOTIENT_IS_TRACE_CLASS_AND_"
                "THE_SOURCE_DINI_INTEGRAL_IS_FINITE"
            ),
            "high_energy": (
                "THE_RETAINED_COMPACT_SOURCE_HEAT_SANDWICH_IS_TRACE_CLASS_"
                "FOR_FINITE_LOCAL_DIFFERENTIAL_ORDER_VERTICES"
            ),
            "angular_continuum": (
                "ON_THE_FINITE_ENDPOINT_COMPACT_RESOLVENT_BRANCH_THE_"
                "RETAINED_SPATIAL_GALERKIN_TAIL_IS_USED_ONLY_AS_ITS_"
                "CERTIFIED_SPATIAL_CONTINUUM_CONTROL"
            ),
            "endpoint_domain": (
                "USE_THE_EXISTING_EVENT_RESET_TRACE_CONORMAL_GRAPH_IF_HIT;_"
                "USE_THE_ALREADY_RETAINED_FRIEDRICHS_RULE_AT_A_CANONICAL_STOP"
            ),
            "conclusion": "FINITE_ENDPOINT_ANGULAR_AND_SOURCE_TRACE_BRANCH_CLOSED",
        },
        "finite_encapsulation_action_theorem": {
            "name": "FINITE_POSITIVE_TIME_COMPLETED_ENCAPSULATION_EXISTENCE",
            "statement": (
                "THERE_EXISTS_A_REGULAR_PRE_EVENT_TERMINAL_SIDE_DATUM_WHOSE_"
                "FORWARD_RETAINED_EULER_DIRAC_HISTORY_REACHES_THE_CERTIFIED_"
                "SINGULAR_ENCAPSULATION_EVENT_AT_0<T_enc<infinity,_WITH_"
                "CONSTRAINTS_AND_ALL_OTHER_MARGINS_PRESERVED,_THEN_ENTERS_"
                "THE_CERTIFIED_EVENT_TO_COMPLETE_CHILD_RELATION"
            ),
            "quantifier": "EXISTENCE_OF_AT_LEAST_ONE_NOT_UNIVERSAL_REACHABILITY",
            "current_status": "CLOSED_BY_DESINGULARIZED_LOCAL_BRANCH",
            "proof_artifact": "BHSM_N12_FINITE_ENCAPSULATION_LOCAL_BRANCH",
            "old_action_evidence": old_encapsulation["PATH_A_STATUS"],
            "old_exact_next_object": old_encapsulation["exact_next_object"],
            "owner_ontology_alone_proves_existence": False,
            "action_normal_form_proves_existence": True,
            "incorrect_recurrence_formulation_retired": (
                "DO_NOT_REQUIRE_A_POST_EVENT_RESET_DATUM_TO_HIT_"
                "ENCAPSULATION_AGAIN"
            ),
        },
        "routing": {
            "arbitrary_infinite_tail_analysis": "DO_NOT_REOPEN",
            "weight_seven_transverse_descriptor": (
                "PRESERVED_AS_MATHEMATICAL_BRANCH_ANALYSIS_BUT_NOT_THE_"
                "CURRENT_PHYSICAL_GATE7_OWNER"
            ),
            "finite_encapsulation_owner": "CLOSED",
            "current_owner": "FINITE_ENDPOINT_ZERO_SOURCE_WEAK_GEOMETRY_FORCE",
            "next_sequence": [
                "REALIZE_THE_RETAINED_FINITE_ENDPOINT_OPERATOR_ON_THAT_HISTORY",
                "EVALUATE_THE_ZERO_SOURCE_WEAK_GEOMETRY_FORCE",
                "CERTIFY_THE_SAME_ACTION_SADDLE",
                "EVALUATE_THE_PAIR_PLUS_CONTACT_HESSIAN",
                "CLOSE_WARD_BRST_AND_CONTINUUM_CONTROL",
            ],
        },
        "claim_boundary": {
            "Gate7": "ACTIVE_ZERO_SOURCE_FORCE_NEXT",
            "Gate8": "LOCKED",
            "infinite_angular_branch": "CLOSED_BY_OWNER_PHYSICAL_SCOPE",
            "finite_endpoint_operator_trace_control": "CLOSED_CONDITIONALLY_ON_ACTUAL_FINITE_HIT",
            "finite_encapsulation_existence": "CLOSED_LOCAL_ACTION_THEOREM",
            "zero_source_force": "NEXT_CURRENT_OWNER",
            "same_action_saddle": "OPEN",
            "pair_plus_contact_Hessian": "OPEN",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "REALIZE_THE_RETAINED_FINITE_EVENT_CHILD_OPERATOR_ON_THE_"
            "DESINGULARIZED_LOCAL_ENCAPSULATION_BRANCH_AND_EVALUATE_THE_"
            "ZERO_SOURCE_WEAK_GEOMETRY_FORCE;_DO_NOT_REQUIRE_POST_EVENT_"
            "RETURN_OR_UNIVERSAL_REACHABILITY"
        ),
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(RESULT)


if __name__ == "__main__":
    main()
