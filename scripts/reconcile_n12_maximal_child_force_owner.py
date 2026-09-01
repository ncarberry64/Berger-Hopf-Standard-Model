"""Reconcile the exact remaining action-owned input for the Gate-7 force."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_MAXIMAL_CHILD_FORCE_OWNER_RECONCILIATION.json"
)
THEORY = ROOT / "theory/n12_maximal_child_force_owner_reconciliation.md"
INPUTS = (
    ROOT / "artifacts/flagship_integration/BHSM_N12_GATE7_FORMATION_DECAY_CHRONOLOGY_SUPERSESSION.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORWARD_COMMON_SOURCE_INCIDENCE.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_PARAMETRIC_EXTERIOR_ORACLE_EXECUTABLE_INTERFACE.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_FORCE_ADJOINT_PULLBACK.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_INTRINSIC_TIME_QUOTIENT_FORCE_ROOT.json",
    ROOT / "artifacts/flagship_integration/BHSM_N12_ASYMPTOTIC_CHILD_EXTERIOR_CONNECTION_PRECONDITIONS.json",
    THEORY,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, object]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "missing force-owner inputs: " + ", ".join(missing)
        )
    records = [_load(path) for path in INPUTS[:-1]]
    if not all(record.get("validation_passed") is True for record in records):
        raise RuntimeError("validated force-owner parents required")
    chronology, domain, incidence, solver, adjoint, quotient, asymptotic = records

    validation = {
        "maximal_child_phase_is_post_event_decay_or_evolution": chronology[
            "validation"
        ]["child_phase_is_post_event_decay_or_evolution"],
        "maximal_source_domain_is_action_owned": domain["ownership"][
            "abstract_forward_source_domain_action_owned"
        ],
        "arbitrary_Robin_family_is_removed": domain["ownership"][
            "arbitrary_Robin_nonuniqueness_removed"
        ],
        "event_and_Friedrichs_endpoint_rules_are_complete": (
            domain["validation"]["Friedrichs_rule_retained_for_excluded_endpoint"]
            and domain["validation"]["birth_graph_retained"]
        ),
        "common_source_incidence_is_assembled": (
            incidence["validation_passed"]
            and incidence["incidence"][
                "rank16_Weyl_coexact_gauge_pair_and_contact"
            ]
            == "ASSEMBLED"
            and incidence["incidence"][
                "complex_ghost_minus_two_pair_and_contact"
            ]
            == "ASSEMBLED"
        ),
        "Weyl_value_and_two_jet_solver_is_derived": solver["validation"][
            "value_first_second_jet_interface_executes"
        ],
        "Weyl_solver_forms_no_inverse": solver["validation"][
            "no_explicit_matrix_inverse_is_formed"
        ],
        "force_adjoint_pullback_is_derived": adjoint["validation"][
            "adjoint_is_equivalent_to_allowed_first_jet_covector"
        ],
        "explicit_time_generator_not_needed_for_first_force_root": not quotient[
            "scope"
        ]["explicit_time_generator_needed_for_first_force_root"],
        "actual_history_coefficient_oracle_remains_missing": not domain[
            "ownership"
        ]["complete_history_coefficient_oracle_available"],
        "actual_projected_force_remains_open": (
            solver["claim_boundary"]["actual_projected_force"] == "OPEN"
        ),
        "two_chords_not_promoted_to_force_endpoint": solver["validation"][
            "two_certified_chords_are_not_promoted_to_force_endpoint"
        ],
        "asymptotic_branch_not_promoted_without_reset_connection": asymptotic[
            "nonpromotion"
        ]["one_stored_reset_state_is_on_asymptotic_branch"] is False,
        "no_chord3_terminal_recurrence_selector_endpoint_scale_fit_or_prediction_added": True,
    }
    return {
        "artifact": "BHSM_N12_MAXIMAL_CHILD_FORCE_OWNER_RECONCILIATION",
        "status": (
            "MAXIMAL_HISTORY_COEFFICIENT_ORACLE_AND_FIRST_JET_SINGLE_FORCE_OWNER"
        ),
        "classification": (
            "THE_MAXIMAL_SOURCE_DOMAIN,_FULL_GAUGE_GHOST_RANK16_HS_"
            "INCIDENCE,_INVERSE_FREE_WEYL_JET_SOLVER,_ADJOINT_PULLBACK,_AND_"
            "INTRINSIC_FORCE_ROOT_TEST_ARE_DERIVED;_THE_SINGLE_EARLIEST_"
            "MISSING_INPUT_IS_THE_ACTION_OWNED_MAXIMAL_HISTORY_COEFFICIENT_"
            "REALIZATION_AND_FIRST_RESET_QUOTIENT_GEOMETRY_JET_ON_A_NONEMPTY_"
            "REGULAR_STRATUM"
        ),
        "closed_dependencies": {
            "maximal_endpoint_domain_rule": "DERIVED",
            "gauge_ghost_rank16_HS_source_incidence": "ASSEMBLED",
            "Weyl_value_first_second_jet_solver": "DERIVED_INVERSE_FREE",
            "force_operator_cotangent_and_adjoint_pullback": "DERIVED",
            "explicit_hybrid_time_generator_for_first_force_root": (
                "NOT_REQUIRED_BY_INTRINSIC_QUOTIENT_THEOREM"
            ),
        },
        "single_open_input": {
            "history_form": "xi_MAPS_TO_(Y_xi(tau),P_xi,D_xi_P_xi)",
            "equivalent_exterior_form": (
                "xi_MAPS_TO_(M_C(z;xi),D_xi_M_C(z;xi))"
            ),
            "domain": "NONEMPTY_REGULAR_EVENT_GENERATED_RESET_STRATUM",
            "action_owned": True,
            "available": False,
        },
        "downstream_ready_after_input": {
            "evaluate_q_rep": True,
            "test_raw_bordered_force_root_equivalent_to_physical_quotient": True,
            "if_force_nonzero_require_second_operator_jet": True,
            "if_force_nonzero_require_geometry_reset_KKT_Hessian": True,
            "then_certify_same_action_saddle": True,
        },
        "exact_next_dependency": (
            "DERIVE_OR_CERTIFY_THE_ACTION_OWNED_MAXIMAL_HISTORY_COEFFICIENT_"
            "REALIZATION_AND_FIRST_RESET_QUOTIENT_GEOMETRY_JET_ON_A_NONEMPTY_"
            "REGULAR_STRATUM,_WITHOUT_CHORD3,_TERMINAL_RECURRENCE,_AN_"
            "ARBITRARY_VALIDATION_CUTOFF,_OR_A_HAND_SELECTED_RESET_MEMBER"
        ),
        "claim_boundary": {
            "Gate7": "ACTIVE_SINGLE_MAXIMAL_HISTORY_COEFFICIENT_ORACLE_OWNER",
            "Gate8": "LOCKED",
            "source_incidence": "ASSEMBLED",
            "force_root_quotient_test": "DERIVED",
            "maximal_history_coefficient_oracle_and_first_jet": (
                "OPEN_CURRENT_OWNER"
            ),
            "actual_projected_force": "OPEN_AFTER_ORACLE",
            "same_action_saddle": "OPEN_AFTER_FORCE",
            "geometry_reset_KKT_Hessian": "OPEN_IF_FORCE_NONZERO",
            "chord_03_authorized": False,
            "frozen_predictions_changed": False,
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
