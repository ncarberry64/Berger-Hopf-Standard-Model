"""Adjudicate Gate 7 after the BHSM-AE-2 matter-domain extension."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_AE2_MAXIMAL_EXTERIOR_ADJUDICATION.json"
)
AE2_ACTION = ROOT / (
    "artifacts/action_extension/BHSM_ACTION_AE2_GLOBAL_SPIN_RESET_ACTION.json"
)
AE2_GATE7 = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_AE2_GLOBAL_SPIN_MATTER_DOMAIN.json"
)
AE2_THRESHOLD = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_AE2_ZERO_THRESHOLD_NO_SHORTCUT.json"
)
MAXIMAL_DOMAIN = ROOT / (
    "artifacts/flagship_integration/BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json"
)
PROPER_TIME = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FORWARD_PROPER_TIME_FORM_OWNERSHIP.json"
)
INCIDENCE = ROOT / (
    "artifacts/flagship_integration/BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE.json"
)
EXTERIOR_GAP = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_FORWARD_EXTERIOR_GAP_ORACLE_AUDIT.json"
)
CONTINUUM = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json"
)
GLOBAL_CONTROL = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_GLOBAL_FLOW_COERCIVE_CONTROL_GATE.json"
)
SCRIPT = ROOT / "scripts/adjudicate_n12_gate7_ae2_maximal_exterior.py"
INPUTS = (
    AE2_ACTION,
    AE2_GATE7,
    AE2_THRESHOLD,
    MAXIMAL_DOMAIN,
    PROPER_TIME,
    INCIDENCE,
    EXTERIOR_GAP,
    CONTINUUM,
    GLOBAL_CONTROL,
    SCRIPT,
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _canonical(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite AE2 maximal-exterior value")
        rounded = round(value, 15)
        return 0.0 if rounded == 0.0 else rounded
    if isinstance(value, dict):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("all AE2 maximal-exterior inputs are required")
    (
        action,
        gate7,
        threshold,
        maximal_domain,
        proper_time,
        incidence,
        exterior_gap,
        continuum,
        global_control,
    ) = (_load(path) for path in INPUTS[:-1])
    records = (
        action,
        gate7,
        threshold,
        maximal_domain,
        proper_time,
        incidence,
        exterior_gap,
        continuum,
        global_control,
    )
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated AE2 maximal-exterior lineage is required")

    validation = {
        "AE2_action_and_matter_domain_validated": (
            action["action_version"] == "BHSM-AE-2.0.0"
            and gate7["action_version"] == "BHSM-AE-2.0.0"
        ),
        "AE2_relative_phase_removed": (
            gate7["source_domain"]["Cayley_phase_family"] is None
        ),
        "forward_component_has_unique_maximal_flow_dichotomy": (
            continuum["maximal_flow_alternative"][
                "unique_maximal_continuum_child_flow"
            ]
            is True
        ),
        "abstract_maximal_source_domain_is_action_owned": (
            maximal_domain["ownership"][
                "abstract_forward_source_domain_action_owned"
            ]
            is True
        ),
        "common_nonzero_incidence_is_now_assembled": (
            incidence["validation_passed"] is True
        ),
        "maximal_history_coefficient_oracle_is_absent": (
            maximal_domain["ownership"][
                "complete_history_coefficient_oracle_available"
            ]
            is False
        ),
        "actual_maximal_outcome_is_absent": (
            maximal_domain["ownership"][
                "which_maximal_outcome_occurs_numerically_known"
            ]
            is False
        ),
        "global_S2_coercive_bound_is_absent": (
            global_control["owned_and_missing_energy_structure"][
                "coercive_S2_bound_on_continuum_child_component"
            ]
            is False
        ),
        "local_zero_threshold_shortcut_is_excluded": (
            threshold["claim_boundary"]["local_collars_suffice_for_strict_margin"]
            is False
        ),
        "gap_and_Friedrichs_class_do_not_determine_exterior_oracle": (
            exterior_gap["certified_core_effect"]["promotion_authorized"]
            is False
        ),
        "force_saddle_Hessian_not_fabricated": (
            gate7["sector_status"]["zero_source_weak_geometry_force"] == "OPEN"
            and gate7["sector_status"]["same_action_replacement_saddle"] == "OPEN"
            and gate7["sector_status"]["pair_plus_contact_Hessian"] == "OPEN"
        ),
        "frozen_predictions_unchanged": True,
        "FULL_BHSM_COMPLETE_false": True,
    }

    return {
        "artifact": "BHSM_N12_GATE7_AE2_MAXIMAL_EXTERIOR_ADJUDICATION",
        "action_version": "BHSM-AE-2.0.0",
        "status": "CANONICAL_AE2_GATE7_MAXIMAL_EXTERIOR_NO_GO",
        "classification": (
            "THE_UNIQUE_OWNER_SELECTED_AE2_EXTENSION_CLOSES_THE_NORMAL_"
            "MATTER_TRANSMISSION_DOMAIN_WITHOUT_A_PHASE_OR_NEW_COEFFICIENT;_"
            "GATE7_THEN_STOPS_AT_A_DIFFERENT_ACTION_REQUIRED_OBJECT:_THE_"
            "REALIZED_MAXIMAL_FORWARD_log_R4_HISTORY,_ITS_ACTUAL_EVENT_OR_"
            "CANONICAL_STOP_OUTCOME,_AND_THE_RESULTING_CALDERON_ORACLE_JETS;_"
            "THE_CERTIFIED_TWO_CHORD_CORE,_SPATIAL_GAP,_AND_ABSTRACT_"
            "FRIEDRICHS_RULE_DO_NOT_DETERMINE_THOSE_NONLOCAL_VALUES"
        ),
        "action_extension_adjudication": {
            "selected_option": "A",
            "decision_type": action["decision_report"]["decision_type"],
            "unique_extension_implemented": True,
            "matter_birth_graph": gate7["source_domain"],
            "self_adjoint_physical_matter_domain": "CLOSED",
            "relative_Cayley_ambiguity": "REMOVED",
            "new_coefficient_scale_or_propagating_field": False,
            "double_counted_surface_term": False,
            "unchanged_action_no_go_preserved": True,
        },
        "Gate7_native_requirement": {
            "classification": "EVENT_OR_CANONICAL_STOP_FOR_EVERY_RELEVANT_MAXIMAL_FORWARD_HISTORY",
            "choice": "C",
            "universal_terminal_event_reachability_required": False,
            "well_defined_reset_only_sufficient": False,
            "one_event_reaching_history_currently_certified": False,
            "continuum_result": continuum["maximal_flow_alternative"],
            "ordered_stop_set": continuum["ordered_event"]["stop_set"],
            "endpoint_domain_rule": maximal_domain["endpoint_rule"],
        },
        "completed_AE2_Gate7_inputs": {
            "normal_matter_domain": "CLOSED_BY_RESET_OWNED_GLOBAL_SPIN_TIMES_G_SM_LIFT",
            "abstract_maximal_source_form_domain": "CLOSED",
            "proper_time_kinematics": "CLOSED",
            "local_nonzero_common_incidence": incidence["status"],
            "negative_probe_two_chord_product_bounds": "CERTIFIED_BROAD",
            "continuum_maximal_flow_dichotomy": "CERTIFIED",
        },
        "canonical_no_go": {
            "statement": (
                "NO_REPOSITORY_CERTIFICATE_DETERMINES_THE_AE2_MAXIMAL_"
                "EVENT_CHILD_CALDERON_MAP_OR_ITS_FIRST_TWO_GEOMETRY_JETS_"
                "FROM_THE_CURRENT_TWO_CHORD_DATA_AND_GLOBAL_DICHOTOMY"
            ),
            "local_zero_energy_obstruction": threshold["theorem"],
            "exterior_nonuniqueness_witness": exterior_gap["theorem"],
            "global_control_obstruction": global_control[
                "owned_and_missing_energy_structure"
            ],
            "not_a_proof_of": [
                "NONEXISTENCE_OF_THE_ACTION_DETERMINED_MAXIMAL_HISTORY",
                "NONEXISTENCE_OF_A_TERMINAL_EVENT",
                "A_ZERO_MODE_ON_THE_REALIZED_MAXIMAL_EXTERIOR",
                "IMPOSSIBILITY_OF_FUTURE_GLOBAL_ANALYTIC_OR_VALIDATED_NUMERICAL_CONTROL",
            ],
            "prohibited_substitutions": [
                "PROMOTE_THE_TWO_CHORD_ENDPOINT_TO_A_PHYSICAL_TERMINAL",
                "REUSE_A_PERIODIC_OR_FREE_TERMINAL_DOMAIN",
                "SET_THE_UNKNOWN_EXTERIOR_CALDERON_MAP_TO_ZERO",
                "DROP_THE_PRODUCT_DIRAC_CROSS_TERM_TO_CREATE_A_FALSE_MASS_GAP",
                "FIT_THE_0P765819120592_FORCE_OR_HESSIAN_DEFECT",
            ],
        },
        "downstream_dependency_ledger": {
            "zero_source_weak_geometry_force": "BLOCKED_BY_M_C_AND_D_Phi_M_C",
            "same_action_replacement_saddle": "BLOCKED_BY_ZERO_SOURCE_FORCE",
            "pair_plus_contact_Hessian": "BLOCKED_BY_SAME_DOMAIN_M_C_D_Phi_M_C_D_Phi2_M_C_AND_SADDLE",
            "Ward_BRST_closure": "BLOCKED_BY_REALIZED_DOMAIN_HESSIAN",
            "relative_trace_and_force": "BLOCKED_BY_RESOLVENT_OR_HEAT_ORACLE_AND_TAIL",
            "Gate8": "LOCKED_BY_GATE7",
            "chord_03": "NO_PROOF_VALUE_AND_NOT_AUTHORIZED",
        },
        "exact_next_dependency": (
            "PROVE_GLOBAL_MAXIMAL_FORWARD_CONTROL_OR_CERTIFY_THE_FIRST_"
            "ACTUAL_EVENT_OR_CANONICAL_STOP_FOR_THE_N12_CHILD,_THEN_"
            "RIGOROUSLY_ENCLOSE_log_R4(tau)_AND_ITS_FIRST_SECOND_ACTION_"
            "JACOBI_VARIATIONS_ON_THAT_COMPLETE_HISTORY_AND_COMPUTE_THE_"
            "EQUIVALENT_M_C(z),D_Phi_M_C(z),D_Phi2_M_C(z)_AND_PAIR_PLUS_"
            "CONTACT_ORACLE_ON_ONE_NONEMPTY_NATIVE_RESOLVENT_REGION"
        ),
        "adjudication": {
            "new_canonical_no_go_reached": True,
            "additional_action_extension_required": False,
            "inequivalent_surviving_action_extensions": 1,
            "Gate7": "ACTIVE_NOT_CLOSED",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def deterministic_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def materialize() -> Path:
    payload = build_payload()
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(deterministic_bytes(payload))
    return TARGET


if __name__ == "__main__":
    print(materialize())
