"""Localize the first exact failure in forward invariant-history selection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INTRINSIC = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_INTRINSIC_STATE_RETURN_SECTION_GATE.json"
)
EVENT_RETURN = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_EXISTING_PERSISTENCE_EVENT_RETURN_AUDIT.json"
)
LOCAL_FLOW = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_LOCAL_CONTINUUM_GALERKIN_FLOW.json"
)
MAXIMAL_FLOW = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json"
)
CHIRALITY = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_FORWARD_TIME_TEMPORAL_CHIRALITY_AUDIT.json"
)
COERCIVE = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_GLOBAL_FLOW_COERCIVE_CONTROL_GATE.json"
)
CLOCK = ROOT / "artifacts/BHSM_aether_joint_hamiltonian_selection_v15_2.json"
RELATIVE_PERIODIC = ROOT / "artifacts/BHSM_relative_periodic_persistence_v15_7.json"
CONTINUUM = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json"
)
INITIAL_SIDE = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_CONTINUUM_CHILD_INITIAL_EVENT_SIDE.json"
)
THEORY = ROOT / "theory/n12_forward_invariant_history_existence_gate.md"
RESULT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_FORWARD_INVARIANT_HISTORY_EXISTENCE_GATE.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    inputs = (
        INTRINSIC, EVENT_RETURN, LOCAL_FLOW, MAXIMAL_FLOW, CHIRALITY,
        COERCIVE, CLOCK, RELATIVE_PERIODIC, CONTINUUM, INITIAL_SIDE, THEORY,
    )
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing invariant-history inputs: " + ", ".join(missing))

    intrinsic = _load(INTRINSIC)
    event_return = _load(EVENT_RETURN)
    local_flow = _load(LOCAL_FLOW)
    maximal_flow = _load(MAXIMAL_FLOW)
    chirality = _load(CHIRALITY)
    coercive = _load(COERCIVE)
    clock = _load(CLOCK)
    relative_periodic = _load(RELATIVE_PERIODIC)
    continuum = _load(CONTINUUM)
    initial_side = _load(INITIAL_SIDE)

    conclusion = event_return["action_ownership_conclusion"]
    validation = {
        "continuum_event_child_certified": (
            continuum["CONTINUUM_EVENT_CHILD_CERTIFIED"] is True
        ),
        "conditional_first_return_map_derived": (
            intrinsic["derived_first_return_section"][
                "conditional_regular_map_theorem"
            ].startswith("PROVED")
        ),
        "first_return_map_not_executable": (
            intrinsic["derived_first_return_section"]["map_executable"] is False
        ),
        "existing_history_records_no_return": (
            conclusion["existing_witness_records_a_first_positive_return"] is False
        ),
        "return_domain_neither_nonempty_nor_empty_is_proved": (
            conclusion["later_first_positive_return_proved_to_exist"] is False
            and conclusion["return_domain_proved_empty"] is False
        ),
        "local_continuum_flow_only": (
            local_flow["scientific_result"]["unique_local_continuum_retained_child_flow_exists"]
            is True
            and local_flow["scientific_result"]["global_continuation_or_return_proved"]
            is False
        ),
        "maximal_flow_selects_no_return_or_exit_outcome": (
            maximal_flow["ordered_event"]["outcome_selected"] is False
        ),
        "formal_reflection_not_used_as_forward_return": (
            chirality["physical_time"]["formal_reversal_is_gauge"] is False
            and chirality["physical_time"][
                "formal_reversal_is_backward_physical_evolution"
            ] is False
        ),
        "compact_coercive_energy_shell_absent": (
            coercive["owned_and_missing_energy_structure"][
                "coercive_S2_bound_on_continuum_child_component"
            ] is False
        ),
        "stable_reference_cycle_absent": (
            clock["clock"]["action_selected_stable_core_cycle"] is False
        ),
        "relative_periodic_orbit_absent": (
            relative_periodic["action_selected_orbit"] is None
        ),
        "no_new_equation_gate_parent_selector_or_numerical_campaign": True,
        "continuum_initial_child_side_certified_positive": (
            initial_side["validation_passed"] is True
            and initial_side["continuum_transfer"]["sign"] == "POSITIVE"
        ),
    }

    payload = {
        "artifact": "BHSM_N12_FORWARD_INVARIANT_HISTORY_EXISTENCE_GATE",
        "classification": (
            "FORWARD_FIRST_RETURN_DOMAIN_NONEMPTY_NOT_PROVED;_NO_ACTION_"
            "SELECTED_FIXED_PERIODIC_OR_RELATIVE_PERIODIC_CHILD_HISTORY_YET"
        ),
        "exact_return_domain": {
            "start": "C_INFINITY(E)_FOR_E_IN_THE_EXISTING_SIMPLE_ORDERED_EVENT_SECTION",
            "flow": "THE_EXISTING_FORWARD_RETAINED_CONTINUUM_EULER_DIRAC_FLOW",
            "required_history": (
                "REMAINS_IN_ETA_METRIC_LAPSE_INERTIA_GAUGE_TRACE_DIRAC_AND_"
                "CHILD_DOMAINS_UNTIL_A_FINITE_FIRST_POSITIVE_EVENT_ZERO"
            ),
            "required_landing": (
                "SIMPLE_TRANSVERSE_EVENT_INSIDE_THE_CERTIFIED_CONTINUUM_"
                "EVENT_TO_CHILD_CHART"
            ),
            "nonempty_proved": False,
            "empty_proved": False,
        },
        "forward_landing_chirality_lemma": {
            "hypotheses": "F(0)_NONZERO_AND_FINITE_FIRST_ZERO_TAU_IS_TRANSVERSE",
            "identity": "SIGN(D_T_F(TAU))=-SIGN(F(0))",
            "F": "F(t)=E_ORD(FLOW_t(C_INFINITY(E)))",
            "new_sign_gate": False,
            "N12_initial_child_side": "POSITIVE_AT_96_192_AND_384_POINT_QUADRATURE",
            "continuum_initial_child_side_independently_enclosed": True,
            "continuum_initial_child_event_value_lower": initial_side[
                "continuum_transfer"
            ]["continuum_initial_child_event_value_lower"],
            "formal_reflection_creates_a_forward_return": False,
        },
        "periodic_point_prerequisites": {
            "nonempty_return_domain": False,
            "return_into_certified_child_chart": False,
            "continuous_return_map_on_controlled_iterate_domain": False,
            "compact_trapping_set": False,
            "nonzero_return_degree_or_index": False,
            "action_selected_reference_cycle": False,
            "fixed_or_periodic_point_may_be_claimed": False,
        },
        "localized_failure": {
            "first_retained_action_failure": (
                "NONEMPTY_ADMISSIBLE_FORWARD_FIRST_RETURN_DOMAIN_NOT_ESTABLISHED"
            ),
            "no_return_or_no_orbit_proved": False,
            "exact_next_dependency": (
                "PROVE_THAT_AT_LEAST_ONE_EXISTING_COMPLETE_EVENT_HAS_A_FINITE_"
                "SIMPLE_TRANSVERSE_FIRST_FORWARD_RETURN_WHOSE_HISTORY_REMAINS_"
                "IN_THE_EXISTING_CONTINUUM_CHILD_DOMAIN_AND_LANDS_INSIDE_THE_"
                "CERTIFIED_EVENT_TO_CHILD_CHART_OR_PROVE_THAT_EVERY_SUCH_"
                "FORWARD_HISTORY_EXITS_OR_NEVER_RETURNS"
            ),
            "after_nonempty_return": (
                "PROVE_A_PERIODIC_POINT_BY_AN_ACTION_OWNED_COMPACT_TRAPPING_"
                "DEGREE_INDEX_OR_EQUIVALENT_EXISTENCE_MECHANISM"
            ),
        },
        "claim_boundaries": {
            "formal_reversal_quotiented": False,
            "parent_subtraction_fabricated": False,
            "trajectory_sampling_is_proof": False,
            "action_selected_state_or_observable_promoted": False,
            "prediction_frozen": False,
        },
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in inputs
        },
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "classification": payload["classification"],
        "first_retained_action_failure": payload["localized_failure"][
            "first_retained_action_failure"
        ],
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
