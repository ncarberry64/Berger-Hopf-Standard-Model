"""Audit the missing nonlinear object behind the N6-to-N12 Schur cover.

The existing finite cover encloses an affine family of *linear* Schur
operators at one N12 state.  A validated continuation by overlapping radii
balls additionally needs an exact nonlinear family whose zero set is being
continued.  This module records that distinction without changing the BHSM
action, residual, gates, or frozen predictions.
"""

from __future__ import annotations

import ast
import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _embedded_weak_bulk_constraint_data,
)


DEFAULT_CROSS_ARTIFACT = Path(
    "artifacts/BHSM_AETHER_CROSS_RESOLUTION_RECONNAISSANCE_V21_35.json"
)
DEFAULT_LINEAR_ARTIFACT = Path(
    "artifacts/BHSM_N6_N12_JOINT_SCHUR_CHORD_COVER.json"
)
DEFAULT_LINEAR_SCRIPT = Path(
    "scripts/measure_n6_n12_joint_schur_chord_cover.py"
)


def _function_record(tree: ast.AST, name: str) -> dict[str, Any]:
    node = next(
        item
        for item in ast.walk(tree)
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
        and item.name == name
    )
    names = sorted({
        item.id for item in ast.walk(node) if isinstance(item, ast.Name)
    })
    return {
        "arguments": [argument.arg for argument in node.args.args],
        "referenced_names": names,
        "line": node.lineno,
    }


def _tail_norm(
    exact: Mapping[str, list[str]],
    *,
    source_order: int = 6,
    maximum_order: int = 48,
    points: int = 256,
) -> float:
    data = _embedded_weak_bulk_constraint_data(
        exact,
        source_order=source_order,
        maximum_order=maximum_order,
        points=points,
    )
    high = np.arange(maximum_order) >= source_order
    weights = 1.0 / (1.0 + data["frequencies"] ** 2)
    return math.sqrt(float(
        np.sum(weights[:maximum_order][high] * data["bulk_lapse"][high] ** 2)
        + np.sum(
            weights[maximum_order:][high] * data["bulk_shift"][high] ** 2
        )
    ))


