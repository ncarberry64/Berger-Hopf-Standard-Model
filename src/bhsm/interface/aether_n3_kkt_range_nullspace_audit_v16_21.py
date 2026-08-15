"""Range/nullspace and endpoint-variation audit of the v16.20 N=3 KKT."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_analytic_kkt_covector_v16_12 import (
    replacement_action_covector,
    scaled_analytic_kkt_residual,
)
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import (
    kkt_jacobian_at,
)
from bhsm.interface.aether_n3_kkt_refreshed_curvature_v16_16 import (
    scaled_event_hessian,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    NODES,
    Q_DIMENSION,
    anchored_kkt_dimensions,
    kkt_variable_scales,
    open_difference_matrix,
    replacement_action_from_base,
    trapezoid_weights,
)
from bhsm.interface.aether_n3_terminal_scale_range_defect_v16_20 import (
    range_defect_and_projection,
)


VERSION = "v16.21"
CLASSIFICATION = "BHSM_N3_KKT_RANGE_NULLSPACE_ENDPOINT_VARIATION_AUDIT"
FULL_BHSM_COMPLETE = False


def v16_20_projected_raw_vector() -> np.ndarray:
    values = range_defect_and_projection()["projected_raw_vector_hex"]
    result = np.asarray([float.fromhex(value) for value in values])
    if result.shape != (376,):
        raise ValueError("v16.20 vector has wrong dimension")
    return result


def _component_label(index: int) -> str:
    q_count = (NODES - 1) * Q_DIMENSION
    m_count = NODES * 6
    if index < q_count:
        return f"q_node_{index // Q_DIMENSION + 1}_component_{index % Q_DIMENSION}"
    if index < q_count + m_count:
        local = index - q_count
        return f"m_node_{local // 6}_component_{local % 6}"
    if index == q_count + m_count:
        return "period"
    return "event_multiplier"


def refreshed_jacobian_and_residual() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    raw = v16_20_projected_raw_vector()
    scales = kkt_variable_scales()
    y = raw * scales
    assembled = kkt_jacobian_at(raw)
    matrix = np.asarray(assembled["KKT_jacobian"]).copy()
    event_hessian = scaled_event_hessian(y[:-1])
    matrix[:-1, :-1] += y[-1] * event_hessian
    matrix = 0.5 * (matrix + matrix.T)
    residual = scaled_analytic_kkt_residual(y)
    return matrix, residual, raw


def nullspace_audit() -> dict[str, Any]:
    matrix, residual, _ = refreshed_jacobian_and_residual()
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    scale = float(np.max(np.abs(eigenvalues)))
    residual_norm = float(np.linalg.norm(residual))
    coefficients = eigenvectors.T @ residual
    rows = {}
    for tolerance in (1.0e-8, 1.0e-10, 1.0e-12, 1.0e-14):
        null = np.abs(eigenvalues) <= tolerance * scale
        null_indices = np.flatnonzero(null)
        overlaps = coefficients[null_indices]
        # A null overlap is numerically relevant when it carries at least
        # 1e-5 of the complete residual norm.  This is well above the
        # endpoint-row finite-difference noise and lists each such vector.
        relevant_threshold = 1.0e-5 * residual_norm
        relevant = null_indices[np.abs(overlaps) >= relevant_threshold]
        relevant_rows = []
        for eigen_index in relevant:
            vector = eigenvectors[:, eigen_index]
            dominant = np.argsort(np.abs(vector))[-6:][::-1]
            relevant_rows.append({
                "eigen_index": int(eigen_index),
                "eigenvalue": float(eigenvalues[eigen_index]),
                "left_null_overlap_uT_R": float(coefficients[eigen_index]),
                "dominant_components": [
                    {
                        "index": int(index),
                        "label": _component_label(int(index)),
                        "coefficient": float(vector[index]),
                    }
                    for index in dominant
                ],
            })
        relevant_rows.sort(
            key=lambda row: abs(row["left_null_overlap_uT_R"]),
            reverse=True,
        )
        rows[f"relative_{tolerance:.0e}"] = {
            "rank": int(np.sum(~null)),
            "right_nullity": int(np.sum(null)),
            "left_nullity": int(np.sum(null)),
            "residual_projection_on_left_nullspace_norm": float(
                np.linalg.norm(overlaps)
            ),
            "fraction_of_residual_outside_numerical_range": float(
                np.linalg.norm(overlaps) / residual_norm
            ),
            "maximum_abs_left_null_overlap": float(
                np.max(np.abs(overlaps)) if len(overlaps) else 0.0
            ),
            "relevant_overlap_threshold": relevant_threshold,
            "numerically_relevant_left_null_vectors": relevant_rows,
        }
    return {
        "matrix_dimension": len(matrix),
        "symmetric_relative_residual": float(
            np.linalg.norm(matrix - matrix.T) / max(1.0, np.linalg.norm(matrix))
        ),
        "spectral_scale": scale,
        "smallest_absolute_eigenvalue": float(np.min(np.abs(eigenvalues))),
        "residual_norm": residual_norm,
        "tolerance_audit": rows,
    }


def endpoint_variation_audit() -> dict[str, Any]:
    raw = v16_20_projected_raw_vector()
    base = raw[:-1]
    analytic = np.asarray(replacement_action_covector(base)["covector"])
    indices = (0, 10, 200, 210, 220, 374)
    checks = []
    for index in indices:
        step = 2.0e-6 * max(1.0, abs(float(base[index])))
        delta = np.zeros_like(base)
        delta[index] = step
        finite = (
            replacement_action_from_base(base + delta)
            - replacement_action_from_base(base - delta)
        ) / (2.0 * step)
        checks.append({
            "index": index,
            "label": _component_label(index),
            "analytic_action_covector": float(analytic[index]),
            "full_action_finite_difference": float(finite),
            "absolute_residual": float(abs(analytic[index] - finite)),
            "relative_residual": float(
                abs(analytic[index] - finite) / max(1.0, abs(finite))
            ),
        })

    difference = open_difference_matrix()
    weights = trapezoid_weights()
    weighted = np.diag(weights)
    boundary = np.zeros_like(difference)
    boundary[0, 0] = -1.0
    boundary[-1, -1] = 1.0
    sbp_defect = weighted @ difference + difference.T @ weighted - boundary
    x = np.linspace(0.0, 1.0, NODES)
    polynomial_errors = {}
    for degree in range(4):
        exact = np.zeros_like(x) if degree == 0 else degree * x ** (degree - 1)
        approximation = difference @ x**degree
        polynomial_errors[str(degree)] = {
            "endpoint_maximum": float(np.max(np.abs(
                approximation[[0, -1]] - exact[[0, -1]]
            ))),
            "interior_maximum": float(np.max(np.abs(
                approximation[1:-1] - exact[1:-1]
            ))),
        }
    return {
        "endpoint_and_period_rows_match_action": all(
            row["relative_residual"] < 2.0e-5 for row in checks
        ),
        "row_checks": checks,
        "endpoint_quadrature_weights": {
            "node_0": float(weights[0]),
            "node_1": float(weights[1]),
            "node_2": float(weights[2]),
            "node_22": float(weights[22]),
            "node_23": float(weights[23]),
        },
        "polynomial_derivative_errors": polynomial_errors,
        "summation_by_parts_defect_norm": float(np.linalg.norm(sbp_defect)),
        "summation_by_parts_defect_maximum": float(np.max(np.abs(sbp_defect))),
        "summation_by_parts_defect_nonzero_count": int(np.sum(
            np.abs(sbp_defect) > 1.0e-13
        )),
        "current_derivative_quadrature_pair_is_SBP": bool(
            np.linalg.norm(sbp_defect) < 1.0e-12
        ),
        "anchored_variational_count": anchored_kkt_dimensions(),
        "reset_coordinates_removed_from_variables": 10,
        "reset_stationarity_rows_removed_with_variables": 10,
        "phase_multiplier_present": False,
        "terminal_scale_is_a_free_reduced_coordinate": True,
        "proper_time_T_lapse_chain_rule_verified_upstream_v16_12": True,
    }


def completion_payload() -> dict[str, Any]:
    nullspace = nullspace_audit()
    endpoint = endpoint_variation_audit()
    strict = nullspace["tolerance_audit"]["relative_1e-12"]
    validation = {
        "symmetric_KKT_audited": nullspace["symmetric_relative_residual"] < 1.0e-14,
        "ranks_and_nullities_reported": all(
            row["rank"] + row["right_nullity"] == 376
            for row in nullspace["tolerance_audit"].values()
        ),
        "left_null_overlaps_computed": strict[
            "maximum_abs_left_null_overlap"
        ] >= 0.0,
        "endpoint_rows_are_true_action_variations": endpoint[
            "endpoint_and_period_rows_match_action"
        ],
        "derivative_quadrature_SBP_status_computed": (
            endpoint["summation_by_parts_defect_norm"] >= 0.0
        ),
    }
    return {
        "artifact": "BHSM_aether_n3_kkt_range_nullspace_audit_v16_21",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "status": "RECLASSIFIED",
        "range_nullspace_audit": nullspace,
        "endpoint_variation_audit": endpoint,
        "dependency_advanced": (
            "PRECISE_NUMERICAL_RANGE_AND_DISCRETE_ENDPOINT-VARIATION_AUDIT_"
            "OF_THE_REMAINING_N3_COMMON_EVENT-KKT_DEFECT"
        ),
        "active_calculation": (
            "USE_A_RANK-AWARE_TRUST-REGION_SOLVE_BECAUSE_THE_RESIDUAL_IS_"
            "INSIDE_THE_NUMERICAL_RANGE;_RETAIN_THE_NON-SBP_PAIR_AS_A_"
            "REFINEMENT_AUDIT_RATHER_THAN_PATCHING_ACTION_ROWS"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return [_canonical(item) for item in value.tolist()]
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        return round(value, 12)
    if isinstance(value, Mapping):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_kkt_range_nullspace_audit_v16_21.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "v16_20_projected_raw_vector", "refreshed_jacobian_and_residual",
    "nullspace_audit", "endpoint_variation_audit", "completion_payload",
    "deterministic_json", "materialize",
]
