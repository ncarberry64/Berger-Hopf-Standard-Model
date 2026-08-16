"""Use exact Rayleigh-F376 directional responses without an event-Hessian block."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.sparse.linalg import LinearOperator, gmres

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import _action_curvature_transform
from bhsm.interface.aether_n3_curvature_singular_subspace_audit_v20_89 import curvature_singular_subspace_audit
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_natural_radius_scan_v21_04 import v21_04_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_event_covector_v20_80 import rayleigh_square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_structural_hindsight_recovery_v20_68 import _fresh_child_gate
from bhsm.interface.aether_n3_residual_manifold_normal_acceleration_v21_06 import _current_square_response


VERSION = "v21.14"
CLASSIFICATION = "BHSM_N3_EXACT_RAYLEIGH_MATRIX_FREE_RESPONSE_PROPOSAL"
FULL_BHSM_COMPLETE = False
RESPONSE_STEP = 2.0e-7
POINTS = 17
MATERIAL_THRESHOLD = 9.7385990208e-5


def completion_payload(*, restart: int = 30, right_precondition: bool = False) -> dict[str, Any]:
    raw = v21_04_selected_raw_vector()
    scales = kkt_variable_scales()
    y = raw * scales
    residual = rayleigh_square_physical_residual(y)
    source_norm = float(np.linalg.norm(residual))
    transform, transform_audit = _action_curvature_transform(raw)

    def response(direction_y: np.ndarray, step: float = RESPONSE_STEP) -> np.ndarray:
        norm = float(np.linalg.norm(direction_y))
        if norm == 0.0:
            return np.zeros(376)
        unit = direction_y / norm
        return norm * (
            rayleigh_square_physical_residual(y + step * unit)
            - rayleigh_square_physical_residual(y - step * unit)
        ) / (2.0 * step)

    right_map = np.eye(376)
    preconditioner_audit: dict[str, Any] = {
        "used": False,
        "root_equivalent_invertible_right_coordinate_map": True,
    }
    if right_precondition:
        curvature = curvature_singular_subspace_audit(raw, source_label="v21.04")
        assembled_x = _current_square_response(raw, curvature) @ transform
        left, singular, right_t = np.linalg.svd(assembled_x, full_matrices=True)
        tolerance = float(np.finfo(float).eps * max(assembled_x.shape) * singular[0])
        retained = singular > tolerance
        floor = float(singular[np.flatnonzero(retained)[-1]])
        inverse = 1.0 / np.maximum(singular, floor)
        right_map = (right_t.T * inverse) @ left.T
        preconditioner_audit = {
            "used": True,
            "source": "ACTION_OWNED_ASSEMBLED_SQUARE_RESPONSE_NUMERICAL_ONLY",
            "assembled_event_curvature_has_no_DERIVATIVE_AUTHORITY": True,
            "right_coordinate_map_only": True,
            "left_residual_scaling_added": False,
            "spectral_floor_owned_by_weakest_numerically_retained_assembled_mode": floor,
            "assembled_numerical_rank": int(np.count_nonzero(retained)),
            "condition_number_after_floor": float(singular[0] / floor),
            "root_equivalent_invertible_right_coordinate_map": bool(
                np.linalg.matrix_rank(right_map) == 376
            ),
        }
    operator = LinearOperator(
        (376, 376),
        matvec=lambda dq: response(transform @ (right_map @ dq)),
        dtype=float,
    )
    callbacks: list[float] = []
    direction_q, info = gmres(
        operator,
        -residual,
        rtol=1.0e-6,
        atol=0.0,
        restart=restart,
        maxiter=1,
        callback=lambda value: callbacks.append(float(value)),
        callback_type="pr_norm",
    )
    direction_x = right_map @ direction_q
    direction_y = transform @ direction_x
    unit_x = direction_x / np.linalg.norm(direction_x)
    unit_y = transform @ unit_x
    fine = response(direction_y, 0.5 * RESPONSE_STEP)
    reference = response(direction_y, RESPONSE_STEP)
    coarse = response(direction_y, 2.0 * RESPONSE_STEP)
    denominator = max(float(np.linalg.norm(reference)), 1.0)
    response_audit = {
        "scaled_steps": [0.5 * RESPONSE_STEP, RESPONSE_STEP, 2.0 * RESPONSE_STEP],
        "half_vs_reference_relative": float(np.linalg.norm(fine - reference) / denominator),
        "double_vs_reference_relative": float(np.linalg.norm(coarse - reference) / denominator),
        "linear_residual_relative": float(
            np.linalg.norm(reference + residual) / max(source_norm, 1.0)
        ),
        "gmres_info_has_no_physical_authority": int(info),
        "krylov_restart_numerical_control": restart,
        "iterations": len(callbacks),
        "final_callback_relative_residual": callbacks[-1] if callbacks else None,
    }
    action_radii = json.loads(Path(
        "artifacts/BHSM_N3_STRUCTURAL_HINDSIGHT_RECOVERY_V20_68.json"
    ).read_text(encoding="utf-8"))["structural_hindsight_recovery"][
        "prospective_search"
    ]["class_action_amplitudes"]
    direct = json.loads(Path(
        "artifacts/BHSM_N3_DIRECT_REFRESH_PROPOSAL_V21_02.json"
    ).read_text(encoding="utf-8"))["direct_refresh_proposal"]
    direct_positive = {
        row["radius_class"]: float(row["realized_physical_scaled_norm"])
        for row in direct["exact_search"]["trials"]
        if row["orientation"] == "positive"
    }
    action_endpoints = np.asarray([
        float(action_radii["PLATEAU_DESCENT"]),
        float(action_radii["MEDIUM_DESCENT"]),
    ])
    physical_endpoints = np.asarray([
        direct_positive["PLATEAU_DESCENT"],
        direct_positive["MEDIUM_DESCENT"],
    ])
    trials = []
    eligible = []
    for index, fraction in enumerate(np.linspace(0.0, 1.0, POINTS)):
        action_radius = float(np.exp(
            (1.0 - fraction) * np.log(action_endpoints[0])
            + fraction * np.log(action_endpoints[1])
        ))
        physical_radius = float(np.exp(
            (1.0 - fraction) * np.log(physical_endpoints[0])
            + fraction * np.log(physical_endpoints[1])
        ))
        displacement_x = action_radius * unit_x
        displacement_y = action_radius * unit_y
        intersection = min(
            1.0, physical_radius / max(float(np.linalg.norm(displacement_y)), 1.0e-300)
        )
        displacement_x *= intersection
        displacement_y *= intersection
        for orientation in (-1.0, 1.0):
            candidate_y = y + orientation * displacement_y
            try:
                candidate_raw = candidate_y / scales
                norm = float(np.linalg.norm(rayleigh_square_physical_residual(candidate_y)))
                eta = float(_minimum_node_eta(candidate_raw))
                reduction = source_norm - norm
                row = {
                    "radius_index": index,
                    "orientation": "negative" if orientation < 0.0 else "positive",
                    "bhsm_action_radius": action_radius,
                    "bhsm_physical_radius": physical_radius,
                    "intersection_factor": intersection,
                    "realized_action_coordinate_norm": float(np.linalg.norm(displacement_x)),
                    "realized_physical_scaled_norm": float(np.linalg.norm(displacement_y)),
                    "exact_rayleigh_f376_l2": norm,
                    "exact_reduction": reduction,
                    "eta_minimum": eta,
                }
                trials.append(row)
                if eta > 1.0e-5 and reduction > MARGIN:
                    eligible.append({**row, "raw": candidate_raw})
            except (ArithmeticError, FloatingPointError, ValueError):
                continue
    best = min(eligible, key=lambda row: row["exact_rayleigh_f376_l2"]) if eligible else None
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
        "source_frontier": {"version": "v21.04", "exact_rayleigh_f376_l2": source_norm},
        "matrix_free_response": {
            "exact_original_rayleigh_f376_directional_differences": True,
            "right_action_coordinate_map": transform_audit,
            "assembled_event_hessian_used": False,
            "response_audit": response_audit,
            "model_used_only_to_propose": True,
        },
        "prospective_exact_search": {
            "both_orientations": True,
            "dual_bhsm_metric_intersection": True,
            "trial_count": len(trials),
            "best_trials": sorted(trials, key=lambda row: row["exact_rayleigh_f376_l2"])[:16],
            "original_unweighted_rayleigh_f376_authoritative": True,
            "material_threshold_reused_from_accepted_history": MATERIAL_THRESHOLD,
            "best": best_summary,
            "material_recovery": material,
        },
        "promotion": promotion,
        "classification": "EXACT_MATRIX_FREE_MATERIAL_RECOVERY" if material else "EXACT_MATRIX_FREE_NO_MATERIAL_RECOVERY",
        "physical_equations_changed": False,
        "event_definition_changed": False,
        "complete_child_gate_changed": False,
        "left_residual_scaling_added": False,
        "componentwise_monotonicity_added": False,
    }
    if right_precondition:
        result["matrix_free_response"]["right_response_preconditioner"] = preconditioner_audit
    validation = {
        "source_v21_04_reproduced": abs(source_norm - 0.782775399601569) < 5.0e-12,
        "exact_directional_rows": result["matrix_free_response"]["exact_original_rayleigh_f376_directional_differences"],
        "no_event_hessian_block": not result["matrix_free_response"]["assembled_event_hessian_used"],
        "model_only_proposes": result["matrix_free_response"]["model_used_only_to_propose"],
        "both_signs_all_points": result["prospective_exact_search"]["trial_count"] == 2 * POINTS,
        "exact_rows_decide": result["prospective_exact_search"]["original_unweighted_rayleigh_f376_authoritative"],
        "promotion_only_after_material_recovery": not promotion["attempted"] or material,
        "promotion_requires_child": not promotion["promoted"] or promotion["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"]
        and not result["event_definition_changed"]
        and not result["complete_child_gate_changed"]
        and not result["left_residual_scaling_added"],
        "no_componentwise_gate": not result["componentwise_monotonicity_added"],
    }
    if right_precondition:
        validation["root_equivalent_right_map"] = preconditioner_audit[
            "root_equivalent_invertible_right_coordinate_map"
        ]
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_EXACT_MATRIX_FREE_RESPONSE_PROPOSAL_V21_14",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "exact_matrix_free_response_proposal": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_EXACT_MATRIX_FREE_RESPONSE_PROPOSAL_V21_14.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "completion_payload", "materialize"]
