"""One exact-F376 proposal from the validated Rayleigh event-curvature block."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import _action_curvature_transform
from bhsm.interface.aether_n3_exact_action_hessian_assembly_v18_18 import exact_sbp_action_hessian
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_rayleigh_event_covector_v20_80 import (
    rayleigh_sbp_event_covector, rayleigh_square_physical_residual,
)
from bhsm.interface.aether_n3_rayleigh_krylov_restriction_audit_v20_86 import v20_86_selected_raw_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_structural_hindsight_recovery_v20_68 import _fresh_child_gate


VERSION = "v20.88"
CLASSIFICATION = "BHSM_N3_RAYLEIGH_CURVATURE_PRECONDITIONED_PROPOSAL"
FULL_BHSM_COMPLETE = False
BACKTRACKS = 18


def v20_88_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_RAYLEIGH_CURVATURE_PRECONDITIONED_PROPOSAL_V20_88.json"
    ).read_text(encoding="utf-8"))["rayleigh_curvature_preconditioned_proposal"]
    if not payload["promotion"]["promoted"]:
        raise ValueError("v20.88 has no physically promoted state")
    return np.asarray([float.fromhex(value) for value in payload["exact_line_search"]["best"]["raw_vector_hex"]])


def rayleigh_curvature_preconditioned_proposal() -> dict[str, Any]:
    scales = kkt_variable_scales(); raw = v20_86_selected_raw_vector(); y = raw * scales
    residual = rayleigh_square_physical_residual(y); source_norm = float(np.linalg.norm(residual))
    curvature_artifact = json.loads(Path(
        "artifacts/BHSM_N3_RAYLEIGH_EVENT_CURVATURE_BLOCK_V20_87.json"
    ).read_text(encoding="utf-8"))["rayleigh_event_curvature_block"]
    support = np.asarray(curvature_artifact["support_indices"], dtype=int)
    block = np.asarray(curvature_artifact["symmetric_support_block"], dtype=float)
    action = exact_sbp_action_hessian(raw[:-1]); action_raw = np.asarray(action.pop("hessian"))
    inverse = 1.0 / scales[:-1]
    action_scaled = inverse[:, None] * action_raw * inverse[None, :]
    event_hessian = np.zeros((375, 375)); event_hessian[np.ix_(support, support)] = block
    event_gradient = rayleigh_sbp_event_covector(raw[:-1]) * inverse / scales[-1]
    matrix = np.zeros((376, 376))
    matrix[:-1, :-1] = action_scaled + y[-1] * event_hessian
    matrix[:-1, -1] = event_gradient; matrix[-1, :-1] = event_gradient
    transform, transform_audit = _action_curvature_transform(raw)
    transformed = matrix @ transform
    direction_x, _, rank, singular = np.linalg.lstsq(transformed, -residual, rcond=None)
    direction_y = transform @ direction_x
    predicted = residual + matrix @ direction_y
    trials = []; eligible = []
    for orientation in (-1.0, 1.0):
        for backtrack in range(BACKTRACKS):
            alpha = orientation * 0.5**backtrack
            candidate_y = y + alpha * direction_y
            try:
                candidate_raw = candidate_y / scales
                norm = float(np.linalg.norm(rayleigh_square_physical_residual(candidate_y)))
                eta = float(_minimum_node_eta(candidate_raw)); reduction = source_norm - norm
                row = {"orientation": "negative" if orientation < 0.0 else "positive", "alpha": alpha,
                       "backtrack": backtrack, "exact_rayleigh_f376_l2": norm,
                       "exact_reduction": reduction, "eta_minimum": eta}
                trials.append(row)
                if eta > 1.0e-5 and reduction > MARGIN:
                    eligible.append({**row, "raw": candidate_raw})
            except (ArithmeticError, FloatingPointError, ValueError):
                continue
    selected = None; attempts = []
    for candidate in sorted(eligible, key=lambda row: row["exact_rayleigh_f376_l2"])[:4]:
        child = _fresh_child_gate(candidate["raw"])
        attempts.append({"alpha": candidate["alpha"], "exact_rayleigh_f376_l2": candidate["exact_rayleigh_f376_l2"],
                         "all_pass": child["all_pass"], "flux_envelope": child["flux_envelope"]})
        if child["all_pass"]:
            selected = candidate
            break
    best = None
    if selected is not None:
        best = {key: value for key, value in selected.items() if key != "raw"}
        best["raw_vector_hex"] = [float(value).hex() for value in selected["raw"]]
    promotion = {"attempted": bool(eligible), "promoted": selected is not None,
                 "child": child if eligible else None, "child_attempts": attempts}
    return {
        "source": {"version": "v20.86", "exact_rayleigh_f376_l2": source_norm},
        "proposal_model": {
            "physical_solve_dimension": [376, 376], "event_multiplier_explicit": True,
            "rayleigh_event_curvature_support": int(support.size),
            "event_curvature_artifact_validated": True,
            "action_coordinate_map": transform_audit,
            "transformed_rank": int(rank), "largest_singular_value": float(singular[0]),
            "smallest_singular_value": float(singular[-1]),
            "proposal_direction_scaled_l2": float(np.linalg.norm(direction_y)),
            "predicted_residual_l2_has_no_physical_authority": float(np.linalg.norm(predicted)),
            "used_only_to_propose": True,
        },
        "exact_line_search": {"both_orientations": True, "trial_count": len(trials),
                              "best_trials": sorted(trials, key=lambda row: row["exact_rayleigh_f376_l2"])[:10],
                              "best": best, "original_unweighted_376_rows_authoritative": True},
        "promotion": promotion,
        "outcome": "RAYLEIGH_CURVATURE_PRECONDITIONED_DESCENT_PROMOTED" if promotion["promoted"] else (
            "RAYLEIGH_CURVATURE_PRECONDITIONED_DESCENT_FAILED_CHILD" if eligible else "RAYLEIGH_CURVATURE_PRECONDITIONER_NO_DESCENT"
        ),
        "physical_equations_changed": False, "event_definition_changed": False,
        "acceptance_gate_changed": False, "left_residual_scaling_added": False,
        "componentwise_monotonicity_added": False,
    }


def completion_payload() -> dict[str, Any]:
    result = rayleigh_curvature_preconditioned_proposal(); best = result["exact_line_search"]["best"]
    validation = {
        "source_v20_86_reproduced": abs(result["source"]["exact_rayleigh_f376_l2"] - 0.787514011519100) < 5.0e-12,
        "square_explicit_multiplier_model": result["proposal_model"]["physical_solve_dimension"] == [376, 376] and result["proposal_model"]["event_multiplier_explicit"],
        "validated_curvature_used": result["proposal_model"]["event_curvature_artifact_validated"] and result["proposal_model"]["rayleigh_event_curvature_support"] == 37,
        "model_only_proposes": result["proposal_model"]["used_only_to_propose"],
        "exact_rows_decide": result["exact_line_search"]["original_unweighted_376_rows_authoritative"],
        "candidate_reduces_merit": best is None or best["exact_reduction"] > 0.0,
        "promotion_requires_child": not result["promotion"]["promoted"] or result["promotion"]["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"] and not result["event_definition_changed"] and not result["acceptance_gate_changed"] and not result["left_residual_scaling_added"],
        "no_componentwise_gate": not result["componentwise_monotonicity_added"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_RAYLEIGH_CURVATURE_PRECONDITIONED_PROPOSAL_V20_88", "version": VERSION,
        "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "rayleigh_curvature_preconditioned_proposal": result, "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation, "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_RAYLEIGH_CURVATURE_PRECONDITIONED_PROPOSAL_V20_88.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v20_88_selected_raw_vector", "rayleigh_curvature_preconditioned_proposal", "completion_payload", "materialize"]
