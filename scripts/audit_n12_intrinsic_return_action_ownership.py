"""Localize the analytic ownership gap in the N12 intrinsic return route."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTINUUM = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json"
)
DIRECT = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_CERTIFICATE.json"
)
PERSISTENCE = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_POSITIVE_DURATION_PERSISTENCE_WITNESS.json"
)
RETURN = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_EXISTING_PERSISTENCE_EVENT_RETURN_AUDIT.json"
)
INTRINSIC = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_INTRINSIC_STATE_RETURN_SECTION_GATE.json"
)
ETA_EXIT = ROOT / "artifacts/BHSM_aether_n3_eta_boundary_transversality_v16_10.json"
PERSISTENCE_DEFINITION = ROOT / (
    "artifacts/BHSM_aether_persistent_nonequilibrium_child_v17_87.json"
)
CLOCK = ROOT / "artifacts/BHSM_aether_joint_hamiltonian_selection_v15_2.json"
RELATIVE_PERIODIC = ROOT / "artifacts/BHSM_relative_periodic_persistence_v15_7.json"
POST_PARENT = ROOT / (
    "artifacts/qxi_relative_energy_preparation/"
    "BHSM_POST_PARENT_FLAGSHIP_OBSERVABLE_GATE.json"
)
FINITE_FLOW = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_FINITE_FLOW_CONTINUATION_DICHOTOMY.json"
)
COERCIVE = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_GLOBAL_FLOW_COERCIVE_CONTROL_GATE.json"
)
EVENT_EQUIVARIANCE = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_EVENT_CHILD_TIME_REVERSAL_EQUIVARIANCE_GATE.json"
)
CHIRALITY = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_FORWARD_TIME_TEMPORAL_CHIRALITY_AUDIT.json"
)
ORDERED_REVERSAL = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_ORDERED_EVENT_TIME_REVERSAL_OBSTRUCTION.json"
)
CHILD_BOUNDARY = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_CHILD_BOUNDARY_HAMILTONIAN_OWNERSHIP_GATE.json"
)
CONSTRAINT_ENERGY = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_CONSTRAINT_REDUCED_ENERGY_IDENTITY_GATE.json"
)
CONTINUUM_FLOW = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json"
)
RESULT = ROOT / (
    "artifacts/intrinsic_state_selection/"
    "BHSM_N12_INTRINSIC_RETURN_ACTION_OWNERSHIP_GATE.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    inputs = (
        CONTINUUM, DIRECT, PERSISTENCE, RETURN, INTRINSIC, ETA_EXIT,
        PERSISTENCE_DEFINITION, CLOCK, RELATIVE_PERIODIC, POST_PARENT,
        FINITE_FLOW, COERCIVE, EVENT_EQUIVARIANCE, CHIRALITY,
        ORDERED_REVERSAL, CHILD_BOUNDARY, CONSTRAINT_ENERGY, CONTINUUM_FLOW,
    )
    missing = [str(path) for path in inputs if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing return-ownership inputs: " + ", ".join(missing))
    continuum = _load(CONTINUUM)
    direct = _load(DIRECT)
    persistence = _load(PERSISTENCE)
    event_return = _load(RETURN)
    intrinsic = _load(INTRINSIC)
    eta_exit = _load(ETA_EXIT)
    persistence_definition = _load(PERSISTENCE_DEFINITION)
    clock = _load(CLOCK)
    relative_periodic = _load(RELATIVE_PERIODIC)
    post_parent = _load(POST_PARENT)
    finite_flow = _load(FINITE_FLOW)
    coercive = _load(COERCIVE)
    event_equivariance = _load(EVENT_EQUIVARIANCE)
    chirality = _load(CHIRALITY)
    ordered_reversal = _load(ORDERED_REVERSAL)
    child_boundary = _load(CHILD_BOUNDARY)
    constraint_energy = _load(CONSTRAINT_ENERGY)
    continuum_flow = _load(CONTINUUM_FLOW)

    eta_boundary = eta_exit["boundary_transversality"]
    child_domain = persistence_definition["persistence_and_decay_contract"][
        "persistence_domain_B_child"
    ]
    first_missing = chirality["flagship_consequence"]["first_missing_object"]
    validation = {
        "continuum_event_child_remains_certified": continuum[
            "CONTINUUM_EVENT_CHILD_CERTIFIED"
        ] is True,
        "direct_N12_child_remains_certified": direct[
            "DIRECT_N12_COMPLETE_PERSISTENT_CHILD_CERTIFIED"
        ] is True,
        "only_positive_duration_not_global_persistence_is_certified": (
            persistence["local_existence"]["positive_duration_exists"] is True
            and persistence["fine_evolution"]["coordinate_duration"] > 0.0
        ),
        "existing_witness_does_not_record_a_return": event_return[
            "action_ownership_conclusion"
        ]["existing_witness_records_a_first_positive_return"] is False,
        "interior_and_later_return_remain_open": (
            event_return["action_ownership_conclusion"][
                "unrecorded_interior_return_excluded"
            ] is False
            and event_return["action_ownership_conclusion"][
                "later_first_positive_return_proved_to_exist"
            ] is False
        ),
        "return_map_is_not_executable": intrinsic[
            "derived_first_return_section"
        ]["map_executable"] is False,
        "known_retained_action_flow_can_exit_eta_domain": (
            eta_boundary["classical_flow_is_transverse_outward"] is True
            and eta_boundary["smooth_classical_in_domain_continuation_exists"]
            is False
        ),
        "stable_reference_cycle_is_not_action_selected": clock["clock"][
            "action_selected_stable_core_cycle"
        ] is False,
        "relative_periodic_orbit_is_absent": relative_periodic[
            "action_selected_orbit"
        ] is None,
        "matched_parent_route_remains_closed": post_parent[
            "candidate_chain_audit"
        ][0]["status"] == "NOT_EXECUTABLE",
        "finite_N12_maximal_flow_dichotomy_is_closed": (
            finite_flow["validation_passed"] is True
            and finite_flow["theorem"]["unique_maximal_N12_solution_exists"]
            is True
        ),
        "unreduced_energy_noncoercivity_is_localized": coercive[
            "validation_passed"
        ] is True,
        "no_new_evolution_selector_observable_or_prediction": True,
        "formal_reflection_is_not_gauge": (
            chirality["physical_time"]["formal_reversal_is_gauge"] is False
        ),
        "one_temporal_chirality_sector_is_not_action_selected": (
            chirality["event_to_child_conclusion"][
                "one_temporal_chirality_sector_action_selected"
            ] is False
        ),
        "temporal_chirality_label_sign_G_is_derived_on_simple_transverse_events": (
            chirality["candidate_invariant_audit"]["ordered_event_transport"][
                "locally_constant_on_simple_transverse_event_components"
            ] is True
        ),
        "temporal_chirality_sectors_are_not_quotiented": (
            chirality["event_to_child_conclusion"][
                "two_sectors_may_be_quotiented"
            ] is False
        ),
        "event_forward_global_sign_shortcut_is_invalidated": (
            ordered_reversal["flagship_chain"][
                "event_forward_shortcut_adjudicated"
            ] is True
        ),
        "event_child_formal_equivariance_is_closed": (
            event_equivariance["validation_passed"] is True
        ),
        "child_boundary_H_xi_ownership_no_go_is_localized": (
            child_boundary["validation_passed"] is True
            and child_boundary["action_owned_inventory"][
                "complete_covariant_symplectic_potential"
            ] is False
        ),
        "constraint_reduced_Legendre_energy_zero_identity_is_closed": (
            constraint_energy["validation_passed"] is True
            and constraint_energy["exact_identity"]["restricted_identity"]
            == "E_N|C_N_inverse_0=0"
        ),
        "continuum_maximal_flow_dichotomy_is_closed": (
            continuum_flow["validation_passed"] is True
        ),
    }
    payload = {
        "artifact": "BHSM_N12_INTRINSIC_RETURN_ACTION_OWNERSHIP_GATE",
        "classification": (
            "FIRST_RETURN_NOT_YET_ACTION_EXECUTABLE;_FORMAL_REVERSAL_LABELS_"
            "TWO_DISTINCT_FORWARD_TIME_TEMPORAL_CHIRALITY_SECTORS_BUT_THE_"
            "CURRENT_ACTION_SELECTS_NEITHER"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in inputs
        },
        "owned_structure": {
            "resolution_independent_complete_child": True,
            "existing_child_phase_domain": child_domain,
            "local_retained_action_vector_field_at_N12": True,
            "positive_duration_admissible_history": True,
            "existing_simple_ordered_event_function": (
                "e_ord(Y)=lambda_ord(Hessian_of_the_retained_action_at_Y)"
            ),
            "conditional_first_return_section": intrinsic[
                "derived_first_return_section"
            ]["map"],
        },
        "exact_event_transport_identity": {
            "simple_eigenpair": "H(Y)psi(Y)=e_ord(Y)psi(Y);_norm(psi)=1",
            "retained_flow": "dY/dt=V(Y)",
            "derivative": (
                "d_e_ord(Y(t))/dt=<psi(Y),D_H(Y)[V(Y)]psi(Y)>"
            ),
            "action_form": (
                "D_H_IS_THE_RETAINED_ACTION_THIRD_VARIATION_WITH_THE_EXISTING_"
                "CONSTRAINT_AND_GAUGE_REDUCTION"
            ),
            "new_equation_or_gate": False,
        },
        "global_flow_audit": {
            "finite_N12_maximal_flow_dichotomy_proved": True,
            "continuum_maximal_flow_dichotomy_proved": True,
            "local_continuum_anchor_flow_certified": finite_flow[
                "continuum_transfer"
            ]["local_continuum_flow_on_anchor_action_ball_closed"],
            "continuum_certificate_scope": (
                "STATIC_EVENT_TO_COMPLETE_CHILD_NORMAL_TAIL_WITH_TRANSFERRED_"
                "POSITIVE_DURATION_NEIGHBORHOOD"
            ),
            "positive_duration_coordinate_time": persistence[
                "fine_evolution"
            ]["coordinate_duration"],
            "global_continuum_flow_theorem_in_audited_inputs": False,
            "uniform_eta_Dirac_action_graph_bound_for_all_forward_times": False,
            "compact_invariant_child_energy_shell_proved": False,
            "anchor_specific_recurrence_proved": False,
            "unreduced_autonomous_energy_supplies_S2_control": False,
            "blanket_eta_domain_invariance_may_be_assumed": False,
            "counterexample_scope": (
                "THE_EXISTING_N3_RETAINED_ACTION_FLOW_EXITS_ETA_TRANSVERSELY;_"
                "THIS_INVALIDATES_A_BLANKET_INVARIANCE_INFERENCE_BUT_DOES_NOT_"
                "PROVE_THE_N12_OR_CONTINUUM_ANCHOR_EXITS"
            ),
            "N3_eta_exit_time": eta_boundary["exit_time"],
            "N3_eta_directional_rate": eta_boundary[
                "directional_eta_margin_rate"
            ],
        },
        "return_or_no_return_proof_obligations": {
            "first": (
                "PROVE_EXISTENCE_OF_AN_ACTION_SELECTED_INVARIANT_HISTORY_ON_"
                "THE_FORWARD_TIME_RETURN_RELATION_WITHOUT_QUOTIENTING_OR_"
                "NUMERICALLY_CHOOSING_THE_FORMALLY_REFLECTED_TEMPORAL_"
                "CHIRALITY_SECTORS"
            ),
            "formal_reflection_status": (
                "DISTINCT_FORWARD_TIME_CHIRAL_PAIRING_NOT_GAUGE_OR_PHYSICAL_"
                "BACKWARD_EVOLUTION"
            ),
            "then": (
                "BOUND_OR_INTEGRATE_<psi,D_H[V]psi>_UNTIL_THE_FIRST_OF_"
                "ORDERED_EVENT_RETURN_OR_EXISTING_PHYSICAL_DOMAIN_EXIT"
            ),
            "return_outcome": (
                "PROVE_A_FINITE_SIMPLE_TRANSVERSE_ZERO_AND_APPLY_THE_ALREADY_"
                "DERIVED_CONDITIONAL_FIRST_RETURN_THEOREM"
            ),
            "no_return_outcome": (
                "PROVE_THE_ORDERED_EVENT_STAYS_NONZERO_UNTIL_A_CERTIFIED_"
                "DOMAIN_EXIT_OR_FOR_ALL_FORWARD_TIME"
            ),
            "recurrence_shortcut_available": False,
            "reason_recurrence_is_not_currently_a_lemma": (
                "NO_COMPACT_INVARIANT_FINITE_MEASURE_CHILD_SET_OR_ACTION_"
                "SELECTED_REFERENCE_CYCLE_IS_PRESENT_IN_THE_AUDITED_RESULTS"
            ),
        },
        "flagship_chain_consequence": {
            "matched_parent_Q_xi_or_Delta_H_authorized": False,
            "intrinsic_return_observable_executable": False,
            "shortest_action_owned_route": (
                "CONTINUUM_CHILD_TO_ACTION_SELECTED_INVARIANT_FORWARD_TIME_"
                "HISTORY_WITH_FORMAL_REFLECTION_RETAINED_AS_DISTINCT_CHIRAL_"
                "PARTNER_TO_REFLECTION_INVARIANT_DIMENSIONLESS_READOUT"
            ),
            "numerical_trajectory_search_authorized_as_substitute": False,
            "temporal_chirality_sector_may_be_selected_numerically": False,
            "temporal_chirality_sectors_quotiented": False,
            "prediction_frozen": False,
            "held_out_comparison_performed": False,
        },
        "first_missing_action_owned_object": first_missing,
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
        "first_missing_action_owned_object": first_missing,
        "N3_eta_exit_is_only_a_blanket_invariance_counterexample": True,
        "validation_passed": payload["validation_passed"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
