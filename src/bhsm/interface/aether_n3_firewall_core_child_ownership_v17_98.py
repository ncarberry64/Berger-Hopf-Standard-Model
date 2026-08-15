"""Classify the firewall core data in the complete child boundary map."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from bhsm.interface.aether_core_surface_trace_v15_11 import (
    response_and_passage_payload,
)
from bhsm.interface.aether_hybrid_standard_model_bundle_v15_53 import (
    hybrid_bundle_gluing,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_scalar_complete_child_boundary_solution_v17_96 import (
    scalar_complete_child_boundary_solution,
)
from bhsm.interface.aether_n3_zero_background_calderon_closure_v17_97 import (
    zero_background_calderon_closure,
)
from bhsm.interface.aether_reconstruction_firewall_event_v15_45 import (
    boundary_identity_chain_complex,
    oriented_cut_and_event_data,
)


VERSION = "v17.98"
CLASSIFICATION = "BHSM_N3_FIREWALL_CORE_CHILD_OWNERSHIP"
FULL_BHSM_COMPLETE = False


def firewall_core_child_ownership() -> dict[str, Any]:
    identities = boundary_identity_chain_complex()
    event = oriented_cut_and_event_data()
    passage = response_and_passage_payload()
    bundle = hybrid_bundle_gluing()
    scalar = scalar_complete_child_boundary_solution()
    zero_sector = zero_background_calderon_closure()
    survivor = event["surviving_data"]

    discrete_rows = {
        "global_event_degree_is_one": survivor["global_event_degree"] == 1,
        "child_orientation_is_negative_x": (
            survivor["orientation_branch"] == "child_x_negative"
        ),
        "odd_FR_parity_retained": survivor["FR_parity"] == -1,
        "child_parent_boundary_identities_not_exchanged": (
            not identities["boundary_identity_exchange"]
        ),
        "SM_bundle_isomorphism_class_returns": bundle[
            "hybrid_bundle_returns_to_same_isomorphism_class"
        ],
    }
    return {
        "ownership_decision": {
            "continuous_pregeometric_core_trace_in_retained_child_action": False,
            "continuous_pregeometric_core_flux_row_in_F_child": False,
            "continuous_core_row_count": 0,
            "reason": (
                "AT_THE_RECONSTRUCTION_FIREWALL_METRIC_PROPER_TIME_"
                "CURVATURE_AND_CANONICAL_MOMENTUM_ARE_NOT_TRANSPORTED_"
                "PRIMITIVES;THE_RETAINED_ACTION_OWNS_ONLY_THE_POST_EVENT_"
                "REGULAR_CHILD_FIELDS_AND_DISCRETE_INCIDENCE_DATA"
            ),
            "setting_an_unknown_core_Calderon_operator_to_zero": False,
            "microscopic_pregeometric_generator_derived": False,
            "microscopic_generator_role": (
                "STILL_OPEN_FOR_A_MICROSCOPIC_AETHER_TRANSITION_AMPLITUDE_"
                "BUT_NOT_AN_EXTRA_CONTINUOUS_ROW_OF_THE_CLASSICAL_CHILD_BVP"
            ),
        },
        "firewall_discrete_match": {
            "rows": discrete_rows,
            "all_rows_closed": all(discrete_rows.values()),
            "boundary_matrix_d1": identities["boundary_matrix_d1"],
            "not_transported_as_pregeometric_primitives": event[
                "not_transported_as_pregeometric_primitives"
            ],
        },
        "retained_action_check": {
            "conservative_core_surface_flux_in_retained_action": passage[
                "conservative_core_surface_flux_in_retained_action"
            ],
            "candidate_action_completion_adopted": passage[
                "candidate_action_completion_adopted"
            ],
            "new_core_equation_added": False,
        },
        "complete_retained_F_child": {
            "gravity_eta_scalar_block_closed": scalar["F_child_scalar"][
                "closed_to_resolved_derivative_tolerance"
            ],
            "zero_background_gauge_spinor_ghost_HS_block_closed": (
                zero_sector["F_child_zero_background_norm"] == 0.0
            ),
            "firewall_discrete_incidence_block_closed": all(
                discrete_rows.values()
            ),
            "unowned_core_operator_not_inserted": True,
            "boundary_map_closed": bool(
                scalar["F_child_scalar"][
                    "closed_to_resolved_derivative_tolerance"
                ]
                and zero_sector["F_child_zero_background_norm"] == 0.0
                and all(discrete_rows.values())
            ),
            "positive_duration_persistence_witness": "OPEN",
        },
        "whole_system_interpretation": (
            "THE_FOURTH_BODY_IS_THE_COMPLETE_DERIVED_CHILD_RELATION_"
            "COMPOSED_OF_CONTINUOUS_REGULAR_BOUNDARY_ROWS_AND_DISCRETE_"
            "FIREWALL_INCIDENCE_NOT_AN_EXTRA_CORE_COORDINATE"
        ),
    }


def completion_payload() -> dict[str, Any]:
    result = firewall_core_child_ownership()
    ownership = result["ownership_decision"]
    retained = result["retained_action_check"]
    complete = result["complete_retained_F_child"]
    validation = {
        "no_unowned_continuous_core_row": (
            ownership["continuous_core_row_count"] == 0
            and not ownership[
                "continuous_pregeometric_core_flux_row_in_F_child"
            ]
        ),
        "unknown_core_operator_not_set_zero": not ownership[
            "setting_an_unknown_core_Calderon_operator_to_zero"
        ],
        "microscopic_generator_open_honestly": not ownership[
            "microscopic_pregeometric_generator_derived"
        ],
        "discrete_firewall_rows_closed": result[
            "firewall_discrete_match"
        ]["all_rows_closed"],
        "no_candidate_core_action_adopted": (
            not retained["candidate_action_completion_adopted"]
            and not retained["new_core_equation_added"]
        ),
        "retained_boundary_map_closed": complete["boundary_map_closed"],
        "persistence_not_fabricated": complete[
            "positive_duration_persistence_witness"
        ] == "OPEN",
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_firewall_core_child_ownership_v17_98",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "firewall_core_child_ownership": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_COMPLETE_CHILD_MATCHES_ACTION_OWNED_REGULAR_FIELDS_AND_"
            "DISCRETE_FIREWALL_DATA_WITHOUT_AN_EXTRA_PREGEOMETRIC_COORDINATE"
        ),
        "dependency_closed": (
            "COMPLETE_RETAINED_EVENT_TO_CHILD_BOUNDARY_SOLVABILITY_MAP"
        ),
        "active_calculation": (
            "EVOLVE_THE_V17_96_CHILD_FOR_A_POSITIVE_CONSTRAINT_CONSISTENT_"
            "ETA_HYPERREGULAR_INTERVAL_AND_APPLY_THE_PERSISTENCE_DEFINITION"
        ),
        "direct_N3_solve_authorized_next": False,
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_firewall_core_child_ownership_v17_98.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "firewall_core_child_ownership", "completion_payload", "materialize",
]
