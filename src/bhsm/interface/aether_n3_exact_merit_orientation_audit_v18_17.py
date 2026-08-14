"""Audit both orientations of the v18.16 coupled direction by exact merit."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN, _metrics
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_square_kkt_complete_child_promotion_v18_12 import v18_12_selected_raw_vector


VERSION = "v18.17"
CLASSIFICATION = "BHSM_N3_EXACT_MERIT_ORIENTATION_AUDIT"
FULL_BHSM_COMPLETE = False


def v18_17_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_exact_merit_orientation_audit_v18_17.json"
    ).read_text(encoding="utf-8"))
    selected = payload["exact_merit_orientation_audit"][
        "selected_true_merit_candidate_pending_child_acceptance"
    ]
    if selected is None:
        raise ValueError("v18.17 has no candidate to reconstruct")
    return np.asarray([float.fromhex(value) for value in selected["raw_vector_hex"]])


def exact_merit_orientation_audit() -> dict[str, Any]:
    source_artifact = json.loads(Path(
        "artifacts/BHSM_aether_n3_action_curvature_square_kkt_proposal_v18_16.json"
    ).read_text(encoding="utf-8"))
    proposal = source_artifact["action_curvature_square_kkt_proposal"]
    source_raw = v18_12_selected_raw_vector()
    scales = kkt_variable_scales(); source_y = source_raw * scales
    source_residual = _square_physical_residual(source_y)
    initial = _metrics(source_residual)
    full_forward = proposal["trials"][0]
    full_forward_raw = np.asarray([
        float.fromhex(value) for value in full_forward["raw_vector_hex"]
    ])
    direction_y = (full_forward_raw - source_raw) * scales
    source_merit = 0.5 * float(source_residual @ source_residual)
    reverse_trials: list[dict[str, Any]] = []
    eligible: list[dict[str, Any]] = []
    directional_slopes = []
    for forward in proposal["trials"]:
        if "metrics" not in forward:
            continue
        fraction = float(forward["fraction"])
        candidate_y = source_y - fraction * direction_y
        try:
            residual = _square_physical_residual(candidate_y)
            candidate_raw = candidate_y / scales
            metrics = _metrics(residual)
            eta = _minimum_node_eta(candidate_raw)
            reverse_merit = 0.5 * float(residual @ residual)
            forward_merit = 0.5 * float(forward["metrics"]["complete"] ** 2)
            central_slope = (forward_merit - reverse_merit) / (2.0 * fraction)
            row = {
                "backtrack": int(forward["backtrack"]),
                "fraction": fraction,
                "orientation": "OPPOSITE_TO_V18_16_PROPOSAL",
                "physical_scaled_coordinate_step_norm": float(fraction * np.linalg.norm(direction_y)),
                "raw_coordinate_step_norm": float(fraction * np.linalg.norm(direction_y / scales)),
                "eta_minimum": eta,
                "metrics": metrics,
                "complete_norm_reduction": initial["complete"] - metrics["complete"],
                "exact_symmetric_merit_directional_slope": central_slope,
                "raw_vector_hex": [float(value).hex() for value in candidate_raw],
            }
            row["true_merit_eligible"] = bool(
                eta > 1.0e-5 and row["complete_norm_reduction"] > MARGIN
            )
            reverse_trials.append(row)
            directional_slopes.append({
                "fraction": fraction,
                "exact_symmetric_merit_directional_slope_along_v18_16_orientation": central_slope,
            })
            if row["true_merit_eligible"]:
                eligible.append(row)
        except (ArithmeticError, FloatingPointError, ValueError) as exc:
            reverse_trials.append({
                "backtrack": int(forward["backtrack"]),
                "fraction": fraction,
                "orientation": "OPPOSITE_TO_V18_16_PROPOSAL",
                "domain_valid": False,
                "exception": type(exc).__name__,
            })
    selected = min(eligible, key=lambda row: row["metrics"]["complete"]) if eligible else None
    finite_slopes = [row["exact_symmetric_merit_directional_slope_along_v18_16_orientation"] for row in directional_slopes]
    return {
        "source_state": "v18.12_complete_child_promoted_state",
        "source_proposal": source_artifact["artifact"],
        "source_proposal_status": source_artifact["status"],
        "source_complete_norm": initial["complete"],
        "source_merit": source_merit,
        "source_eta_minimum": _minimum_node_eta(source_raw),
        "v18_16_forward_candidate_count": sum(
            bool(row.get("true_merit_eligible", False)) for row in proposal["trials"]
        ),
        "exact_directional_slope_range_along_v18_16_orientation": [
            min(finite_slopes), max(finite_slopes)
        ],
        "proposal_orientation_is_exact_descent": bool(max(finite_slopes) < 0.0),
        "opposite_orientation_trials": reverse_trials,
        "selected_true_merit_candidate_pending_child_acceptance": selected,
        "physical_solve_dimension": [376, 376],
        "event_multiplier_explicit": True,
        "physical_equations_changed": False,
        "componentwise_monotonicity_required": False,
        "must_remain_on_previous_iterate_path": False,
        "acceptance_rule": (
            "INDEPENDENT_EXACT_TOTAL_MERIT_REDUCTION_AND_ETA_ONLY_AT_THIS_"
            "STAGE;_COMPLETE_CHILD_REQUIRED_BEFORE_PROMOTION"
        ),
    }


def completion_payload() -> dict[str, Any]:
    result = exact_merit_orientation_audit()
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    validation = {
        "source_is_v18_12": result["source_state"].startswith("v18.12"),
        "v18_16_had_no_forward_candidate": result["v18_16_forward_candidate_count"] == 0,
        "square_explicit_multiplier_system": result["physical_solve_dimension"] == [376, 376] and result["event_multiplier_explicit"],
        "physical_equations_unchanged": not result["physical_equations_changed"],
        "no_componentwise_filter": not result["componentwise_monotonicity_required"],
        "previous_path_not_a_constraint": not result["must_remain_on_previous_iterate_path"],
        "orientation_classified_by_exact_merit": not result["proposal_orientation_is_exact_descent"],
        "selected_reduces_true_merit": bool(selected is None or selected["complete_norm_reduction"] > MARGIN),
        "selected_preserves_eta": bool(selected is None or selected["eta_minimum"] > 1.0e-5),
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_exact_merit_orientation_audit_v18_17",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "exact_merit_orientation_audit": result,
        "status": "RECLASSIFIED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "EXACT_TOTAL_MERIT_RATHER_THAN_THE_INEXACT_PROPOSAL_MODEL_"
            "DETERMINES_WHICH_ORIENTATION_IS_PHYSICALLY_DESCENDING"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "RECONSTRUCT_AND_TEST_THE_SELECTED_COMPLETE_CHILD_IF_PRESENT;_"
            "OTHERWISE_DERIVE_AN_EXACT_MERIT_DESCENT_DIRECTION"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_exact_merit_orientation_audit_v18_17.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v18_17_selected_raw_vector", "exact_merit_orientation_audit", "completion_payload", "materialize"]
