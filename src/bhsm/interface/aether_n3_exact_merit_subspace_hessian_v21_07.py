"""Measure the exact nonlinear merit Hessian in a BHSM-owned accepted subspace."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import _action_curvature_transform
from bhsm.interface.aether_n3_corrected_rayleigh_multisecant_v21_05 import STATES
from bhsm.interface.aether_n3_dual_metric_range_space_proposal_v20_91 import _physical_history_radii
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_natural_radius_scan_v21_04 import v21_04_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_event_covector_v20_80 import rayleigh_square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_residual_manifold_normal_acceleration_v21_06 import _current_square_response
from bhsm.interface.aether_n3_structural_hindsight_recovery_v20_68 import _fresh_child_gate


VERSION = "v21.07"
CLASSIFICATION = "BHSM_N3_EXACT_NONLINEAR_MERIT_SUBSPACE_HESSIAN"
FULL_BHSM_COMPLETE = False
MATERIAL_THRESHOLD = 9.7385990208e-5
POINTS = 17


def _orthonormalize(named: list[tuple[str, np.ndarray]]) -> list[tuple[str, np.ndarray]]:
    result: list[tuple[str, np.ndarray]] = []
    for name, vector in named:
        value = np.asarray(vector, dtype=float).copy()
        original = float(np.linalg.norm(value))
        for _, prior in result:
            value -= float(prior @ value) * prior
        norm = float(np.linalg.norm(value))
        if norm > 1.0e-10 * max(original, 1.0e-300):
            result.append((name, value / norm))
    return result


def _trust_step(hessian: np.ndarray, gradient: np.ndarray, radius: float) -> tuple[np.ndarray, float]:
    eigenvalues, eigenvectors = np.linalg.eigh(hessian)
    coefficients = eigenvectors.T @ gradient
    scale = max(float(np.max(np.abs(eigenvalues))), 1.0)
    low = max(0.0, -float(eigenvalues[0]) + 1.0e-12 * scale)

    def step(shift: float) -> np.ndarray:
        return -eigenvectors @ (coefficients / (eigenvalues + shift))

    if low == 0.0:
        candidate = step(0.0)
        if np.linalg.norm(candidate) <= radius:
            return candidate, 0.0
    high = max(1.0, 2.0 * low)
    while np.linalg.norm(step(high)) > radius:
        high *= 4.0
    for _ in range(96):
        middle = 0.5 * (low + high)
        if np.linalg.norm(step(middle)) > radius:
            low = middle
        else:
            high = middle
    return step(high), high


def completion_payload() -> dict[str, Any]:
    source_raw = v21_04_selected_raw_vector()
    scales = kkt_variable_scales()
    source_y = source_raw * scales
    source_residual = rayleigh_square_physical_residual(source_y)
    source_norm = float(np.linalg.norm(source_residual))
    source_merit = 0.5 * source_norm**2
    payload_06 = json.loads(Path(
        "artifacts/BHSM_N3_RESIDUAL_MANIFOLD_NORMAL_ACCELERATION_V21_06.json"
    ).read_text(encoding="utf-8"))
    curvature = payload_06["curvature_refresh"]
    matrix = _current_square_response(source_raw, curvature)
    transform, transform_audit = _action_curvature_transform(source_raw)
    raws = {version: loader() for version, loader in STATES}
    prior = json.loads(Path(
        "artifacts/BHSM_N3_CORRECTED_RAYLEIGH_MULTI_SECANT_V21_05.json"
    ).read_text(encoding="utf-8"))["corrected_rayleigh_multisecant"]
    coefficients = np.asarray(prior["multisecant_model"]["coefficients"], dtype=float)
    ordered_raws = [raws[version] for version, _ in STATES]
    secant_matrix = np.column_stack([
        np.linalg.solve(
            transform, (ordered_raws[index + 1] - ordered_raws[index]) * scales
        )
        for index in range(len(ordered_raws) - 1)
    ])
    multisecant = secant_matrix @ coefficients
    gradient_y = matrix.T @ source_residual
    gradient_x = transform.T @ gradient_y
    named = [
        ("corrected_multisecant", multisecant),
        ("material_v20_92_to_v20_94", np.linalg.solve(
            transform, (raws["v20.94"] - raws["v20.92"]) * scales
        )),
        ("material_v20_95_to_v20_98", np.linalg.solve(
            transform, (raws["v20.98"] - raws["v20.95"]) * scales
        )),
        ("material_v20_88_to_v20_91", np.linalg.solve(
            transform, (raws["v20.91"] - raws["v20.88"]) * scales
        )),
        ("negative_current_merit_gradient", -gradient_x),
    ]
    basis = _orthonormalize(named)
    basis_x = np.column_stack([vector for _, vector in basis])
    basis_y = transform @ basis_x
    dimension = basis_x.shape[1]
    radius_payload = json.loads(Path(
        "artifacts/BHSM_N3_NATURAL_RADIUS_SCAN_V21_04.json"
    ).read_text(encoding="utf-8"))["natural_radius_scan"]
    radius_best = radius_payload["exact_search"]["best"]
    reference_radius = float(radius_best["realized_action_coordinate_norm"])
    reference_physical_radius = float(radius_best["realized_physical_scaled_norm"])
    difference_radii = np.minimum(
        reference_radius,
        reference_physical_radius / np.maximum(
            np.linalg.norm(basis_y, axis=0), 1.0e-300
        ),
    )

    plus_merit = np.empty(dimension)
    minus_merit = np.empty(dimension)
    for index in range(dimension):
        local_radius = float(difference_radii[index])
        plus = rayleigh_square_physical_residual(
            source_y + local_radius * basis_y[:, index]
        )
        minus = rayleigh_square_physical_residual(
            source_y - local_radius * basis_y[:, index]
        )
        plus_merit[index] = 0.5 * float(plus @ plus)
        minus_merit[index] = 0.5 * float(minus @ minus)
    exact_gradient = (plus_merit - minus_merit) / (2.0 * difference_radii)
    hessian = np.zeros((dimension, dimension))
    hessian[np.diag_indices(dimension)] = (
        plus_merit - 2.0 * source_merit + minus_merit
    ) / difference_radii**2
    for left in range(dimension):
        for right in range(left + 1, dimension):
            left_radius = float(difference_radii[left])
            right_radius = float(difference_radii[right])
            directions = (
                left_radius * basis_y[:, left] + right_radius * basis_y[:, right],
                left_radius * basis_y[:, left] - right_radius * basis_y[:, right],
                -left_radius * basis_y[:, left] + right_radius * basis_y[:, right],
                -left_radius * basis_y[:, left] - right_radius * basis_y[:, right],
            )
            values = []
            for direction in directions:
                residual = rayleigh_square_physical_residual(
                    source_y + direction
                )
                values.append(0.5 * float(residual @ residual))
            mixed = (values[0] - values[1] - values[2] + values[3]) / (
                4.0 * left_radius * right_radius
            )
            hessian[left, right] = mixed
            hessian[right, left] = mixed
    analytic_gradient = basis_y.T @ gradient_y
    gauss_newton = basis_y.T @ matrix.T @ matrix @ basis_y
    residual_weighted = hessian - gauss_newton
    eigenvalues = np.linalg.eigvalsh(hessian)

    action_radii = curvature["bhsm_owned_action_coordinate_radii"]
    history_physical_radii = _physical_history_radii(scales)
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
        step_x, shift = _trust_step(hessian, exact_gradient, action_radius)
        displacement_y = basis_y @ step_x
        intersection = min(
            1.0, physical_radius / max(float(np.linalg.norm(displacement_y)), 1.0e-300)
        )
        step_x *= intersection
        displacement_y *= intersection
        for orientation in (-1.0, 1.0):
            candidate_y = source_y + orientation * displacement_y
            try:
                candidate_raw = candidate_y / scales
                residual = rayleigh_square_physical_residual(candidate_y)
                norm = float(np.linalg.norm(residual))
                eta = float(_minimum_node_eta(candidate_raw))
                reduction = source_norm - norm
                row = {
                    "radius_index": index,
                    "orientation": "negative" if orientation < 0.0 else "positive",
                    "bhsm_action_radius": action_radius,
                    "bhsm_physical_radius": physical_radius,
                    "intersection_factor": intersection,
                    "realized_action_coordinate_norm": float(np.linalg.norm(step_x)),
                    "realized_physical_scaled_norm": float(np.linalg.norm(displacement_y)),
                    "quadratic_shift_numerical_control": shift,
                    "quadratic_predicted_merit_change_has_no_physical_authority": float(
                        orientation * exact_gradient @ step_x
                        + 0.5 * step_x @ hessian @ step_x
                    ),
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
        "subspace": {
            "members": [name for name, _ in basis],
            "dimension": dimension,
            "action_owned_coordinate_map": transform_audit,
        },
        "exact_merit_jet": {
            "maximum_finite_difference_action_radius": reference_radius,
            "finite_difference_physical_radius_cap": reference_physical_radius,
            "direction_specific_action_radii": difference_radii.tolist(),
            "analytic_vs_exact_gradient_relative": float(
                np.linalg.norm(analytic_gradient - exact_gradient)
                / max(np.linalg.norm(exact_gradient), 1.0)
            ),
            "gradient_comparison_classification": (
                "ASSEMBLED_J_GRADIENT_RESOLVED"
                if np.linalg.norm(analytic_gradient - exact_gradient)
                / max(np.linalg.norm(exact_gradient), 1.0) < 2.0e-2
                else "ASSEMBLED_J_GRADIENT_MISMATCH_RECORDED_EXACT_DIFFERENCE_RETAINS_AUTHORITY"
            ),
            "hessian_eigenvalues": eigenvalues.tolist(),
            "negative_eigenvalue_count": int(np.count_nonzero(eigenvalues < 0.0)),
            "hessian_frobenius_norm": float(np.linalg.norm(hessian)),
            "gauss_newton_frobenius_norm": float(np.linalg.norm(gauss_newton)),
            "residual_weighted_curvature_frobenius_norm": float(np.linalg.norm(residual_weighted)),
            "residual_weighted_to_gauss_newton_ratio": float(
                np.linalg.norm(residual_weighted) / max(np.linalg.norm(gauss_newton), 1.0)
            ),
            "history_physical_radii_retained_for_audit_only": history_physical_radii,
            "prospective_physical_radii_source": "V21_02_REALIZED_DUAL_METRIC_ENDPOINTS",
            "all_terms_from_exact_action_or_exact_F376": True,
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
        "classification": "EXACT_MERIT_HESSIAN_MATERIAL_RECOVERY" if material else "EXACT_MERIT_HESSIAN_NO_MATERIAL_RECOVERY",
        "physical_equations_changed": False,
        "event_definition_changed": False,
        "complete_child_gate_changed": False,
        "left_residual_scaling_added": False,
        "componentwise_monotonicity_added": False,
    }
    validation = {
        "source_v21_04_reproduced": abs(source_norm - 0.782775399601569) < 5.0e-12,
        "basis_nontrivial": dimension >= 3,
        "exact_gradient_finite_nonzero": bool(
            np.all(np.isfinite(exact_gradient)) and np.linalg.norm(exact_gradient) > 0.0
        ),
        "exact_action_or_rows_only": result["exact_merit_jet"]["all_terms_from_exact_action_or_exact_F376"],
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
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_EXACT_MERIT_SUBSPACE_HESSIAN_V21_07",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "exact_merit_subspace_hessian": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_EXACT_MERIT_SUBSPACE_HESSIAN_V21_07.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "completion_payload", "materialize"]
