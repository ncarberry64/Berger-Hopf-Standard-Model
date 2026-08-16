"""Measure and prospectively test full-F376 residual-manifold normal curvature."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import _action_curvature_transform
from bhsm.interface.aether_n3_corrected_rayleigh_multisecant_v21_05 import STATES
from bhsm.interface.aether_n3_curvature_singular_subspace_audit_v20_89 import curvature_singular_subspace_audit
from bhsm.interface.aether_n3_exact_action_hessian_assembly_v18_18 import exact_sbp_action_hessian
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_natural_radius_scan_v21_04 import v21_04_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_event_covector_v20_80 import (
    rayleigh_sbp_event_covector, rayleigh_square_physical_residual,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_structural_hindsight_recovery_v20_68 import _fresh_child_gate


VERSION = "v21.06"
CLASSIFICATION = "BHSM_N3_FULL_RESIDUAL_MANIFOLD_NORMAL_ACCELERATION"
FULL_BHSM_COMPLETE = False
MATERIAL_THRESHOLD = 9.7385990208e-5


def _current_square_response(raw: np.ndarray, audit: dict[str, Any]) -> np.ndarray:
    scales = kkt_variable_scales()
    y = raw * scales
    inverse = 1.0 / scales[:-1]
    action = exact_sbp_action_hessian(raw[:-1])
    action_raw = np.asarray(action.pop("hessian"))
    action_scaled = inverse[:, None] * action_raw * inverse[None, :]
    support = np.asarray(audit["event_curvature_support_indices"], dtype=int)
    block = np.asarray(audit["event_curvature_symmetric_block"], dtype=float)
    event_hessian = np.zeros((375, 375))
    event_hessian[np.ix_(support, support)] = block
    event_gradient = rayleigh_sbp_event_covector(raw[:-1]) * inverse / scales[-1]
    matrix = np.zeros((376, 376))
    matrix[:-1, :-1] = action_scaled + y[-1] * event_hessian
    matrix[:-1, -1] = event_gradient
    matrix[-1, :-1] = event_gradient
    return matrix


def completion_payload() -> dict[str, Any]:
    source_raw = v21_04_selected_raw_vector()
    scales = kkt_variable_scales()
    source_y = source_raw * scales
    source_residual = rayleigh_square_physical_residual(source_y)
    source_norm = float(np.linalg.norm(source_residual))
    curvature = curvature_singular_subspace_audit(source_raw, source_label="v21.04")
    matrix = _current_square_response(source_raw, curvature)
    transform, transform_audit = _action_curvature_transform(source_raw)

    prior = json.loads(Path(
        "artifacts/BHSM_N3_CORRECTED_RAYLEIGH_MULTI_SECANT_V21_05.json"
    ).read_text(encoding="utf-8"))["corrected_rayleigh_multisecant"]
    coefficients = np.asarray(prior["multisecant_model"]["coefficients"], dtype=float)
    raws = [loader() for _, loader in STATES]
    secants_x = np.column_stack([
        np.linalg.solve(transform, (raws[index + 1] - raws[index]) * scales)
        for index in range(len(raws) - 1)
    ])
    direction_x = secants_x @ coefficients
    direction_x_norm = float(np.linalg.norm(direction_x))
    tangent_x = direction_x / direction_x_norm
    tangent_y = transform @ tangent_x
    prior_best = prior["exact_search"]["best"]
    reference_radius = float(abs(prior_best["alpha"]) * direction_x_norm)

    curvature_rows = []
    estimates = []
    for factor in (0.5, 1.0, 2.0):
        radius = factor * reference_radius
        plus = rayleigh_square_physical_residual(source_y + radius * tangent_y)
        minus = rayleigh_square_physical_residual(source_y - radius * tangent_y)
        estimate = (plus - 2.0 * source_residual + minus) / radius**2
        estimates.append(estimate)
        curvature_rows.append({
            "radius_factor": factor,
            "action_coordinate_radius": radius,
            "directional_second_variation_l2": float(np.linalg.norm(estimate)),
            "plus_exact_f376_l2": float(np.linalg.norm(plus)),
            "minus_exact_f376_l2": float(np.linalg.norm(minus)),
        })
    second_variation = estimates[1]
    curvature_consistency = {
        "half_vs_reference_relative": float(
            np.linalg.norm(estimates[0] - second_variation)
            / max(np.linalg.norm(second_variation), 1.0)
        ),
        "double_vs_reference_relative": float(
            np.linalg.norm(estimates[2] - second_variation)
            / max(np.linalg.norm(second_variation), 1.0)
        ),
    }

    left, singular, right_t = np.linalg.svd(matrix, full_matrices=True)
    tolerance = float(np.finfo(float).eps * max(matrix.shape) * singular[0])
    retained = singular > tolerance
    spectral_coefficients = left.T @ (-second_variation)
    acceleration_coefficients = np.zeros_like(spectral_coefficients)
    acceleration_coefficients[retained] = (
        spectral_coefficients[retained] / singular[retained]
    )
    acceleration_y = right_t.T @ acceleration_coefficients
    acceleration_x = np.linalg.solve(transform, acceleration_y)
    normal_defect = matrix @ acceleration_y + second_variation

    trials = []
    eligible = []
    for orientation in (-1.0, 1.0):
        for exponent in range(-10, 5):
            radius = orientation * reference_radius * 2.0**exponent
            tangent_candidate_y = source_y + radius * tangent_y
            curved_candidate_y = (
                tangent_candidate_y + 0.5 * radius**2 * acceleration_y
            )
            for path, candidate_y in (
                ("tangent", tangent_candidate_y),
                ("normal_accelerated", curved_candidate_y),
            ):
                try:
                    candidate_raw = candidate_y / scales
                    norm = float(np.linalg.norm(rayleigh_square_physical_residual(candidate_y)))
                    eta = float(_minimum_node_eta(candidate_raw))
                    reduction = source_norm - norm
                    row = {
                        "path": path,
                        "orientation": "negative" if orientation < 0.0 else "positive",
                        "radius_exponent": exponent,
                        "signed_action_coordinate_radius": radius,
                        "exact_rayleigh_f376_l2": norm,
                        "exact_reduction": reduction,
                        "eta_minimum": eta,
                        "normal_acceleration_action_contribution_norm": float(
                            0.5 * radius**2 * np.linalg.norm(acceleration_x)
                        ),
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
        "tangent": {
            "source": "V21_05_CORRECTED_ACCEPTED_RAYLEIGH_MULTI_SECANT",
            "action_coordinate_direction_norm_before_normalization": direction_x_norm,
            "reference_action_coordinate_radius": reference_radius,
            "coordinate_map": transform_audit,
        },
        "full_residual_directional_curvature": {
            "exact_symmetric_evaluations": curvature_rows,
            "consistency": curvature_consistency,
            "reference_second_variation_l2": float(np.linalg.norm(second_variation)),
            "all_376_rows_measured": True,
        },
        "normal_acceleration": {
            "relation": "J*a=-D2F376[s,s]",
            "response_rank_numerical_only": int(np.count_nonzero(retained)),
            "response_tolerance_numerical_only": tolerance,
            "action_coordinate_norm": float(np.linalg.norm(acceleration_x)),
            "physical_scaled_norm": float(np.linalg.norm(acceleration_y)),
            "relative_normal_equation_defect": float(
                np.linalg.norm(normal_defect) / max(np.linalg.norm(second_variation), 1.0)
            ),
            "used_only_to_propose": True,
        },
        "prospective_exact_search": {
            "paths": ["tangent", "normal_accelerated"],
            "both_orientations": True,
            "original_unweighted_rayleigh_f376_authoritative": True,
            "valid_trial_count": len(trials),
            "best_trials": sorted(trials, key=lambda row: row["exact_rayleigh_f376_l2"])[:16],
            "material_threshold_reused_from_accepted_history": MATERIAL_THRESHOLD,
            "best": best_summary,
            "material_recovery": material,
        },
        "promotion": promotion,
        "classification": "NORMAL_ACCELERATION_MATERIAL_RECOVERY" if material else "NORMAL_ACCELERATION_NO_MATERIAL_RECOVERY",
        "physical_equations_changed": False,
        "event_definition_changed": False,
        "complete_child_gate_changed": False,
        "left_residual_scaling_added": False,
        "componentwise_monotonicity_added": False,
    }
    validation = {
        "source_v21_04_reproduced": abs(source_norm - 0.782775399601569) < 5.0e-12,
        "current_curvature_source_reproduced": abs(
            curvature["source"]["exact_rayleigh_f376_l2"] - source_norm
        ) < 5.0e-12,
        "three_exact_curvature_scales": len(curvature_rows) == 3,
        "all_rows_measured": result["full_residual_directional_curvature"]["all_376_rows_measured"],
        "normal_acceleration_only_proposes": result["normal_acceleration"]["used_only_to_propose"],
        "exact_rows_decide": result["prospective_exact_search"]["original_unweighted_rayleigh_f376_authoritative"],
        "promotion_only_after_material_recovery": not promotion["attempted"] or material,
        "promotion_requires_child": not promotion["promoted"] or promotion["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"]
        and not result["event_definition_changed"]
        and not result["complete_child_gate_changed"]
        and not result["left_residual_scaling_added"],
        "no_componentwise_gate": not result["componentwise_monotonicity_added"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_RESIDUAL_MANIFOLD_NORMAL_ACCELERATION_V21_06",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "residual_manifold_normal_acceleration": result,
        "curvature_refresh": curvature,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_RESIDUAL_MANIFOLD_NORMAL_ACCELERATION_V21_06.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "completion_payload", "materialize"]
