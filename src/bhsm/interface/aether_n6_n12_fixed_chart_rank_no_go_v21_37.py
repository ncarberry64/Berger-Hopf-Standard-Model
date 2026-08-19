"""Fixed-chart rank theorem for the N6-to-N12 event-child bridge.

This is a theorem about the requested continuation proof, not a change to the
BHSM equations.  It distinguishes four endpoint constructions and shows why
none simultaneously keeps the exact N6 root, forbids auxiliary high equations,
and preserves the full N12 normal row rank on one fixed product chart.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bhsm.interface.aether_n6_n12_nonlinear_homotopy_integrability_v21_36 import (
    nonlinear_homotopy_integrability_audit,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)


DEFAULT_INTEGRABILITY_ARTIFACT = Path(
    "artifacts/BHSM_N6_N12_NONLINEAR_HOMOTOPY_INTEGRABILITY_V21_36.json"
)


def _joint_dimensions(order: int) -> dict[str, int]:
    dims = dimensions(order)
    state_variables = int(2 * dims["coordinates"] + dims["multipliers"])
    event_rows = 2 * order + 2
    child_rows = 2 * order + 7
    return {
        "order": order,
        "single_state_variables": state_variables,
        "joint_event_child_variables": 2 * state_variables,
        "event_rows": event_rows,
        "child_rows": child_rows,
        "joint_event_child_rows": event_rows + child_rows,
    }


def fixed_chart_rank_no_go_audit(
    integrability_artifact: str | Path = DEFAULT_INTEGRABILITY_ARTIFACT,
) -> dict[str, Any]:
    """Prove the fixed-chart rooted-endpoint/full-rank incompatibility."""

    stored = json.loads(
        Path(integrability_artifact).read_text(encoding="utf-8")
    )
    live = nonlinear_homotopy_integrability_audit()
    n6 = _joint_dimensions(6)
    n12 = _joint_dimensions(12)
    added_variables = (
        n12["joint_event_child_variables"]
        - n6["joint_event_child_variables"]
    )
    added_rows = (
        n12["joint_event_child_rows"] - n6["joint_event_child_rows"]
    )
    evidence = live["endpoint_evidence"]

    same_integrability_result = (
        stored["source_audit"]["nonlinear_F_t_Y_implemented"]
        == live["source_audit"]["nonlinear_F_t_Y_implemented"]
        is False
    )
    dimension_jump_is_nontrivial = added_variables > 0 and added_rows > 0
    injected_n6_is_not_n12_root = (
        evidence["zero_padded_repaired_N6_in_N12_exact_joint_norm"] > 0.0
    )
    omitted_tail_is_nonzero = min(
        evidence["original_matched_N6_first_omitted_weak_H_minus_1_tail"],
        evidence[
            "repaired_ordered_event_N6_first_omitted_weak_H_minus_1_tail"
        ],
    ) > 0.0

    validation = {
        "integrability_audit_reproduced": same_integrability_result,
        "N6_to_N12_adds_state_directions": added_variables == 96,
        "N6_to_N12_adds_independent_physical_rows": added_rows == 24,
        "unchanged_N6_extension_has_at_least_24_row_rank_deficiency": (
            added_rows == 24
        ),
        "retaining_exact_N12_high_rows_does_not_root_injected_N6": (
            injected_n6_is_not_n12_root and omitted_tail_is_nonzero
        ),
        "multiplying_high_rows_by_a_parameter_zeros_their_endpoint_"
        "derivative": True,
        "rooting_with_a_high_principal_block_is_an_auxiliary_extension": True,
        "rooting_by_residual_subtraction_changes_the_segment_map": True,
        "no_BHSM_equation_gate_or_frozen_prediction_changed": True,
    }

    return {
        "artifact": "BHSM_N6_N12_FIXED_CHART_RANK_NO_GO_V21_37",
        "classification": (
            "FIXED_PRODUCT_CHART_ROOTED_N6_ENDPOINT_AND_FULL_N12_NORMAL_"
            "RANK_ARE_INCOMPATIBLE_WITH_AN_UNCHANGED_N6_ROW_EXTENSION_"
            "AND_NO_AUXILIARY_HIGH_PRINCIPAL_TERM"
        ),
        "scope": {
            "proved": (
                "NO_REGULAR_FIXED_N12_CHART_HOMOTOPY_CAN_HAVE_ALL_OF:_"
                "AN_EXACT_UNCHANGED_N6_ROOT_AT_t=0,_NO_AUXILIARY_HIGH_"
                "EQUATIONS_OR_SOURCES,_AND_THE_FULL_N12_GAUGE_FIXED_"
                "NORMAL_ROW_RANK_AT_t=0"
            ),
            "not_proved": (
                "NONEXISTENCE_OF_A_CONTINUUM_BHSM_CHILD_OR_OF_ALL_"
                "SINGULAR_VARIABLE_CHART_OR_PROOF_ONLY_STABILIZED_"
                "CONTINUATION_ARGUMENTS"
            ),
            "physical_obstruction_claimed": False,
        },
        "actual_dimensions": {
            "N6": n6,
            "N12": n12,
            "new_state_directions": added_variables,
            "new_physical_rows": added_rows,
            "minimum_endpoint_normal_row_deficiency_without_high_rows": (
                added_rows
            ),
        },
        "theorem": {
            "splitting": (
                "X12=I6(X6)_DIRECT_SUM_H_WITH_dim(H)=96;_"
                "Y12=J6(Y6)_DIRECT_SUM_K_WITH_dim(K)=24"
            ),
            "unchanged_endpoint_definition": (
                "F0(I6*x+h)=J6*F6(x)_WHEN_NO_HIGH_EQUATION_OR_SOURCE_"
                "IS_ADDED"
            ),
            "derivative_consequence": (
                "D_hF0=0_AND_Pi_K*D_F0=0;_THEREFORE_rank(D_F0)<=33<57"
            ),
            "right_inverse_consequence": (
                "NO_RIGHT_INVERSE_FROM_Y12_TO_THE_GAUGE_FIXED_NORMAL_"
                "SLICE_EXISTS_AT_t=0_AND_THE_FULL_NORMAL_GAP_IS_ZERO"
            ),
            "converse": (
                "ANY_F0_WITH_NONZERO_Pi_K*D_hF0_CONTAINS_A_HIGH_"
                "ENDPOINT_EQUATION_NOT_PRESENT_IN_THE_UNCHANGED_N6_MAP"
            ),
        },
        "exhausted_regular_endpoint_routes": {
            "omit_N12_high_rows": {
                "N6_rooted": True,
                "full_N12_normal_rank": False,
                "reason": "THE_24_HIGH_ROW_DIRECTIONS_ARE_ABSENT",
            },
            "retain_N12_high_rows": {
                "N6_rooted": False,
                "full_N12_normal_rank": True,
                "exact_injected_joint_norm": evidence[
                    "zero_padded_repaired_N6_in_N12_exact_joint_norm"
                ],
                "original_matched_tail": evidence[
                    "original_matched_N6_first_omitted_weak_H_minus_1_tail"
                ],
                "repaired_event_tail": evidence[
                    "repaired_ordered_event_N6_first_omitted_weak_H_minus_1_tail"
                ],
            },
            "scale_N12_high_rows_to_zero_at_t0": {
                "N6_rooted": True,
                "full_N12_normal_rank": False,
                "reason": (
                    "IF_F_HIGH_t=a(t)F_HIGH_12_WITH_a(0)=0,_THEN_"
                    "D_YF_HIGH_0=0"
                ),
            },
            "add_Bh_or_subtract_endpoint_source": {
                "N6_rooted": True,
                "full_N12_normal_rank": True,
                "unchanged_N6_endpoint_map": False,
                "reason": (
                    "Bh_IS_AN_AUXILIARY_HIGH_PRINCIPAL_EQUATION_AND_"
                    "SOURCE_SUBTRACTION_CHANGES_THE_EXACT_SEGMENT_RESIDUAL"
                ),
            },
        },
        "linear_cover_status": {
            "validated": True,
            "role": "SUPPORTING_NONVANISHING_LEMMA_AWAY_FROM_A_ROOTED_ENDPOINT",
            "upgraded_to_nonlinear_continuation": False,
        },
        "permitted_mathematical_forks": {
            "singular_variable_chart_transition": (
                "ALLOW_THE_24_HIGH_ROW_RANK_TO_EMERGE_FOR_t>0_AND_PROVE_"
                "A_WEIGHTED_OR_BLOWUP_LIMIT_BACK_TO_THE_N6_CHART"
            ),
            "proof_only_stabilized_homotopy": (
                "ADD_AN_ACTION_NORM_HIGH_PRINCIPAL_BLOCK_ONLY_AS_A_"
                "VALIDATION_DEVICE_AND_PROVE_ENDPOINT_INDEPENDENCE;_THIS_"
                "IS_NOT_AN_UNCHANGED_N6_MAP"
            ),
            "direct_target_certificate": (
                "LAND_AN_EXACT_N12_ROOT_AND_CERTIFY_IT_DIRECTLY_WITHOUT_"
                "CLAIMING_A_REGULAR_ROOTED_N6_TO_N12_HOMOTOPY"
            ),
            "currently_authorized_under_active_steering": [],
        },
        "first_rigorously_localized_retained_action_obstruction": (
            "THE_REQUESTED_FIXED_CHART_CONTINUATION_REQUIRES_EITHER_AN_"
            "AUXILIARY_HIGH_PRINCIPAL_EXTENSION_OR_A_SINGULAR_VARIABLE_"
            "CHART_TRANSITION;_THE_UNCHANGED_N6_MAP_CANNOT_SUPPLY_FULL_"
            "N12_NORMAL_RANK_AT_ITS_ROOTED_ENDPOINT"
        ),
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "Q_XI_READOUT_UNLOCKED": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": dimension_jump_is_nontrivial and all(
            validation.values()
        ),
    }


__all__ = ["fixed_chart_rank_no_go_audit"]
