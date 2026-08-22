"""Localize the retained-action obstruction to global terminal reachability."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESET = ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_CONTINUUM_SINGULAR_HITTING_RESET_RELATION.json"
INITIAL = ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_CONTINUUM_CHILD_INITIAL_EVENT_SIDE.json"
LOCAL_NO_RETURN = ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_LOCAL_CONTINUUM_NO_EVENT_RETURN.json"
ENDPOINTS = ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_EXISTING_PERSISTENCE_EVENT_RETURN_AUDIT.json"
MAXIMAL = ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json"
COERCIVE = ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_GLOBAL_FLOW_COERCIVE_CONTROL_GATE.json"
REVERSAL = ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_ORDERED_EVENT_TIME_REVERSAL_OBSTRUCTION.json"
INVARIANT = ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_FORWARD_INVARIANT_HISTORY_EXISTENCE_GATE.json"
TIME_DOMAIN = ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_FORWARD_TIME_DOMAIN_ORIENTATION_AUDIT.json"
THEORY = ROOT / "theory/n12_forward_terminal_chart_reachability_gate.md"
RESULT = ROOT / "artifacts/intrinsic_state_selection/BHSM_N12_FORWARD_TERMINAL_CHART_REACHABILITY_GATE.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    inputs = (
        RESET, INITIAL, LOCAL_NO_RETURN, ENDPOINTS, MAXIMAL, COERCIVE,
        REVERSAL, INVARIANT, TIME_DOMAIN, THEORY,
    )
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing reachability inputs: " + ", ".join(missing))

    reset = _load(RESET)
    initial = _load(INITIAL)
    local = _load(LOCAL_NO_RETURN)
    endpoints = _load(ENDPOINTS)
    maximal = _load(MAXIMAL)
    coercive = _load(COERCIVE)
    reversal = _load(REVERSAL)
    invariant = _load(INVARIANT)
    time_domain = _load(TIME_DOMAIN)

    validation = {
        "local_continuum_terminal_hitting_is_certified": (
            reset["validation_passed"] is True
            and reset["one_sided_hitting_theorem"]["represented_boundary_role"]
            == "FORWARD_TERMINAL"
        ),
        "regular_reset_relation_is_certified": reset["reset_correspondence"][
            "regular_local_continuum_correspondence_proved"
        ] is True,
        "reset_is_not_a_single_valued_physical_selector": reset[
            "reset_correspondence"
        ]["single_valued_physical_reset_map_proved"] is False,
        "continuum_child_starts_on_positive_event_side": initial[
            "continuum_transfer"
        ]["sign"] == "POSITIVE",
        "first_analytic_interval_is_event_free": local["consequence"][
            "first_forward_return_inside_certified_local_interval"
        ] is False,
        "stored_endpoint_moves_away_from_event": endpoints["summary"][
            "final_endpoint_farther_from_zero_at_all_quadratures"
        ] is True,
        "stored_endpoint_is_not_global_nonreturn_proof": endpoints[
            "action_ownership_conclusion"
        ]["return_domain_proved_empty"] is False,
        "maximal_flow_outcome_is_not_selected": maximal["ordered_event"][
            "outcome_selected"
        ] is False,
        "constraint_reduced_energy_is_identically_zero": coercive[
            "owned_and_missing_energy_structure"
        ]["constraint_reduced_Legendre_energy_is_identically_zero"] is True,
        "unreduced_energy_is_noncoercive": coercive["validation"][
            "exact_unbounded_null_cone_direction_exists"
        ] is True,
        "compact_invariant_child_energy_shell_is_absent": coercive[
            "global_flow_consequence"
        ]["globalization_by_unreduced_energy_conservation_allowed"] is False,
        "global_one_sign_shortcut_is_invalid": reversal["event_transport"][
            "global_strict_sign_on_R_invariant_set_possible"
        ] is False,
        "formal_reflection_is_not_quotiented": reversal["involution"][
            "is_gauge"
        ] is False,
        "single_physical_time_orientation_is_already_fixed": time_domain[
            "admissible_clock_domain"
        ]["number_of_physical_time_orientations"] == 1,
        "reflection_is_not_a_competing_temporal_sector": time_domain[
            "formal_reflection_reclassification"
        ]["second_physical_temporal_orientation"] is False,
        "reachability_domain_remains_unproved": invariant["exact_return_domain"][
            "nonempty_proved"
        ] is False,
        "no_new_equation_gate_selector_parent_observable_or_numerical_campaign": True,
    }

    next_lemma = (
        "DERIVE_AN_ACTION_OWNED_COMPACT_FORWARD_TRAPPING_OR_COMPONENT_RESTRICTED_"
        "INTEGRATED_EVENT_TRANSPORT_ESTIMATE_ON_AT_LEAST_ONE_FORWARD_ORIENTED_"
        "COMPLETE_CHILD_COMPONENT_OR_CERTIFY_ITS_FIRST_EXISTING_PHYSICAL_DOMAIN_EXIT"
    )
    payload = {
        "artifact": "BHSM_N12_FORWARD_TERMINAL_CHART_REACHABILITY_GATE",
        "classification": (
            "FORWARD_TERMINAL_CHART_REACHABILITY_NOT_YET_PROVED;_FIRST_"
            "RETAINED_ACTION_GLOBAL_CONTROL_OBSTRUCTION_LOCALIZED"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in inputs
        },
        "closed_local_structure": {
            "continuum_terminal_hitting_law": True,
            "regular_set_valued_reset_relation": True,
            "initial_event_side": "POSITIVE",
            "first_analytic_interval_event_free": True,
            "maximal_flow_continuation_or_domain_exit_dichotomy": True,
        },
        "global_outcome": {
            "at_least_one_existing_forward_child_reaches_terminal_chart": False,
            "no_existing_forward_child_reaches_terminal_chart": False,
            "certified_physical_domain_exit": False,
            "outcome_selected": False,
        },
        "localized_obstruction": {
            "constraint_reduced_energy": "IDENTICALLY_ZERO",
            "unreduced_energy": "NONCOERCIVE_WITH_EXPLICIT_UNBOUNDED_ZERO_ENERGY_SEQUENCE",
            "complete_child_boundary_H_xi": "NOT_ACTION_EXECUTABLE_IN_CURRENT_REPOSITORY",
            "compact_invariant_child_shell": "ABSENT",
            "action_selected_reference_cycle": "ABSENT",
            "global_event_transport_sign_on_reflection_invariant_union": "IMPOSSIBLE",
            "component_restricted_integrated_event_transport_bound": "NOT_DERIVED",
            "interpretation": (
                "OBSTRUCTION_TO_THE_CURRENT_GLOBAL_PROOF_ROUTE_NOT_A_PROOF_"
                "THAT_THE_RETAINED_ACTION_HAS_NO_RETURNING_HISTORY"
            ),
        },
        "exact_next_mathematical_lemma": next_lemma,
        "claim_boundaries": {
            "trajectory_sampling_is_proof": False,
            "formal_reflection_quotiented": False,
            "single_reset_representative_action_selected": False,
            "matched_parent_Q_xi_or_Delta_H_unlocked": False,
            "observable_or_prediction_promoted": False,
            "FULL_BHSM_COMPLETE": False,
        },
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "classification": payload["classification"],
        "exact_next_mathematical_lemma": next_lemma,
        "result": str(RESULT.relative_to(ROOT)).replace("\\", "/"),
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
