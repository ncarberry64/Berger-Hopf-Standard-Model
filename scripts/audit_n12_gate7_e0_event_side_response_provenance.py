"""Exhaust candidate provenance for the Gate-7 E0 parent-arm response."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
RESULT = BASE / "BHSM_N12_GATE7_E0_EVENT_SIDE_RESPONSE_PROVENANCE_AUDIT.json"
POSITIVE = ROOT / "artifacts" / "n12_continuum_majorant_effectiveness" / "BHSM_N12_POSITIVE_DURATION_CALDERON_HISTORY.json"
RICCATI = BASE / "BHSM_N12_EVENT_NORMAL_WEYL_RICCATI.json"
TWO_SIDED = BASE / "BHSM_N12_EVENT_NORMAL_TWO_SIDED_SEAM_CORRECTION.json"
MAXIMAL = BASE / "BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json"
HISTORICAL = BASE / "BHSM_N12_HISTORICAL_RELATIVE_DETERMINANT_REUSE_AUDIT.json"
ROLE = BASE / "BHSM_N12_COMPACT_HISTORY_ENDPOINT_ROLE_PROVENANCE.json"
ONTOLOGY = BASE / "BHSM_N12_GATE7_CLOSED_SYSTEM_ZERO_EXTERNAL_SOURCE_ONTOLOGY.json"
BIRTH = BASE / "BHSM_N12_GATE7_BIRTH_GRAPH_LOAD_MATCHING_AUDIT.json"
TWO_SEAM = BASE / "BHSM_N12_GATE7_TWO_SEAM_CLOSED_OPERATOR_ASSEMBLY.json"
AE2 = ROOT / "artifacts" / "action_extension" / "BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"
THEORY = ROOT / "theory" / "n12_gate7_e0_event_side_response_provenance_audit.md"
INPUTS = (
    POSITIVE, RICCATI, TWO_SIDED, MAXIMAL, HISTORICAL, ROLE, ONTOLOGY,
    BIRTH, TWO_SEAM, AE2, THEORY,
)


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing E0 provenance inputs: " + ", ".join(missing))
    (
        positive, riccati, two_sided, maximal, historical, role, ontology,
        birth, two_seam, ae2,
    ) = map(_load, INPUTS[:-1])
    records = (
        positive, riccati, two_sided, maximal, historical, role, ontology,
        birth, two_seam, ae2,
    )
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated E0 provenance parents required")

    candidates = [
        {
            "candidate": "BHSM_N12_POSITIVE_DURATION_CALDERON_HISTORY",
            "required_type": "WHOLE_PRE_E0_PARENT_CALDERON_FAMILY_AND_FIRST_QUOTIENT_JET",
            "available": "ONE_SAMPLED_PARENT_BACKWARD_COLLAR_STEP_AND_EVENT_CHILD_SYMBOL_GAP",
            "domain_check": "NO_CERTIFIED_WHOLE_PARENT_INTERVAL_OR_ACTION_OWNED_FAR_END_GRAPH",
            "provenance_check": "SAMPLED_RK4_EXPLICITLY_NOT_PROMOTED_TO_INTERVAL_THEOREM",
            "verdict": "INVALID_AS_M_E0_LOCAL_COEFFICIENT_COLLAR_ONLY",
        },
        {
            "candidate": "BHSM_N12_EVENT_NORMAL_WEYL_RICCATI",
            "required_type": "PHYSICAL_PARENT_ARM_WEYL_VALUE",
            "available": "RICCATI_AND_LINEARIZED_TRANSFER_IDENTITIES",
            "domain_check": "INITIAL_VALUE_REQUIRES_COMPLETE_TWO_SIDED_LOAD",
            "provenance_check": "M_AT_ZERO_EQUALS_W_PHYS_WAS_SUPERSEDED",
            "verdict": "VALID_TRANSFER_IDENTITY_INVALID_AS_REALIZED_M_E0_VALUE",
        },
        {
            "candidate": "BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN",
            "required_type": "ACTION_REALIZED_PRE_E0_PARENT_HISTORY_AND_ENDPOINT_OUTCOME",
            "available": "ABSTRACT_EVENT_STOP_OR_FRIEDRICHS_DOMAIN_DICHOTOMY",
            "domain_check": "UNIQUE_DOMAIN_RULE_BUT_COEFFICIENT_ORACLE_AND_OUTCOME_OPEN",
            "provenance_check": "ACTION_OWNED_ABSTRACT_DOMAIN_ONLY",
            "verdict": "VALID_DOMAIN_TYPE_INVALID_AS_RESPONSE_VALUE",
        },
        {
            "candidate": "BHSM_N12_C2_1222_SEGMENT_NEGATIVE_AXIS_WEYL_FAMILY",
            "required_type": "PRE_E0_PARENT_RESPONSE",
            "available": "DISTINCT_POST_E1_CHILD_FINITE_CORE_RESPONSE",
            "domain_check": "WRONG_HISTORY_ARM_AND_MAXIMAL_TAIL_OPEN",
            "provenance_check": "NO_RECURRENCE_OR_REFLECTION_IDENTIFICATION_RETAINED",
            "verdict": "INVALID_HISTORY_AND_ORIENTATION_MATCH",
        },
        {
            "candidate": "BHSM_N12_HISTORICAL_RELATIVE_DETERMINANT_REUSE_AUDIT",
            "required_type": "CURRENT_N12_PARENT_ARM_OPERATOR",
            "available": "REDUCED_OR_FINITE_MATRIX_TEMPLATES",
            "domain_check": "CURRENT_N12_FIELDS_HISTORY_AND_DOMAIN_ABSENT",
            "provenance_check": "HISTORICAL_AUDIT_EXPLICITLY_FORBIDS_PROMOTION",
            "verdict": "INVALID_SCOPE_TEMPLATE_ONLY",
        },
        {
            "candidate": "BHSM_N12_COMPACT_HISTORY_ENDPOINT_ROLE_PROVENANCE",
            "required_type": "CURRENT_OWNER_ZERO_SOURCE_BIRTH_DOMAIN",
            "available": "OLDER_DIRICHLET_REFERENCE_INTERPRETATION",
            "domain_check": "ZERO_TRACE_REFERENCE_IS_NOT_CURRENT_PHYSICAL_BIRTH_GRAPH",
            "provenance_check": "SUPERSEDED_BY_OWNER_SOURCE_ONTOLOGY",
            "verdict": "INVALID_SUPERSEDED_SOURCE_SEMANTICS",
        },
        {
            "candidate": "AE2_EVENT_COMPLETE_CHILD_CORRESPONDENCE",
            "required_type": "NONZERO_PARENT_ARM_CALDERON_VALUE_AND_JET",
            "available": "TRACE_CONORMAL_RESET_LIFT_AND_CONTACT_TYPES",
            "domain_check": "CORRECT_EVENT_TRACE_SPACE_BUT_NO_PARENT_BULK_RESPONSE",
            "provenance_check": "PHYSICAL_BLOCK_VALUES_NOT_ACTION_DERIVED_IN_CORRESPONDENCE",
            "verdict": "VALID_TYPE_MATCH_VALUE_MISSING",
        },
    ]
    validation = {
        "local_parent_backward_sample_is_not_promoted": (
            positive["measurement"]["is_a_rigorous_positive_duration_observation_lower_bound"] is False
            and positive["steps"] == 1
        ),
        "one_sided_Riccati_initialization_is_superseded": (
            two_sided["supersession"]["superseded_claim"]
            == "M(0,z)=W_phys_AS_THE_PHYSICAL_AE2_EVENT_INITIAL_VALUE"
            and riccati["claim_boundary"]["actual_N12_exterior_Weyl_value_and_jet"]
            == "OPEN"
        ),
        "abstract_domain_does_not_supply_history_value": (
            maximal["ownership"]["complete_history_coefficient_oracle_available"] is False
            and maximal["ownership"]["which_maximal_outcome_occurs_numerically_known"] is False
        ),
        "historical_current_N12_operator_is_absent": (
            historical["current_fit"]["historical_candidate_closes_Gate7_now"] is False
        ),
        "older_Dirichlet_birth_role_is_superseded": (
            role["endpoint_roles"]["birth"]["zero_source_restriction"]
            == "Gamma0_birth(U)=0"
            and ontology["validation"]["zero_external_source_does_not_impose_zero_birth_trace"] is True
        ),
        "AE2_supplies_type_not_parent_response_value": (
            ae2["action_definition"]["trace_graph"]
            == "Gamma0_child(Psi)=U_R*Gamma0_event(Psi)"
            and birth["matching_audit"]["M_E0_nonzero_event_side_Calderon_family"]
            == "ACTUALLY_MISSING"
        ),
        "two_seam_topology_is_closed_but_values_are_open": (
            two_seam["adjudication"]["complete_internal_operator_topology"] == "CLOSED"
            and two_seam["adjudication"]["complete_internal_operator_numerical_family"]
            == "OPEN_CURRENT_OPERATOR_OWNER"
        ),
        "no_C2_recurrence_reflection_source_selector_or_new_endpoint_used": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N12_GATE7_E0_EVENT_SIDE_RESPONSE_PROVENANCE_AUDIT",
        "status": (
            "E0_EVENT_SIDE_PROVENANCE_EXHAUSTED_REALIZED_PARENT_ARM_OPEN"
            if passed else "E0_EVENT_SIDE_PROVENANCE_NOT_VALIDATED"
        ),
        "classification": (
            "THE_REPOSITORY_CONTAINS_THE_PARENT_EVENT_STATE,_A_LOCAL_BACKWARD_"
            "COLLAR_SAMPLE,_THE_AE2_TRACE_DOMAIN,_AND_INVERSE_FREE_TRANSFER_"
            "MACHINERY,_BUT_NO_ACTION_REALIZED_WHOLE_PRE_E0_PARENT_OPERATOR_"
            "WITH_ENDPOINT_DOMAIN,_M_E0_VALUE,_OR_FIRST_QUOTIENT_JET"
        ),
        "required_slot": {
            "operator": "M_E0(z;xi):EVENT_TRACE_TO_OUTWARD_PARENT_CONORMAL",
            "spectral_domain": "EVERY_RETAINED_GRADED_LEVEL_AND_REAL_z<0",
            "parameter_domain": "CERTIFIED_LOCAL_RESET_QUOTIENT_FAMILY",
            "first_jet": "D_xi_M_E0_IN_THE_RESET_COMPATIBLE_CONNECTION",
        },
        "candidate_matching_audit": candidates,
        "minimal_missing_data_package": [
            "ACTION_GENERATED_PRE_E0_PARENT_COEFFICIENT_HISTORY",
            "PARENT_OWN_ACTION_ENDPOINT_EVENT_STOP_OR_FRIEDRICHS_CLASS",
            "RETAINED_GRADED_SECTOR_FORMS_ON_THAT_HISTORY",
            "FIRST_RESET_QUOTIENT_COEFFICIENT_AND_ENDPOINT_JETS",
        ],
        "available_evaluation_machinery": [
            "INVERSE_FREE_CALDERON_TRANSFER",
            "EVENT_NORMAL_RICCATI_IDENTITY",
            "LINEARIZED_RICCATI_FIRST_JET",
            "BORDERED_BIRTH_REDUCTION",
            "TWO_SEAM_DIRECT_SCHUR_EQUIVALENCE",
        ],
        "adjudication": {
            "new_operator_theory_required": False,
            "new_action_term_or_boundary_selector_required": False,
            "actual_pre_E0_parent_realization": "OPEN_CURRENT_HISTORY_OWNER",
            "M_E0_and_first_jet": "WAITING_ON_PARENT_REALIZATION",
            "Gate7": "OPEN",
            "Gate8": "LOCKED",
        },
        "exact_next_dependency": (
            "REALIZE_OR_CERTIFY_THE_ACTION_OWNED_PRE_E0_PARENT_HISTORY_TO_ITS_"
            "OWN_EXISTING_EVENT_CANONICAL_STOP_OR_FRIEDRICHS_END,_THEN_APPLY_"
            "THE_EXISTING_INVERSE_FREE_CALDERON_RICCATI_FIRST_JET_MACHINERY_"
            "TO_OBTAIN_M_E0;_DO_NOT_IDENTIFY_IT_WITH_M_C2_OR_A_REFLECTED_HISTORY"
        ),
        "validation": validation,
        "validation_passed": passed,
        "claim_boundary": {
            "Gate7": "ACTIVE_PRE_E0_PARENT_REALIZATION_AND_C2_MAXIMAL_TAIL",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FULL_BHSM_COMPLETE": False,
            "M_E0_realized": False,
            "frozen_predictions_changed": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "M_E0": payload["adjudication"]["M_E0_and_first_jet"],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