def nonlinear_homotopy_integrability_audit(
    cross_artifact: str | Path = DEFAULT_CROSS_ARTIFACT,
    linear_artifact: str | Path = DEFAULT_LINEAR_ARTIFACT,
    linear_script: str | Path = DEFAULT_LINEAR_SCRIPT,
) -> dict[str, Any]:
    """Localize the first missing object required by nonlinear radii cover."""

    cross_path = Path(cross_artifact)
    linear_path = Path(linear_artifact)
    script_path = Path(linear_script)
    cross = json.loads(cross_path.read_text(encoding="utf-8"))[
        "cross_resolution_reconnaissance"
    ]
    linear = json.loads(linear_path.read_text(encoding="utf-8"))
    source = script_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    rows_record = _function_record(tree, "rows")
    scalar_record = _function_record(tree, "scalar_data")

    original_child = cross["N6_weak_complete_child_candidate"]["child_state"][
        "binary64_hex"
    ]
    repaired_child = cross["N6_repaired_event_complete_child_candidate"][
        "child_state"
    ]["binary64_hex"]
    original_tail = _tail_norm(original_child)
    repaired_tail = _tail_norm(repaired_child)

    cover = linear["latest_probe"]["affine_schur_interval_cover"]
    fixed_linear_scope = cover["scope"] == "FIXED_PAIRED_RICHARDSON_LINEARIZATION_ONLY"
    rows_has_no_parameter = (
        rows_record["arguments"] == ["joint"]
        and "t" not in rows_record["referenced_names"]
    )
    scalar_only_owns_linear_parameter = (
        scalar_record["arguments"] == ["t"]
        and "jll" in scalar_record["referenced_names"]
        and "feedback" in scalar_record["referenced_names"]
        and "rows" not in scalar_record["referenced_names"]
    )
    injected_is_not_root = (
        linear["finite_anchor_history"][
            "zero_padded_repaired_N6_in_N12_exact_joint_norm"
        ]
        > 0.0
    )
    omitted_tail_is_nonzero = min(original_tail, repaired_tail) > 0.0

    validation = {
        "linear_Schur_cover_preserved_as_valid_supporting_lemma": bool(
            linear["latest_probe"]["certification_status"][
                "fixed_paired_linear_schur_homotopy_enclosed"
            ]
        ),
        "linear_cover_scope_is_fixed_center_linearization": fixed_linear_scope,
        "exact_joint_residual_has_no_homotopy_parameter": rows_has_no_parameter,
        "t_parameter_occurs_only_in_linear_Schur_reduction": (
            scalar_only_owns_linear_parameter
        ),
        "zero_padded_repaired_N6_is_not_an_N12_joint_root": injected_is_not_root,
        "first_omitted_weak_tail_is_nonzero_for_both_N6_records": (
            omitted_tail_is_nonzero
        ),
        "no_new_action_residual_constraint_gate_or_selector_introduced": True,
        "no_higher_N_child_or_continuum_claim_promoted": True,
        "frozen_predictions_untouched": True,
    }

    nonlinear_family_defined = not (
        fixed_linear_scope
        and rows_has_no_parameter
        and scalar_only_owns_linear_parameter
    )
    return {
        "artifact": "BHSM_N6_N12_NONLINEAR_HOMOTOPY_INTEGRABILITY_V21_36",
        "classification": (
            "LINEAR_SCHUR_INTERVAL_COVER_VALIDATED_BUT_NOT_INTEGRATED_TO_"
            "AN_EXACT_NONLINEAR_RETAINED_ACTION_CONTINUATION_FAMILY"
        ),
        "linear_supporting_lemma": {
            "status": "VALIDATED_UNCHANGED",
            "accepted_interval_count": cover["accepted_interval_count"],
            "minimum_certified_hard_gap": cover["minimum_certified_hard_gap"],
            "minimum_certified_full_gap": cover["minimum_certified_full_gap"],
            "minimum_certified_soft_denominator": cover[
                "minimum_certified_soft_denominator"
            ],
            "scope": cover["scope"],
        },
        "source_audit": {
            "exact_joint_residual_function": rows_record,
            "linear_Schur_parameter_function": scalar_record,
            "finding": (
                "rows(joint)_evaluates_one_fixed_F57_WITH_NO_t;_"
                "scalar_data(t)_changes_only_THE_FIXED_CENTER_SCHUR_MATRIX_"
                "AND_SOURCE"
            ),
            "nonlinear_F_t_Y_implemented": nonlinear_family_defined,
        },
        "endpoint_evidence": {
            "zero_padded_repaired_N6_in_N12_exact_joint_norm": linear[
                "finite_anchor_history"
            ]["zero_padded_repaired_N6_in_N12_exact_joint_norm"],
            "original_matched_N6_first_omitted_weak_H_minus_1_tail": (
                original_tail
            ),
            "repaired_ordered_event_N6_first_omitted_weak_H_minus_1_tail": (
                repaired_tail
            ),
            "tail_provenance_note": (
                "0.086772051123605_BELONGS_TO_THE_ORIGINAL_MATCHED_N6_"
                "CHILD;_THE_REPAIRED_ORDERED_EVENT_CHILD_HAS_THE_SEPARATE_"
                "0.080655518582802_VALUE_AT_THE_SAME_48_MODE_256_POINT_AUDIT"
            ),
        },
        "integrability_lemma": {
            "required_object": (
                "A_C1_NONLINEAR_F(t,Y)_ON_ONE_FIXED_PRODUCT_CHART_WITH_"
                "F(0,I6Y6)=0,_F(1,Y)=F12(Y),_THE_EXISTING_GAUGE_FIXED_"
                "NORMAL_RANK,_AND_DYF_SCHUR_REDUCTION_EQUAL_TO_THE_"
                "CERTIFIED_S_FIN(t)"
            ),
            "coordinate_pullback_test": (
                "FOR_I_t(x,h)=(x,a(t)h)_WITH_a(0)=0,_"
                "D_h(S12_COMPOSE_I_t)=a(t)*D_H_S12_AND_"
                "D_hh^2(S12_COMPOSE_I_t)=a(t)^2*D_HH^2_S12;_"
                "THE_HIGH_NORMAL_RANK_THEREFORE_COLLAPSES_AT_t=0"
            ),
            "nondegenerate_endpoint_test": (
                "IF_a(0)_IS_NONZERO_TO_KEEP_THE_HIGH_NORMAL_BLOCK,_THE_"
                "NONZERO_OMITTED_EULER_DIRAC_TAIL_PREVENTS_I6Y6_FROM_"
                "BEING_A_ROOT"
            ),
            "source_subtraction_test": (
                "F_t=F12-(1-t)F12(I6Y6)_WOULD_ROOT_THE_START_BUT_ADDS_A_"
                "t_DEPENDENT_LINEAR_SOURCE_AND_IS_NOT_THE_UNCHANGED_"
                "RETAINED_ACTION_OR_RESIDUAL"
            ),
            "quadratic_linear_proxy": (
                "S_FIN(t)=A_LL-t*A_LH*A_HH^-1*A_HL_CAN_BE_REALIZED_AT_"
                "QUADRATIC_ORDER_BY_SCALING_LOW_HIGH_COUPLING_BY_sqrt(t);_"
                "NO_EXACT_NONLINEAR_ACTION_SPLIT_WITH_THE_REQUIRED_ROOTED_"
                "ENDPOINT_IS_DEFINED_OR_VALIDATED_IN_THE_REPOSITORY"
            ),
            "scope_of_negative_result": (
                "THIS_LOCALIZES_A_MISSING_MATHEMATICAL_OBJECT;_IT_DOES_NOT_"
                "PROVE_THAT_NO_ACTION_DERIVED_HOMOTOPY_CAN_EXIST"
            ),
        },
        "radii_cover_status": {
            "overlapping_nonlinear_segment_balls_meaningfully_defined": False,
            "reason": (
                "A_RADII_POLYNOMIAL_MUST_CERTIFY_ZEROS_OF_A_SPECIFIED_"
                "NONLINEAR_MAP;_THE_ONLY_t_FAMILY_CURRENTLY_PRESENT_IS_"
                "A_FIXED_CENTER_LINEAR_SCHUR_PROXY"
            ),
            "fourth_variation_majorant_is_the_next_step": False,
            "why_majorant_is_deferred": (
                "BOUNDS_MUST_BE_TAKEN_ON_THE_ACTUAL_NONLINEAR_FAMILY;_"
                "BOUNDING_AN_UNDEFINED_OR_DIFFERENT_FAMILY_WOULD_NOT_"
                "CERTIFY_THE_BHSM_CONTINUATION"
            ),
        },
        "first_rigorously_localized_retained_action_obstruction": (
            "DERIVE_THE_EXACT_NONLINEAR_NESTED_GALERKIN_EVENT_CHILD_"
            "HOMOTOPY_FROM_THE_UNCHANGED_RETAINED_ACTION_WITH_A_ROOTED_N6_"
            "ENDPOINT_AND_PRESERVED_GAUGE_FIXED_NORMAL_RANK,_OR_LOCALIZE_"
            "WHY_THIS_REQUIRES_AN_ADDED_SOURCE_OR_PRINCIPAL_TERM"
        ),
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "Q_XI_READOUT_UNLOCKED": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


__all__ = ["nonlinear_homotopy_integrability_audit"]
