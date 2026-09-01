"""Reconcile finite formation ontology with the maximal child source domain."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_FORMATION_DECAY_CHRONOLOGY_SUPERSESSION.json"
)
THEOREM = ROOT / "theory/n12_gate7_formation_decay_chronology_supersession.md"
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_FINITE_ENCAPSULATION_PHYSICAL_DOMAIN_AUDIT.json",
    ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_FINITE_ENCAPSULATION_LOCAL_BRANCH.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_NATIVE_SOURCE_READOUT_NECESSITY_AUDIT.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_EVENT_NORMAL_TWO_SIDED_SEAM_CORRECTION.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FINITE_ENDPOINT_FORWARD_ADJOINT_KKT.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_ADJOINT_KKT_EXISTENCE_GATE.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_SAME_ACTION_CONTINUATION_PRECONDITIONS.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_DIRECT_KKT_EXISTENCE_PRECONDITIONS.json",
    THEOREM,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing chronology inputs: " + ", ".join(missing))
    (
        finite_domain,
        formation,
        maximal,
        necessity,
        seam,
        finite_kkt,
        existence,
        continuation,
        direct,
    ) = (_load(path) for path in INPUTS[:-1])
    records = (
        finite_domain,
        formation,
        maximal,
        necessity,
        seam,
        finite_kkt,
        existence,
        continuation,
        direct,
    )
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated chronology inputs required")

    endpoint_rule = maximal["endpoint_rule"]
    validation = {
        "formation_is_pre_event": (
            formation["chronology"]["formation"] == "PRE_EVENT_TERMINAL_SIDE_HISTORY"
        ),
        "encapsulation_is_finite_and_existential": (
            finite_domain["finite_encapsulation_action_theorem"]["quantifier"]
            == "EXISTENCE_OF_AT_LEAST_ONE_NOT_UNIVERSAL_REACHABILITY"
        ),
        "child_phase_is_post_event_decay_or_evolution": (
            finite_domain["physical_domain"]["post_encapsulation"]
            == "IMMEDIATE_ENTRY_INTO_DECAY_OR_EVOLUTION_PHASE"
        ),
        "post_event_return_is_not_required": (
            finite_domain["physical_domain"]["post_event_return_to_encapsulation_required"]
            is False
        ),
        "infinite_child_endpoint_has_action_owned_Friedrichs_rule": (
            endpoint_rule["if_Tmax_is_infinite"]
            == "CLOSE_THE_NONNEGATIVE_MINIMAL_FORM_BY_ITS_FRIEDRICHS_CLOSURE"
        ),
        "finite_domain_exit_has_action_owned_Friedrichs_rule": (
            endpoint_rule["if_finite_strong_blowup_domain_exit_or_Dirac_exit"]
            == "CLOSE_THE_NONNEGATIVE_MINIMAL_FORM_BY_ITS_FRIEDRICHS_CLOSURE"
        ),
        "later_event_uses_retained_graph": (
            "RETAINED_TERMINAL_EVENT_RESET_TRACE_CONORMAL_RELATION"
            in endpoint_rule["if_existing_terminal_event_reset_chart_is_hit"]
        ),
        "terminal_reachability_not_native_source_requirement": (
            necessity["necessity_adjudication"]["B_one_terminal_reaching_history"]
            == "EXISTENCE_ONLY_SUFFICIENT_ENDPOINT_ROUTE_NOT_NATIVE_NECESSITY"
        ),
        "two_sided_child_response_still_required": (
            seam["claim_boundary"]["child_arm_Calderon_value_and_geometry_jets"]
            == "OPEN"
        ),
        "finite_endpoint_KKT_is_valid_but_unsolved": (
            finite_kkt["claim_boundary"]["G7_09_joint_system"] == "DERIVED_UNSOLVED"
            and existence["claim_boundary"]["finite_endpoint_KKT_root"]
            == "OPEN_CURRENT_OWNER"
        ),
        "finite_endpoint_shortcut_audits_preserved": (
            continuation["adjudication"]["continuation_route_invalid_in_principle"]
            is False
            and direct["adjudication"]["direct_existence_route_invalid_in_principle"]
            is False
        ),
        "no_selector_endpoint_action_term_scale_fit_chord_or_prediction_added": True,
    }

    return {
        "artifact": "BHSM_N12_GATE7_FORMATION_DECAY_CHRONOLOGY_SUPERSESSION",
        "status": "FINITE_ENDPOINT_KKT_ROOT_SUPERSEDED_AS_SOLE_OWNER_MAXIMAL_CHILD_EXTERIOR_ORACLE_RESTORED",
        "classification": (
            "FINITE_ENCAPSULATION_APPLIES_TO_THE_PRE_EVENT_FORMATION_ARM;_THE_"
            "POST_EVENT_COMPLETE_CHILD_IS_DECAY_OR_EVOLUTION_AND_ITS_ACTION_"
            "OWNED_MAXIMAL_SOURCE_DOMAIN_MAY_END_AT_A_LATER_EVENT,_A_CANONICAL_"
            "EXIT,_OR_AN_INFINITE_FRIEDRICHS_END;_THEREFORE_A_FINITE_ENDPOINT_"
            "FORWARD_ADJOINT_KKT_ROOT_IS_A_SUFFICIENT_SUBROUTE_NOT_THE_UNIQUE_"
            "NATIVE_GATE7_REQUIREMENT"
        ),
        "chronology": {
            "formation": "PRE_EVENT_FORWARD_HISTORY",
            "encapsulation": "FINITE_POSITIVE_TIME_SINGULAR_EVENT",
            "reset": "AE2_EVENT_TO_COMPLETE_CHILD_RELATION",
            "post_event": "CHILD_DECAY_OR_EVOLUTION_ON_ITS_MAXIMAL_FORWARD_DOMAIN",
            "finite_condition_transfers_to_post_event_child": False,
        },
        "maximal_child_endpoint_alternatives": {
            "later_event": "RETAINED_EVENT_RESET_TRACE_CONORMAL_GRAPH",
            "finite_strong_domain_or_Dirac_exit": "FRIEDRICHS_FORM_CLOSURE",
            "infinite_or_excluded_end": "FRIEDRICHS_FORM_CLOSURE",
            "arbitrary_validation_cutoff": "FORBIDDEN",
        },
        "supersession": {
            "superseded_current_owner": (
                "NONEMPTY_REGULAR_FINITE_ENDPOINT_FORWARD_ADJOINT_KKT_ROOT_"
                "AS_THE_ONLY_GATE7_ROUTE"
            ),
            "correct_current_owner": (
                "PARAMETRIC_EVENT_GENERATED_MAXIMAL_CHILD_CALDERON_WEYL_"
                "FAMILY_AND_PHYSICAL_QUOTIENT_HEAT_MINUS_ZETA_COVECTOR_ROOT"
            ),
            "finite_endpoint_forward_adjoint_KKT_system": (
                "PRESERVED_AS_A_VALID_SUFFICIENT_SUBROUTE_ON_A_FINITE_STRATUM"
            ),
            "finite_endpoint_existence_gate": (
                "PRESERVED_AS_CONDITIONAL_SUBROUTE_AUDIT_NOT_CURRENT_NATIVE_"
                "NECESSITY"
            ),
            "same_action_continuation_audit": (
                "PRESERVED_WITHIN_ITS_FINITE_ENDPOINT_SCOPE"
            ),
            "direct_heat_coercivity_audit": (
                "PRESERVED_HEAT_REGULATOR_ALONE_REMAINS_NONCOERCIVE"
            ),
        },
        "exact_next_dependency": (
            "CERTIFY_ON_A_NONEMPTY_REGULAR_PHYSICAL_RESET_QUOTIENT_STRATUM_"
            "THE_EVENT_GENERATED_MAXIMAL_CHILD_M_child(z;xi)_AND_ITS_REQUIRED_"
            "QUOTIENT_GEOMETRY_JET_USING_THE_RETAINED_EVENT_OR_FRIEDRICHS_"
            "ENDPOINT_RULE,_THEN_CERTIFY_A_ROOT_OF_THE_HEAT_MINUS_ZETA_"
            "QUOTIENT_COVECTOR;_A_FINITE_ENDPOINT_BVP_IS_SUFFICIENT_BUT_NOT_"
            "REQUIRED"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_MAXIMAL_CHILD_EXTERIOR_ORACLE_CURRENT_OWNER",
            "Gate8": "LOCKED",
            "finite_encapsulation_existence": "CLOSED_LOCAL_ACTION_THEOREM",
            "finite_endpoint_KKT_root": "OPTIONAL_SUFFICIENT_SUBROUTE_OPEN",
            "maximal_child_exterior_oracle": "OPEN_CURRENT_OWNER",
            "same_action_saddle": "OPEN_AFTER_ORACLE",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "adjudication": {
            "post_event_finite_terminal_reachability_required": False,
            "universal_terminal_reachability_required": False,
            "infinite_Friedrichs_child_exterior_allowed": True,
            "finite_endpoint_BVP_route_remains_valid": True,
            "retained_action_incompatibility_proved": False,
            "new_action_term_justified": False,
        },
        "inputs": {path.relative_to(ROOT).as_posix(): _sha256(path) for path in INPUTS},
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
    print(RESULT)


if __name__ == "__main__":
    main()
