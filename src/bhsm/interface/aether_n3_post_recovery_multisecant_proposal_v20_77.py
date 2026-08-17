"""Action-coordinate multisecant proposal from the recovered accepted corridor."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import _action_curvature_transform
from bhsm.interface.aether_n3_controlled_structured_shake_recovery_v20_69 import v20_69_selected_raw_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_structural_hindsight_recovery_v20_68 import _fresh_child_gate
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_70 import v20_70_selected_raw_vector
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_71 import v20_71_selected_raw_vector
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_72 import v20_72_selected_raw_vector
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_73 import v20_73_selected_raw_vector
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_74 import v20_74_selected_raw_vector
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_75 import v20_75_selected_raw_vector


VERSION = "v20.77"
CLASSIFICATION = "BHSM_N3_POST_RECOVERY_ACTION_MULTI_SECANT_PROPOSAL"
FULL_BHSM_COMPLETE = False
BACKTRACKS = 41
STATES: tuple[tuple[str, Callable[[], np.ndarray]], ...] = (
    ("v20.69", v20_69_selected_raw_vector), ("v20.70", v20_70_selected_raw_vector),
    ("v20.71", v20_71_selected_raw_vector), ("v20.72", v20_72_selected_raw_vector),
    ("v20.73", v20_73_selected_raw_vector), ("v20.74", v20_74_selected_raw_vector),
    ("v20.75", v20_75_selected_raw_vector),
)


def v20_77_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_POST_RECOVERY_MULTI_SECANT_PROPOSAL_V20_77.json"
    ).read_text(encoding="utf-8"))
    result = payload["post_recovery_multisecant_proposal"]
    if not result["promotion"]["promoted"]:
        raise ValueError("v20.77 multisecant candidate was not physically promoted")
    return np.asarray([float.fromhex(value) for value in result["exact_line_search"]["best"]["raw_vector_hex"]])


def _block_fractions(direction: np.ndarray) -> dict[str, float]:
    blocks = {
        "scale": [10 * node for node in range(23)],
        "u": [10 * node + column for node in range(23) for column in range(1, 4)],
        "w": [10 * node + column for node in range(23) for column in range(4, 7)],
        "v": [10 * node + column for node in range(23) for column in range(7, 10)],
        "lapse": [230 + 6 * node + column for node in range(24) for column in range(3)],
        "shift": [230 + 6 * node + column for node in range(24) for column in range(3, 6)],
        "period": [374], "event_multiplier": [375],
    }
    denominator = float(direction @ direction)
    return {name: float(direction[rows] @ direction[rows] / denominator) for name, rows in blocks.items()}


def post_recovery_multisecant_proposal() -> dict[str, Any]:
    scales = kkt_variable_scales()
    raws = [loader() for _, loader in STATES]
    residuals = [_square_physical_residual(raw * scales) for raw in raws]
    source_raw = raws[-1]; source_residual = residuals[-1]
    source_norm = float(np.linalg.norm(source_residual))
    transform, transform_audit = _action_curvature_transform(source_raw)
    secants_x = []
    residual_secants = []
    labels = []
    for index in range(len(raws) - 1):
        secants_x.append(np.linalg.solve(transform, (raws[index + 1] - raws[index]) * scales))
        residual_secants.append(residuals[index + 1] - residuals[index])
        labels.append(f"{STATES[index][0]}_to_{STATES[index + 1][0]}")
    s = np.column_stack(secants_x)
    y = np.column_stack(residual_secants)
    singular = np.linalg.svd(y, compute_uv=False)
    coefficients, _, rank, _ = np.linalg.lstsq(y, -source_residual, rcond=None)
    direction_x = s @ coefficients
    predicted = source_residual + y @ coefficients
    trials = []
    best = None
    for orientation in (-1.0, 1.0):
        for backtrack in range(BACKTRACKS):
            alpha = orientation * 0.5**backtrack
            candidate_y = source_raw * scales + alpha * (transform @ direction_x)
            try:
                raw = candidate_y / scales
                norm = float(np.linalg.norm(_square_physical_residual(candidate_y)))
                eta = float(_minimum_node_eta(raw)); reduction = source_norm - norm
                row = {"orientation": "negative" if orientation < 0.0 else "positive", "alpha": alpha, "backtrack": backtrack, "exact_f376_l2": norm, "exact_reduction": reduction, "eta_minimum": eta}
                trials.append(row)
                if eta > 1.0e-5 and reduction > MARGIN and (best is None or norm < best["exact_f376_l2"]):
                    best = {**row, "raw": raw}
            except (ArithmeticError, FloatingPointError, ValueError):
                continue
    if best is not None:
        base_alpha = float(best["alpha"])
        for factor in (0.625, 0.75, 0.875, 1.125, 1.25, 1.5):
            alpha = base_alpha * factor
            candidate_y = source_raw * scales + alpha * (transform @ direction_x)
            try:
                raw = candidate_y / scales
                norm = float(np.linalg.norm(_square_physical_residual(candidate_y)))
                eta = float(_minimum_node_eta(raw)); reduction = source_norm - norm
                row = {"orientation": "negative" if alpha < 0.0 else "positive", "alpha": alpha, "backtrack": None, "exact_f376_l2": norm, "exact_reduction": reduction, "eta_minimum": eta, "local_exact_refinement_factor": factor}
                trials.append(row)
                if eta > 1.0e-5 and reduction > MARGIN and norm < best["exact_f376_l2"]:
                    best = {**row, "raw": raw}
            except (ArithmeticError, FloatingPointError, ValueError):
                continue
    best_summary = None
    promotion = {"attempted": False, "promoted": False}
    if best is not None:
        best_summary = {key: value for key, value in best.items() if key != "raw"}
        best_summary["raw_vector_hex"] = [float(value).hex() for value in best["raw"]]
        child = _fresh_child_gate(best["raw"])
        promotion = {"attempted": True, "promoted": child["all_pass"], "child": child}
    return {
        "source_frontier": {"version": "v20.75", "exact_f376_l2": source_norm},
        "ownership_source": "VALIDATED_V20_76_DISTRIBUTED_W_PERIOD_SCALE_V_NO_DOMINANT_OWNER",
        "multisecant_model": {
            "accepted_secants": labels, "dimension": len(labels), "rank": int(rank),
            "singular_values": singular.tolist(), "coefficients": coefficients.tolist(),
            "action_coordinate_direction_norm": float(np.linalg.norm(direction_x)),
            "action_coordinate_block_fractions": _block_fractions(direction_x),
            "predicted_residual_norm_has_no_physical_authority": float(np.linalg.norm(predicted)),
            "coordinate_map": transform_audit,
            "model_used_only_to_propose": True,
        },
        "exact_line_search": {
            "both_orientations_scanned": True, "original_unweighted_f376_authoritative": True,
            "valid_trial_count": len(trials), "best_trials": sorted(trials, key=lambda row: row["exact_f376_l2"])[:12],
            "best": best_summary,
        },
        "promotion": promotion,
        "physical_equations_changed": False, "event_definition_changed": False,
        "complete_child_gate_changed": False, "left_residual_scaling_added": False,
        "next_action": "CONTINUE_EXACT_N3_CLOSURE_FROM_V20_77" if promotion["promoted"] else "DERIVE_NEXT_ACTION_OWNED_DIRECTION_FROM_DISTRIBUTED_OWNER_GEOMETRY",
    }


def completion_payload() -> dict[str, Any]:
    result = post_recovery_multisecant_proposal(); best = result["exact_line_search"]["best"]
    validation = {
        "source_v20_75_reproduced": abs(result["source_frontier"]["exact_f376_l2"] - 0.758674247739506) < 5.0e-12,
        "accepted_secants_only": result["multisecant_model"]["dimension"] == len(STATES) - 1,
        "model_only_proposes": result["multisecant_model"]["model_used_only_to_propose"],
        "exact_f376_decides": result["exact_line_search"]["original_unweighted_f376_authoritative"],
        "both_orientations": result["exact_line_search"]["both_orientations_scanned"],
        "promotion_only_after_descent": not result["promotion"]["attempted"] or best["exact_reduction"] > 0.0,
        "promotion_only_after_child": not result["promotion"]["promoted"] or result["promotion"]["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"] and not result["event_definition_changed"] and not result["complete_child_gate_changed"] and not result["left_residual_scaling_added"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_POST_RECOVERY_MULTI_SECANT_PROPOSAL_V20_77",
        "version": VERSION, "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "post_recovery_multisecant_proposal": result,
        "status": "VALIDATED" if passed else "INVALIDATED", "validation": validation, "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_POST_RECOVERY_MULTI_SECANT_PROPOSAL_V20_77.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v20_77_selected_raw_vector", "post_recovery_multisecant_proposal", "completion_payload", "materialize"]
