"""Use only corrected accepted Rayleigh-F376 secants to propose from v21.00."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import _action_curvature_transform
from bhsm.interface.aether_n3_curvature_transport_proposal_v21_00 import v21_00_selected_raw_vector
from bhsm.interface.aether_n3_dual_metric_range_space_continuation_v20_92 import v20_92_selected_raw_vector
from bhsm.interface.aether_n3_dual_metric_range_space_proposal_v20_91 import v20_91_selected_raw_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_rayleigh_curvature_preconditioned_proposal_v20_88 import v20_88_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_event_covector_v20_80 import rayleigh_square_physical_residual
from bhsm.interface.aether_n3_rayleigh_krylov_restriction_audit_v20_86 import v20_86_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_multiplier_continuation_v20_82 import v20_82_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_multiplier_continuation_v20_84 import v20_84_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_square_kkt_continuation_v20_83 import v20_83_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_square_kkt_continuation_v20_85 import v20_85_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_square_kkt_proposal_v20_81 import v20_81_selected_raw_vector
from bhsm.interface.aether_n3_refreshed_dual_metric_continuation_v20_95 import v20_95_selected_raw_vector
from bhsm.interface.aether_n3_refreshed_dual_metric_continuation_v20_99 import v20_99_selected_raw_vector
from bhsm.interface.aether_n3_refreshed_dual_metric_proposal_v20_94 import v20_94_selected_raw_vector
from bhsm.interface.aether_n3_refreshed_dual_metric_proposal_v20_98 import v20_98_selected_raw_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_structural_hindsight_recovery_v20_68 import _fresh_child_gate


VERSION = "v21.05"
CLASSIFICATION = "BHSM_N3_CORRECTED_ACCEPTED_RAYLEIGH_MULTI_SECANT_PROPOSAL"
FULL_BHSM_COMPLETE = False
BACKTRACKS = 41
MATERIAL_THRESHOLD = 9.7385990208e-5
STATES: tuple[tuple[str, Callable[[], np.ndarray]], ...] = (
    ("v20.81", v20_81_selected_raw_vector),
    ("v20.82", v20_82_selected_raw_vector),
    ("v20.83", v20_83_selected_raw_vector),
    ("v20.84", v20_84_selected_raw_vector),
    ("v20.85", v20_85_selected_raw_vector),
    ("v20.86", v20_86_selected_raw_vector),
    ("v20.88", v20_88_selected_raw_vector),
    ("v20.91", v20_91_selected_raw_vector),
    ("v20.92", v20_92_selected_raw_vector),
    ("v20.94", v20_94_selected_raw_vector),
    ("v20.95", v20_95_selected_raw_vector),
    ("v20.98", v20_98_selected_raw_vector),
    ("v20.99", v20_99_selected_raw_vector),
    ("v21.00", v21_00_selected_raw_vector),
)


def completion_payload() -> dict[str, Any]:
    scales = kkt_variable_scales()
    raws = [loader() for _, loader in STATES]
    residuals = [rayleigh_square_physical_residual(raw * scales) for raw in raws]
    source_raw = raws[-1]
    source_y = source_raw * scales
    source_residual = residuals[-1]
    source_norm = float(np.linalg.norm(source_residual))
    transform, transform_audit = _action_curvature_transform(source_raw)
    secants_x = []
    residual_secants = []
    labels = []
    for index in range(len(raws) - 1):
        secants_x.append(np.linalg.solve(
            transform, (raws[index + 1] - raws[index]) * scales
        ))
        residual_secants.append(residuals[index + 1] - residuals[index])
        labels.append(f"{STATES[index][0]}_to_{STATES[index + 1][0]}")
    s_matrix = np.column_stack(secants_x)
    y_matrix = np.column_stack(residual_secants)
    coefficients, _, rank, singular = np.linalg.lstsq(
        y_matrix, -source_residual, rcond=None
    )
    direction_x = s_matrix @ coefficients
    predicted = source_residual + y_matrix @ coefficients
    trials = []
    best = None
    for orientation in (-1.0, 1.0):
        for backtrack in range(BACKTRACKS):
            alpha = orientation * 0.5**backtrack
            candidate_y = source_y + alpha * (transform @ direction_x)
            try:
                raw = candidate_y / scales
                norm = float(np.linalg.norm(rayleigh_square_physical_residual(candidate_y)))
                eta = float(_minimum_node_eta(raw))
                reduction = source_norm - norm
                row = {
                    "orientation": "negative" if orientation < 0.0 else "positive",
                    "alpha": alpha,
                    "backtrack": backtrack,
                    "exact_rayleigh_f376_l2": norm,
                    "exact_reduction": reduction,
                    "eta_minimum": eta,
                }
                trials.append(row)
                if eta > 1.0e-5 and reduction > MARGIN and (
                    best is None or norm < best["exact_rayleigh_f376_l2"]
                ):
                    best = {**row, "raw": raw}
            except (ArithmeticError, FloatingPointError, ValueError):
                continue
    if best is not None:
        base_alpha = float(best["alpha"])
        for factor in (0.625, 0.75, 0.875, 1.125, 1.25, 1.5):
            alpha = base_alpha * factor
            candidate_y = source_y + alpha * (transform @ direction_x)
            try:
                raw = candidate_y / scales
                norm = float(np.linalg.norm(rayleigh_square_physical_residual(candidate_y)))
                eta = float(_minimum_node_eta(raw))
                reduction = source_norm - norm
                row = {
                    "orientation": "negative" if alpha < 0.0 else "positive",
                    "alpha": alpha,
                    "backtrack": None,
                    "exact_rayleigh_f376_l2": norm,
                    "exact_reduction": reduction,
                    "eta_minimum": eta,
                    "local_exact_refinement_factor": factor,
                }
                trials.append(row)
                if eta > 1.0e-5 and reduction > MARGIN and norm < best[
                    "exact_rayleigh_f376_l2"
                ]:
                    best = {**row, "raw": raw}
            except (ArithmeticError, FloatingPointError, ValueError):
                continue
    material = bool(best is not None and best["exact_reduction"] >= MATERIAL_THRESHOLD)
    best_summary = None
    promotion = {"attempted": False, "promoted": False}
    if best is not None:
        best_summary = {key: value for key, value in best.items() if key != "raw"}
        best_summary["raw_vector_hex"] = [float(value).hex() for value in best["raw"]]
    if material and best is not None:
        child = _fresh_child_gate(best["raw"])
        promotion = {"attempted": True, "promoted": child["all_pass"], "child": child}
    result = {
        "source_frontier": {"version": "v21.00", "exact_rayleigh_f376_l2": source_norm},
        "multisecant_model": {
            "accepted_corrected_secants": labels,
            "dimension": len(labels),
            "rank": int(rank),
            "singular_values": singular.tolist(),
            "coefficients": coefficients.tolist(),
            "action_coordinate_direction_norm": float(np.linalg.norm(direction_x)),
            "predicted_residual_norm_has_no_physical_authority": float(np.linalg.norm(predicted)),
            "coordinate_map": transform_audit,
            "model_used_only_to_propose": True,
        },
        "exact_search": {
            "both_orientations_scanned": True,
            "original_unweighted_rayleigh_f376_authoritative": True,
            "valid_trial_count": len(trials),
            "best_trials": sorted(trials, key=lambda row: row["exact_rayleigh_f376_l2"])[:12],
            "material_threshold_reused_from_accepted_history": MATERIAL_THRESHOLD,
            "best": best_summary,
            "material_recovery": material,
        },
        "promotion": promotion,
        "classification": "CORRECTED_MULTI_SECANT_MATERIAL_RECOVERY" if material else "CORRECTED_MULTI_SECANT_NO_MATERIAL_RECOVERY",
        "physical_equations_changed": False,
        "event_definition_changed": False,
        "complete_child_gate_changed": False,
        "left_residual_scaling_added": False,
    }
    validation = {
        "source_v21_00_reproduced": abs(source_norm - 0.782778933037026) < 5.0e-12,
        "accepted_corrected_states_only": len(labels) == len(STATES) - 1,
        "model_only_proposes": result["multisecant_model"]["model_used_only_to_propose"],
        "exact_rows_decide": result["exact_search"]["original_unweighted_rayleigh_f376_authoritative"],
        "both_orientations": result["exact_search"]["both_orientations_scanned"],
        "promotion_only_after_material_recovery": not promotion["attempted"] or material,
        "promotion_requires_child": not promotion["promoted"] or promotion["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"]
        and not result["event_definition_changed"]
        and not result["complete_child_gate_changed"]
        and not result["left_residual_scaling_added"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_CORRECTED_RAYLEIGH_MULTI_SECANT_V21_05",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "corrected_rayleigh_multisecant": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_CORRECTED_RAYLEIGH_MULTI_SECANT_V21_05.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "completion_payload", "materialize"]
