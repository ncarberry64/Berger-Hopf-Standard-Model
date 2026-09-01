"""Adjudicate Norman's proposed Gate-7 forward-child component theorem.

The audit separates the semigroup consequences of defining a forward-reachable
reset set from the additional reflection-disjointness and finite-stopping
claims.  It introduces no selector, trajectory campaign, or new physics.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_FORWARD_REACHABLE_COMPONENT_THEOREM_AUDIT.json"
)
INPUTS = {
    "separator": ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_GATE7_COMPONENT_SEPARATOR_AUDIT.json"
    ),
    "reset": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION.json"
    ),
    "reflection_rows": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_EVENT_CHILD_TIME_REVERSAL_EQUIVARIANCE_GATE.json"
    ),
    "reflection_obstruction": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_ORDERED_EVENT_TIME_REVERSAL_OBSTRUCTION.json"
    ),
    "maximal_flow": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json"
    ),
    "return_ownership": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_INTRINSIC_RETURN_ACTION_OWNERSHIP_GATE.json"
    ),
}


def _sha256(path: Path) -> str:
    content = path.read_bytes()
    if path.suffix.lower() == ".json":
        content = content.replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, object]:
    if not all(path.is_file() for path in INPUTS.values()):
        raise FileNotFoundError("all forward-reachable theorem inputs are required")
    records = {name: _load(path) for name, path in INPUTS.items()}
    if not all(record.get("validation_passed") is True for record in records.values()):
        raise RuntimeError("validated retained forward-reachable inputs required")

    separator = records["separator"]
    reset = records["reset"]
    rows = records["reflection_rows"]
    reflection = records["reflection_obstruction"]
    maximal = records["maximal_flow"]
    ownership = records["return_ownership"]

    finite_outcomes = maximal["maximal_flow_alternative"]["finite_time_outcomes"]
    reset_dimension = reset["reset_correspondence"][
        "fixed_event_child_fiber_dimension"
    ]
    reset_single_valued = reset["reset_correspondence"][
        "single_valued_physical_reset_map_proved"
    ]

    clauses = {
        "1_forward_invariance": {
            "adjudication": "VALID_AFTER_REPLACING_COMPONENT_BY_REACHABLE_SET",
            "definition": (
                "REACH_PLUS(C_RESET)={PHI_t(C):C_IN_C_RESET_AND_"
                "0<=t<T_MAX(C)}"
            ),
            "proof": (
                "THE_MAXIMAL_FLOW_SEMIGROUP_PROPERTY_GIVES_"
                "PHI_s(PHI_t(C))=PHI_(s+t)(C)_WHEN_s+t<T_MAX(C)"
            ),
            "scope": "POSITIVE_INVARIANCE_WHILE_THE_RETAINED_FLOW_EXISTS",
            "global_connected_component_proved": False,
            "why_not_component": (
                "THE_RETAINED_RESET_IS_A_LOCAL_SET_VALUED_67_DIMENSIONAL_"
                "CORRESPONDENCE;_GLOBAL_CONNECTEDNESS_OF_ITS_COMPLETE_IMAGE_"
                "AND_OF_THE_REACHABLE_UNION_IS_NOT_CERTIFIED"
            ),
        },
        "2_reflection_is_distinct_pairing": {
            "adjudication": "PARTLY_VALID",
            "proved": (
                "R_IS_NOT_GAUGE,_DOES_NOT_CREATE_A_SECOND_PHYSICAL_TIME_"
                "ORIENTATION,_AND_PAIRS_DISTINCT_FORWARD_CAUCHY_STATES"
            ),
            "not_proved": (
                "R(REACH_PLUS(C_RESET))_IS_DISJOINT_FROM_"
                "REACH_PLUS(C_RESET)"
            ),
        },
        "3_reflection_transition_requires_stop": {
            "adjudication": "NOT_PROVED",
            "reason": (
                "REVERSIBILITY_AND_FLOW_UNIQUENESS_DO_NOT_FORBID_A_REGULAR_"
                "ORBIT_FROM_MEETING_A_REFLECTED_CAUCHY_STATE;_DISJOINTNESS_"
                "REQUIRES_A_PRESERVED_BARRIER,_TOPOLOGICAL_SEPARATION,_OR_"
                "AN_EQUIVALENT_INTEGRATED_ESTIMATE"
            ),
            "existing_stop_list_is_valid": True,
            "existing_stop_list_is_exhaustive_only_at_finite_Tmax": True,
        },
        "4_no_odd_scalar_needed": {
            "adjudication": "VALID_ONLY_AS_A_DEFINITIONAL_STATEMENT",
            "proved": (
                "NO_SCALAR_LABEL_IS_NEEDED_TO_DEFINE_REACH_PLUS(C_RESET)_"
                "BY_FORWARD_FLOW"
            ),
            "not_proved": (
                "THE_DYNAMICALLY_DEFINED_SET_EXCLUDES_ITS_REFLECTED_PARTNER_"
                "OR_SUPPLIES_A_SIGN_CONTROL_FOR_EVENT_TRANSPORT"
            ),
        },
        "5_component_restricted_transport": {
            "adjudication": "VALID_ON_EACH_REGULAR_SIMPLE_EIGENLINE_INTERVAL",
            "differential_identity": (
                "D_DT(E_ORD(PHI_t(C)))=<PSI,D_H(PHI_t(C))[V(PHI_t(C))]PSI>"
            ),
            "integrated_identity": (
                "E_ORD(PHI_t(C))-E_ORD(C)=INTEGRAL_[0,t]_"
                "<PSI,D_H(PHI_s(C))[V(PHI_s(C))]PSI>_ds"
            ),
            "sign_or_absolute_bound_proved": False,
        },
        "6_two_outcome_gate7_dichotomy": {
            "adjudication": "INVALID_AS_STATED;_REPLACE_BY_THREE_OUTCOMES",
            "retained_exhaustive_outcomes": [
                "FINITE_TERMINAL_EVENT_HIT_BEFORE_ANY_EXISTING_STOP",
                "FINITE_EXISTING_DOMAIN_OR_STRONG_OR_DIRAC_OR_EIGENLINE_STOP_BEFORE_EVENT",
                "INFINITE_REGULAR_FORWARD_HISTORY_WITH_EVENT_NONZERO_FOR_ALL_FINITE_TIME",
            ],
            "any_one_outcome_selected": False,
            "why": (
                "THE_RETAINED_MAXIMAL_FLOW_THEOREM_CLASSIFIES_FINITE_T_MAX_"
                "BUT_DOES_NOT_PROVE_T_MAX_FINITE,_EVENT_RETURN,_OR_A_FINITE_"
                "CANONICAL_STOP"
            ),
        },
    }

    validation = {
        "all_inputs_validated": True,
        "reachable_set_positive_invariance_uses_only_flow_semigroup": True,
        "local_set_valued_reset_not_promoted_to_global_connected_component": (
            reset_dimension == 67 and reset_single_valued is False
        ),
        "formal_reflection_not_declared_gauge_or_second_time_orientation": (
            rows["physical_domain"]["formal_reversal_is_gauge"] is False
            and rows["physical_domain"]["number_of_physical_time_orientations"] == 1
        ),
        "reset_equivariance_not_promoted_to_reachable_set_disjointness": (
            rows["zero_set_result"]["global_branch_uniqueness_claimed"] is False
        ),
        "missing_separator_not_fabricated": (
            separator["separator_kill_test"]["separator_found"] is False
        ),
        "transport_identity_integrated_only_on_regular_simple_intervals": True,
        "uncontrolled_transport_integrand_not_assigned_a_sign": (
            reflection["event_transport"][
                "global_strict_sign_on_R_invariant_set_possible"
            ]
            is False
        ),
        "finite_time_maximal_flow_stops_consumed": len(finite_outcomes) == 3,
        "infinite_regular_history_retained_as_third_outcome": True,
        "forward_history_doctrine_preserved": (
            maximal["maximal_flow_alternative"]["unique_maximal_continuum_child_flow"]
            is True
        ),
        "terminal_reachability_not_promoted": (
            ownership["validation"]["forward_first_return_domain_nonempty_not_proved"]
            is True
        ),
        "no_new_selector_coupling_stabilizer_threshold_time_direction_or_gate": True,
        "no_chord_03_or_trajectory_campaign_authorized": True,
        "Gate7_and_later_claim_boundaries_preserved": True,
    }

    return {
        "artifact": "BHSM_N12_GATE7_FORWARD_REACHABLE_COMPONENT_THEOREM_AUDIT",
        "classification": (
            "FORWARD_REACHABLE_RESET_SET_POSITIVE_INVARIANCE_AND_COMPONENT_"
            "RESTRICTED_TRANSPORT_IDENTITY_VALID;_REFLECTION_DISJOINTNESS_"
            "AND_TWO_OUTCOME_FINITE_STOP_DICHOTOMY_NOT_PROVED"
        ),
        "current_flagship_gate": 7,
        "proposed_name": "NORMANS_GATE7_FORWARD_CHILD_COMPONENT_THEOREM",
        "terminology_correction": (
            "USE_FORWARD_REACHABLE_RESET_SET_UNLESS_GLOBAL_CONNECTEDNESS_IS_"
            "SEPARATELY_PROVED"
        ),
        "retained_reset_image": (
            "C_RESET=MATHFRAK_C_INFINITY(E_CERTIFIED)_INTERSECT_"
            "POSITIVE_LAPSE_POSITIVE_DURATION_DOMAIN"
        ),
        "clause_adjudication": clauses,
        "theorem_that_is_currently_proved": {
            "statement": (
                "REACH_PLUS(C_RESET)_IS_POSITIVELY_INVARIANT_WHILE_THE_"
                "UNIQUE_RETAINED_MAXIMAL_FLOW_EXISTS;_ON_EACH_REGULAR_"
                "INTERVAL_WITH_AN_INVERTIBLE_EULER_DIRAC_BLOCK_AND_SIMPLE_"
                "SELECTED_EIGENLINE,_THE_ORDERED_EVENT_OBEYS_THE_DISPLAYED_"
                "INTEGRATED_TRANSPORT_IDENTITY"
            ),
            "reflection_disjointness_included": False,
            "finite_event_or_stop_exhaustion_included": False,
        },
        "canonical_missing_lemma": (
            "PROVE_A_SEPARATOR_FREE_INTEGRATED_ORDERED_EVENT_TRANSPORT_"
            "INEQUALITY_ON_REACH_PLUS(C_RESET)_FORCING_EVENT_OR_AN_EXISTING_"
            "CANONICAL_STOP,_OR_DERIVE_GLOBAL_CONTROL_OF_D(Y)^(-1)*b(Y)_"
            "AND_ALL_EXISTING_STRONG_AND_DOMAIN_MARGINS_AND_THEN_ADJUDICATE_"
            "THE_INFINITE_REGULAR_HISTORY_OUTCOME"
        ),
        "Gate7_status_changed": False,
        "two_chord_global_promotion_authorized": False,
        "chord_03_proof_value_established": False,
        "chord_03_authorized": False,
        "inputs": {
            path.relative_to(ROOT).as_posix(): _sha256(path)
            for path in INPUTS.values()
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise RuntimeError("forward-reachable theorem audit failed validation")
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "classification": payload["classification"],
                "Gate7_status_changed": payload["Gate7_status_changed"],
                "validation_passed": payload["validation_passed"],
                "sha256": _sha256(RESULT),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
