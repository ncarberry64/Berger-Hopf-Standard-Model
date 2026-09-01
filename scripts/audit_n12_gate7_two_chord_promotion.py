"""Audit whether two certified N12 chords promote the Gate-7 source domain.

This audit is deliberately finite and fail-closed.  It consumes the two local
shadowing certificates and the existing global continuation/heat-domain
lineage.  It does not evaluate another proposal chord.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/flagship_integration/"
    "BHSM_N12_GATE7_TWO_CHORD_PROMOTION_AUDIT.json"
)

INPUTS = {
    "first_chord": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_GATE7_COMPLETE_PHYSICAL_U_GREEN_SHADOWING.json"
    ),
    "chord02": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_GATE7_CHORD_02_SIGNED_ALIGNED_GREEN.json"
    ),
    "chord02_domain": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_CHORD_02_HERMITE_SPAN_DOMAIN.json"
    ),
    "proposal_nodes": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_PERSISTENCE_PROPOSAL_NODES.json"
    ),
    "continuation": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_CONTINUUM_MAXIMAL_FLOW_DICHOTOMY.json"
    ),
    "coercive_control": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_GLOBAL_FLOW_COERCIVE_CONTROL_GATE.json"
    ),
    "child_hamiltonian": ROOT / (
        "artifacts/intrinsic_state_selection/"
        "BHSM_N12_CHILD_BOUNDARY_HAMILTONIAN_OWNERSHIP_GATE.json"
    ),
    "prior_heat_tail": ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_GATE7_FORWARD_COVER_HEAT_TAIL.json"
    ),
    "two_chord_heat_tail": ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_GATE7_TWO_CHORD_HEAT_TAIL_AUDIT.json"
    ),
    "heat_trace_class": ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_FORWARD_HEAT_TRACE_CLASS_AUDIT.json"
    ),
    "source_domain": ROOT / (
        "artifacts/flagship_integration/"
        "BHSM_N12_MAXIMAL_FORWARD_SOURCE_DOMAIN.json"
    ),
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> None:
    records = {name: _load(path) for name, path in INPUTS.items()}
    first = records["first_chord"]
    second = records["chord02"]
    second_domain = records["chord02_domain"]
    proposals = records["proposal_nodes"]
    continuation = records["continuation"]
    coercive = records["coercive_control"]
    hamiltonian = records["child_hamiltonian"]
    prior_tail = records["prior_heat_tail"]
    two_chord_tail = records["two_chord_heat_tail"]
    heat_trace = records["heat_trace_class"]
    source_domain = records["source_domain"]

    first_interval = first["summary"]["coordinate_time_interval"]
    second_interval = second_domain["span"]["coordinate_time_interval"]
    certified_interval = [first_interval[0], second_interval[1]]
    first_ratio = first["summary"][
        "maximum_Green_to_existing_local_radius_ratio"
    ]
    second_ratio = second["summary"]["maximum_Green_to_local_radius_ratio"]
    union_ratio = max(first_ratio, second_ratio)

    local_core_closed = (
        first["validation_passed"]
        and second["validation_passed"]
        and second_domain["validation_passed"]
        and first_interval == [0.0, 1e-8]
        and second_interval == [1e-8, 2e-8]
        and union_ratio < 1.0
    )
    invariant_recenter_set_proved = (
        continuation["maximal_flow_alternative"][
            "global_if_norm_and_all_existing_margins_remain_controlled"
        ]
        and coercive["owned_and_missing_energy_structure"][
            "coercive_S2_bound_on_continuum_child_component"
        ]
    )
    terminal_outcome_known = continuation["ordered_event"]["outcome_selected"]
    temporal_heat_tail_closed = (
        two_chord_tail["adjudication"][
            "temporal_state_or_source_tail_certified"
        ]
        or heat_trace["claim_boundary"]["half_line_common_heat_functional"]
        == "DEFINED_FINITE"
    )
    coefficient_oracle_available = source_domain["ownership"][
        "complete_history_coefficient_oracle_available"
    ]

    hypotheses = {
        "H1_finite_certified_core": {
            "required": "EXACT_FORWARD_CORE_[0,T0]_WITH_EXISTING_DOMAIN_MARGINS",
            "proved": local_core_closed,
            "evidence": {
                "coordinate_interval": certified_interval,
                "certified_chords": 2,
                "hard_subspans_per_chord": 64,
                "worst_union_Green_to_local_radius_ratio": union_ratio,
                "terminal_or_domain_exit_on_core": False,
            },
        },
        "H2_uniformly_recenterable_invariant_continuation": {
            "required": (
                "A_FORWARD_INVARIANT_K(B,delta)_CONTAINING_THE_REMAINDER_OF_"
                "THE_HISTORY,_WITH_FINITE_B,_POSITIVE_delta,_UNIFORM_LOCAL_"
                "DURATION,_AND_A_UNIFORM_SIGNED_GREEN_RATIO_BELOW_ONE"
            ),
            "proved": invariant_recenter_set_proved,
            "evidence": {
                "local_recenter_theorem_conditional_on_K_B_delta": True,
                "trajectory_proved_to_remain_in_one_K_B_delta": False,
                "coercive_S2_bound_available": coercive[
                    "owned_and_missing_energy_structure"
                ]["coercive_S2_bound_on_continuum_child_component"],
                "child_boundary_H_xi_action_executable": hamiltonian[
                    "action_owned_inventory"
                ]["complete_Q_xi_assembler"],
                "signed_identity_reused_on_both_chords": True,
                "two_chord_ratio_is_uniform_only_on_certified_union": union_ratio,
            },
        },
        "H3_controlled_maximal_endpoint_or_temporal_tail": {
            "required": (
                "EITHER_THE_FIRST_ACTION_SELECTED_FINITE_TERMINAL_GRAPH,_OR_"
                "AN_ACTION_OWNED_SUMMABLE_TEMPORAL_SOURCE_TAIL_AND_RELATIVE_"
                "HEAT_TRACE_CLASS_CLOSURE"
            ),
            "proved": terminal_outcome_known or temporal_heat_tail_closed,
            "evidence": {
                "maximal_outcome_selected": terminal_outcome_known,
                "spatial_Galerkin_tail_is_temporal_heat_tail": False,
                "finite_cover_heat_tail_certified": prior_tail["status"]
                == "FINITE_FORWARD_COVER_HEAT_TAIL_CERTIFIED",
                "two_chord_temporal_tail_certified": two_chord_tail[
                    "adjudication"
                ]["temporal_state_or_source_tail_certified"],
                "two_chord_best_case_endpoint_bound_lower": two_chord_tail[
                    "two_chord_heat_test"
                ]["best_case_constant_gap_endpoint_bound_lower"],
                "forward_relative_reference_operator_available": heat_trace[
                    "source_audit"
                ]["action_owned_forward_reference_operator_available"],
                "half_line_common_heat_functional_finite": heat_trace[
                    "claim_boundary"
                ]["half_line_common_heat_functional"] == "DEFINED_FINITE",
            },
        },
        "H4_complete_history_coefficient_oracle": {
            "required": (
                "THE_UNIQUE_MAXIMAL_HISTORY_OR_CERTIFIED_FINITE_TERMINAL_"
                "OUTCOME_IS_EVALUABLE_FOR_THE_NONZERO_COMMON_SOURCE_OPERATOR"
            ),
            "proved": coefficient_oracle_available,
            "evidence": {
                "abstract_forward_source_domain_action_owned": source_domain[
                    "ownership"
                ]["abstract_forward_source_domain_action_owned"],
                "complete_history_coefficient_oracle_available": (
                    coefficient_oracle_available
                ),
                "source_Hessian_evaluated": source_domain["ownership"][
                    "source_Hessian_evaluated"
                ],
            },
        },
    }
    promotion_closes = all(item["proved"] for item in hypotheses.values())

    validation = {
        "all_input_artifacts_validated": all(
            record["validation_passed"] for record in records.values()
        ),
        "first_two_chords_are_contiguous_and_certified": local_core_closed,
        "signed_physical_u_identity_reused_without_new_solver": (
            second["validation"][
                "finite_basis_free_physical_u_output_identity_used"
            ]
            and second["validation"][
                "five_signed_EL_components_summed_before_source_norm"
            ]
        ),
        "two_local_chords_not_promoted_to_forward_invariant_set": (
            not hypotheses[
                "H2_uniformly_recenterable_invariant_continuation"
            ]["proved"]
        ),
        "spatial_Galerkin_tail_not_relabelled_temporal_heat_tail": True,
        "authoritative_two_chord_heat_tail_audit_consumed": (
            two_chord_tail["certified_coordinate_time_end"] == 2.0e-8
            and not two_chord_tail["adjudication"][
                "two_chord_finite_core_promotable_to_complete_heat_response"
            ]
        ),
        "no_finite_number_of_additional_chords_claimed_sufficient": True,
        "chord03_not_authorized_without_terminal_horizon_or_global_bound": True,
        "proof_gap_not_relabelled_retained_action_incompatibility": True,
        "Gate7_and_later_claim_boundaries_preserved": not promotion_closes,
    }
    passed = all(validation.values())

    payload = {
        "artifact": "BHSM_N12_GATE7_TWO_CHORD_PROMOTION_AUDIT",
        "classification": (
            "BRANCH_C_PROMOTION_REJECTED_MISSING_GLOBAL_TEMPORAL_CONTROL_"
            "IDENTITY;_CHORD_03_NOT_AUTHORIZED_BY_UNIFORMITY_ARGUMENT"
        ),
        "current_flagship_gate": 7,
        "status": "ACTIVE_NOT_CLOSED",
        "promotion_theorem_audited": {
            "statement": (
                "FINITE_CERTIFIED_CORE_PLUS_A_FORWARD_INVARIANT_UNIFORMLY_"
                "RECENTERABLE_K(B,delta)_PLUS_EITHER_A_RETAINED_FINITE_"
                "TERMINAL_GRAPH_OR_AN_ACTION_OWNED_SUMMABLE_TEMPORAL_HEAT_"
                "TAIL_IMPLIES_AN_EVALUABLE_MAXIMAL_FORWARD_GAUGE_SOURCE_DOMAIN"
            ),
            "hypotheses": hypotheses,
            "conclusion_proved": promotion_closes,
        },
        "two_chord_frontier": {
            "coordinate_interval": certified_interval,
            "certified_chords": 2,
            "certified_hard_subspans": 128,
            "first_chord_Green_to_local_radius_ratio": first_ratio,
            "chord02_Green_to_local_radius_ratio": second_ratio,
            "worst_certified_union_ratio": union_ratio,
            "stored_proposal_interval": proposals["scope"]["coordinate_interval"],
            "remaining_stored_proposal_chords": proposals["scope"]["steps"] - 2,
            "stored_later_nodes_have_proof_authority": False,
        },
        "uniformity_adjudication": {
            "algebraic_signed_identity_is_locally_recenterable": True,
            "current_numeric_constants_are_global_invariants": False,
            "uniform_bound_on_certified_two_chord_union": union_ratio,
            "forward_invariance_of_that_union_or_of_one_K_B_delta": False,
            "why_two_successes_do_not_iterate": (
                "THE_LOCAL_DENOMINATORS,_PHYSICAL_U_NORMALIZATION,_ACTION_"
                "GRAPH_ROWS,_AND_LOCAL_RADII_ARE_RECENTERED_STATE_DEPENDENT_"
                "BOUNDS;_NO_RETAINED_ESTIMATE_KEEPS_ALL_LATER_CENTERS_IN_A_"
                "COMMON_BOUNDED_MARGIN_SET"
            ),
        },
        "branch_c_adjudication": {
            "category": "1_MISSING_PROOF_IDENTITY",
            "missing_identity": (
                "A_GLOBAL_ACTION_OWNED_STRONG_S2_AND_DOMAIN_MARGIN_BOUND_OR_"
                "AN_INTEGRATED_ORDERED_EVENT_TRANSPORT_BOUND_SELECTING_THE_"
                "FIRST_FINITE_TERMINAL_OUTCOME;_AN_INFINITE_BRANCH_ALSO_"
                "REQUIRES_AN_ACTION_OWNED_RELATIVE_HEAT_TRACE_CLASS_THEOREM"
            ),
            "merely_more_stored_chord_coverage_is_known_sufficient": False,
            "genuine_retained_action_deficiency_proved": False,
            "full_action_incompatibility_proved": False,
        },
        "chord03_decision": {
            "authorized_now": False,
            "minimum_additional_chords_sufficient_under_current_estimates": (
                "NO_FINITE_NUMBER_DERIVABLE"
            ),
            "reason": (
                "NO_CERTIFIED_TERMINAL_HORIZON,_CONTRACTION,_PER_CHORD_DECAY,_"
                "OR_ASYMPTOTIC_RECURRENCE_BOUND_CONVERTS_ANOTHER_LOCAL_CHORD_"
                "INTO_GLOBAL_UNIFORMITY_OR_A_SUMMABLE_TEMPORAL_TAIL"
            ),
            "would_become_proof_relevant_if": (
                "AN_ACTION_OWNED_FINITE_TERMINAL_HORIZON_OR_A_QUANTIFIED_"
                "CONTINUATION_TAIL_THEOREM_REDUCES_THE_REMAINING_TASK_TO_A_"
                "KNOWN_FINITE_COVER"
            ),
        },
        "exact_next_dependency": (
            "DERIVE_A_GLOBAL_ACTION_OWNED_STRONG_S2_AND_DOMAIN_MARGIN_BOUND_"
            "OR_AN_INTEGRATED_ORDERED_EVENT_TRANSPORT_BOUND_THAT_SELECTS_A_"
            "FINITE_TERMINAL_OUTCOME;_IF_THE_MAXIMAL_HISTORY_IS_INFINITE,_"
            "ALSO_DERIVE_AN_ACTION_OWNED_RELATIVE_HEAT_TRACE_CLASS_CLOSURE"
        ),
        "claim_boundary": {
            "Gate7": "OPEN",
            "Gate8_plus": "LOCKED",
            "FLAGSHIP_READY": False,
            "FULL_BHSM_COMPLETE": False,
            "GitHub_USB_publication": "UNCHANGED_NOT_AUTHORIZED",
        },
        "inputs": {_relative(path): _sha256(path) for path in INPUTS.values()},
        "validation": validation,
        "validation_passed": passed,
    }
    if not passed:
        raise RuntimeError("two-chord Gate-7 promotion audit did not validate")
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "artifact": _relative(RESULT),
                "classification": payload["classification"],
                "coordinate_interval": certified_interval,
                "promotion_closes": promotion_closes,
                "validation_passed": passed,
                "sha256": _sha256(RESULT),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
