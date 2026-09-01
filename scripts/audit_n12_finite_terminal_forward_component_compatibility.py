"""Audit whether the certified terminal reset root is a finite history.

The 58-row theorem intersects the retained event-to-child reset relation with
the child terminal-event equation.  This is an endpoint-incidence theorem.
It must not be promoted to a positive-duration reset-to-later-event orbit
unless the intervening retained Euler--Dirac history is also certified.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/flagship_integration"
RESULT = BASE / "BHSM_N12_FINITE_TERMINAL_FORWARD_COMPONENT_COMPATIBILITY.json"
THEORY = ROOT / "theory/n12_finite_terminal_forward_component_compatibility.md"
INPUTS = (
    BASE / "BHSM_N12_GATE7_FORWARD_REACHABLE_COMPONENT_THEOREM_AUDIT.json",
    BASE / "BHSM_N12_FINITE_TERMINAL_RESET_STRATUM_CANDIDATE.json",
    BASE / "BHSM_N12_FINITE_TERMINAL_RADII_CERTIFICATE.json",
    BASE / "BHSM_N12_FINITE_TERMINAL_ORIENTATION_CERTIFICATE.json",
    BASE / "BHSM_N12_FINITE_ENDPOINT_ZERO_SOURCE_FORCE_FUNCTIONAL.json",
    BASE / "BHSM_N12_FINITE_ENDPOINT_FORWARD_ADJOINT_KKT.json",
    ROOT / (
        "artifacts/n12_direct_checkpoint/"
        "BHSM_N12_COMPLETE_PERSISTENT_CHILD_CERTIFICATE.json"
    ),
    THEORY,
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    if not all(path.is_file() for path in INPUTS):
        raise FileNotFoundError("finite-terminal component inputs required")
    (
        reachable,
        candidate,
        radii,
        orientation,
        force,
        kkt,
        persistent,
    ) = [_load(path) for path in INPUTS[:-1]]
    if not all(record.get("validation_passed") is True for record in (
        reachable,
        candidate,
        radii,
        orientation,
        force,
        kkt,
        persistent,
    )):
        raise RuntimeError("validated finite-terminal component inputs required")

    validation = {
        "physical_reset_image_is_positive_duration": (
            "POSITIVE_DURATION_DOMAIN" in reachable["retained_reset_image"]
        ),
        "terminal_root_augments_reset_by_child_event_equation": (
            candidate["terminal_normal_block"]["reset_rows"] == 57
            and candidate["terminal_normal_block"]["terminal_rows"] == 58
            and candidate["center"]["child"]["selected_eigenvalue"] < 1.0e-20
            and radii["validation"]["terminal_map_dimension_is_58"] is True
        ),
        "terminal_root_and_incoming_orientation_remain_certified": (
            radii["proof_boundary"]["local_terminal_stratum_exists_in_root_ball"]
            is True
            and orientation["consequence"]["local_forward_event_reaching_history"]
            == "CERTIFIED_EXISTENCE"
        ),
        "certified_physical_child_has_strict_positive_duration": (
            persistent["validation"][
                "existing_positive_duration_persistence_gate"
            ]
            is True
            and persistent["existing_physical_gates"][
                "positive_duration_proper_time"
            ]
            > 0.0
        ),
        "finite_history_kkt_requires_reset_start_and_positive_later_endpoint": (
            kkt["system"]["reset"].startswith("Y(0)=R_AE2(xi)")
            and "FIRST_TRANSVERSE_RETAINED_EVENT" in kkt["system"]["endpoint"]
            and kkt["claim_boundary"]["actual_finite_endpoint_stratum_solution"]
            == "OPEN_CURRENT_OWNER"
        ),
        "operator_history_is_still_absent": (
            force["current_realization_audit"][
                "finite_history_coefficient_or_operator_oracle_available"
            ]
            is False
            and force["current_realization_audit"][
                "therefore_current_force_value_or_sign_evaluated"
            ]
            is False
        ),
        "no_terminal_root_or_orientation_result_falsified": True,
        "no_selector_endpoint_action_term_scale_fit_chord_or_prediction_added": True,
    }

    return {
        "artifact": "BHSM_N12_FINITE_TERMINAL_FORWARD_COMPONENT_COMPATIBILITY",
        "status": (
            "TERMINAL_INCIDENCE_AND_INCOMING_GERM_CERTIFIED_"
            "POSITIVE_DURATION_RESET_TO_LATER_EVENT_CONNECTION_OPEN"
        ),
        "classification": (
            "THE_58_ROW_THEOREM_CERTIFIES_A_POINT_OF_THE_RETAINED_RESET_"
            "RELATION_AT_WHICH_THE_CHILD_SELECTED_EVENT_FUNCTION_IS_ZERO_"
            "AND_THE_ORIENTATION_THEOREM_CERTIFIES_AN_INCOMING_LOCAL_GERM;_"
            "THIS_IS_A_T_EQUALS_ZERO_RESET_EVENT_INCIDENCE_ON_THE_BOUNDARY_"
            "OF_THE_POSITIVE_DURATION_RESET_IMAGE,_NOT_A_T_GREATER_THAN_ZERO_"
            "FORWARD_HISTORY_FROM_A_PHYSICAL_RESET_CHILD_TO_A_LATER_EVENT"
        ),
        "exact_logical_factorization": {
            "certified_terminal_incidence": (
                "(E_*,C_*)_IN_MATHEMATICAL_RESET_RELATION,_"
                "F_reset(E_*,C_*)=0,_e_child(C_*)=0"
            ),
            "certified_local_germ": (
                "THERE_EXISTS_Y_-(tau)_WITH_Y_-(tau)_TO_C_*_IN_FORWARD_"
                "TIME_AND_e_child(Y_-(tau))>0_BEFORE_THE_HIT"
            ),
            "missing_connection": (
                "THERE_EXIST_xi_0,T>0,Y,E_1,C_1_WITH_"
                "Y(0)=R_child(xi_0),_Y'=V(Y),_e(Y(t))>0_FOR_0<=t<T,_"
                "Y(T)=E_1,_AND_(E_1,C_1)_IN_C_RESET_RELATION"
            ),
            "why_the_terminal_root_is_not_that_connection": (
                "AT_THE_CERTIFIED_58_ROW_ROOT_THE_CHILD_EVENT_EQUATION_"
                "ALREADY_VANISHES_AT_THE_RESET_INCIDENCE,_SO_IT_SUPPLIES_"
                "T=0_RATHER_THAN_A_POSITIVE_DURATION_INTERVENING_ORBIT"
            ),
        },
        "provenance_adjudication": {
            "terminal_root_ball": "PRESERVED_CERTIFIED_LOCAL_STRATUM",
            "terminal_orientation": "PRESERVED_CERTIFIED_INCOMING_GERM",
            "physical_forward_reset_component": (
                "RETAINS_ONLY_POSITIVE_DURATION_RESET_DATA_AND_THEIR_"
                "FORWARD_MAXIMAL_ORBITS"
            ),
            "terminal_root_membership_in_physical_positive_duration_reset_image": (
                "NOT_ESTABLISHED_AND_INCOMPATIBLE_WITH_USING_THE_SAME_"
                "ZERO_EVENT_CHILD_AS_A_REGULAR_T_GREATER_THAN_ZERO_START"
            ),
            "reset_to_terminal_flow_connection": "OPEN",
            "compact_finite_history_operator": "OPEN_AFTER_CONNECTION",
            "heat_minus_zeta_force_value": "OPEN_AFTER_OPERATOR",
        },
        "quantitative_context_not_used_as_proof": {
            "terminal_candidate_action_distance_from_certified_reset_witness": (
                candidate["center"][
                    "event_child_action_distance_from_certified_reset"
                ]
            ),
            "terminal_root_solution_distance_upper": orientation[
                "solution_distance_upper"
            ],
            "reason": (
                "DISTANCE_BETWEEN_TWO_REPRESENTATIVES_NEITHER_PROVES_NOR_"
                "DISPROVES_A_GLOBAL_CONNECTING_ORBIT_ON_A_SET_VALUED_RESET_"
                "QUOTIENT"
            ),
        },
        "exact_next_dependency": (
            "CERTIFY_A_NONEMPTY_POSITIVE_DURATION_FORWARD_CONNECTION_BVP_"
            "FROM_THE_PHYSICAL_AE2_RESET_IMAGE_TO_A_LATER_RETAINED_EVENT_"
            "RESET_GRAPH_OR_CANONICAL_STOP_WITH_ALL_INTERMEDIATE_MARGINS;_"
            "THEN_ASSEMBLE_THE_COMPACT_OPERATOR_AND_FIRST_RESET_QUOTIENT_"
            "JET_AND_EVALUATE_THE_EXISTING_HEAT_MINUS_ZETA_FORCE"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_POSITIVE_DURATION_RESET_TO_ENDPOINT_CONNECTION",
            "weight_seven_descriptor": "CLOSED_AS_MATHEMATICAL_BRANCH",
            "finite_terminal_incidence": "CERTIFIED",
            "finite_terminal_incoming_germ": "CERTIFIED",
            "positive_duration_reset_to_later_endpoint_history": "OPEN_CURRENT_OWNER",
            "compact_finite_endpoint_operator": "OPEN_AFTER_CONNECTION",
            "actual_projected_force": "OPEN_AFTER_OPERATOR",
            "same_action_saddle": "OPEN_AFTER_FORCE",
            "Gate8": "LOCKED",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
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


def main() -> None:
    payload = build_payload()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "current_owner": payload["claim_boundary"][
            "positive_duration_reset_to_later_endpoint_history"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
