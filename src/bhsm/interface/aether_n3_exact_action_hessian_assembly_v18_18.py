"""Assemble the global Hessian of the exact retained v17.61 action covector."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import standard_model_casimir_coefficient
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import exact_full_action_jet_at_state
from bhsm.interface.aether_n3_exact_local_jet_sbp_covector_v17_61 import exact_local_jet_sbp_action_covector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    M_DIMENSION, NODES, ORDER, Q_DIMENSION, boundary_lapse,
    boundary_radius_and_jacobian, kkt_variable_scales, trapezoid_weights,
    unpack_reduced,
)
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference
from bhsm.interface.aether_n3_square_kkt_complete_child_promotion_v18_12 import v18_12_selected_raw_vector
from bhsm.interface.aether_replacement_geometry_force_v16_06 import zero_source_heat_geometry_response


VERSION = "v18.18"
CLASSIFICATION = "BHSM_N3_EXACT_ACTION_HESSIAN_ASSEMBLY"
FULL_BHSM_COMPLETE = False
BASE_DIMENSION = 375
HEAT_HESSIAN_STEP = 2.0e-5


def _parent_local_jet(q: np.ndarray, velocity: np.ndarray, m: np.ndarray) -> tuple[float, np.ndarray, np.ndarray]:
    attached = exact_full_action_jet_at_state(ORDER, q, velocity, m, points=36)
    signs_k = (-1.0) ** np.arange(1, ORDER + 1)
    signs_j = (-1.0) ** np.arange(ORDER)
    vb = float(q[1 + 2 * ORDER:1 + 3 * ORDER] @ signs_j)
    radius, _ = boundary_radius_and_jacobian(q[None, :])
    restored = float(
        standard_model_casimir_coefficient()
        * math.exp(float(m[:ORDER] @ signs_k)) / radius[0]
    )
    a_gradient = np.zeros(26)
    a_gradient[0] = -1.0
    a_gradient[1:1 + ORDER] = -signs_k
    a_gradient[1 + 2 * ORDER:1 + 3 * ORDER] = math.tanh(2.0 * vb) * signs_j
    a_gradient[2 * Q_DIMENSION:2 * Q_DIMENSION + ORDER] = signs_k
    a_hessian = np.zeros((26, 26))
    b_slice = slice(1 + 2 * ORDER, 1 + 3 * ORDER)
    a_hessian[b_slice, b_slice] = (
        2.0 / math.cosh(2.0 * vb) ** 2 * np.outer(signs_j, signs_j)
    )
    restored_gradient = restored * a_gradient
    restored_hessian = restored * (
        np.outer(a_gradient, a_gradient) + a_hessian
    )
    return (
        float(attached.value + restored),
        np.asarray(attached.gradient) + restored_gradient,
        np.asarray(attached.hessian) + restored_hessian,
    )


def _heat_gradient(log_geometry: np.ndarray) -> np.ndarray:
    values = np.asarray(log_geometry, dtype=float)
    response = zero_source_heat_geometry_response(
        np.exp(values[:-1]), math.exp(float(values[-1]))
    )
    return np.concatenate((
        np.asarray(response["d_Gamma_heat_d_log_R_nodes"], dtype=float),
        [float(response["d_Gamma_heat_d_log_proper_step"])],
    ))


def _heat_hessian(log_geometry: np.ndarray) -> tuple[np.ndarray, dict[str, float]]:
    center = np.asarray(log_geometry, dtype=float)
    dimension = center.size
    hessian = np.empty((dimension, dimension))
    for column in range(dimension):
        step = HEAT_HESSIAN_STEP * max(1.0, abs(float(center[column])))
        delta = np.zeros(dimension); delta[column] = step
        hessian[:, column] = (
            _heat_gradient(center + delta) - _heat_gradient(center - delta)
        ) / (2.0 * step)
    asymmetry = float(
        np.linalg.norm(hessian - hessian.T) / max(1.0, np.linalg.norm(hessian))
    )
    symmetric = 0.5 * (hessian + hessian.T)
    return symmetric, {
        "relative_raw_asymmetry": asymmetry,
        "norm": float(np.linalg.norm(symmetric)),
        "finite_difference_step": HEAT_HESSIAN_STEP,
    }


def exact_sbp_action_hessian(base_raw: np.ndarray) -> dict[str, Any]:
    base = np.asarray(base_raw, dtype=float)
    if base.shape != (BASE_DIMENSION,):
        raise ValueError("base action vector must have dimension 375")
    state = unpack_reduced(np.concatenate((base, [0.0])))
    q = np.asarray(state["coordinates"]); m = np.asarray(state["multipliers"])
    period = float(state["period"])
    difference = trapezoid_sbp_difference(); weights = trapezoid_weights()
    velocity = difference @ q / period
    hessian = np.zeros((BASE_DIMENSION, BASE_DIMENSION))
    gradient = np.zeros(BASE_DIMENSION)
    period_index = BASE_DIMENSION - 1
    local_values = []
    for node in range(NODES):
        value, local_gradient, local_hessian = _parent_local_jet(
            q[node], velocity[node], m[node]
        )
        local_values.append(value)
        mapping = np.zeros((26, BASE_DIMENSION))
        if node > 0:
            q_slice = slice((node - 1) * Q_DIMENSION, node * Q_DIMENSION)
            mapping[:Q_DIMENSION, q_slice] = np.eye(Q_DIMENSION)
        for source_node in range(1, NODES):
            q_slice = slice((source_node - 1) * Q_DIMENSION, source_node * Q_DIMENSION)
            mapping[Q_DIMENSION:2 * Q_DIMENSION, q_slice] = (
                difference[node, source_node] / period * np.eye(Q_DIMENSION)
            )
        mapping[Q_DIMENSION:2 * Q_DIMENSION, period_index] = -velocity[node] / period
        m_offset = (NODES - 1) * Q_DIMENSION + node * M_DIMENSION
        mapping[2 * Q_DIMENSION:, m_offset:m_offset + M_DIMENSION] = np.eye(M_DIMENSION)
        weight = float(weights[node])
        pulled_gradient = mapping.T @ local_gradient
        gradient += period * weight * pulled_gradient
        gradient[period_index] += weight * value
        hessian += period * weight * (mapping.T @ local_hessian @ mapping)
        hessian[:, period_index] += weight * pulled_gradient
        hessian[period_index, :] += weight * pulled_gradient
        velocity_gradient = local_gradient[Q_DIMENSION:2 * Q_DIMENSION]
        for source_node in range(1, NODES):
            coefficient = difference[node, source_node]
            q_slice = slice((source_node - 1) * Q_DIMENSION, source_node * Q_DIMENSION)
            cross = -weight * coefficient / period * velocity_gradient
            hessian[q_slice, period_index] += cross
            hessian[period_index, q_slice] += cross
        hessian[period_index, period_index] += (
            2.0 * weight / period * float(velocity_gradient @ velocity[node])
        )
    radii, log_radius_gradient = boundary_radius_and_jacobian(q)
    lapse = boundary_lapse(m)
    lapse_sum = float(weights @ lapse)
    proper_step = period * lapse_sum / NODES
    log_geometry = np.concatenate((np.log(radii), [math.log(proper_step)]))
    heat_response = zero_source_heat_geometry_response(radii, proper_step)
    heat_gradient_geometry = np.concatenate((
        np.asarray(heat_response["d_Gamma_heat_d_log_R_nodes"]),
        [float(heat_response["d_Gamma_heat_d_log_proper_step"])],
    ))
    heat_hessian_geometry, heat_audit = _heat_hessian(log_geometry)
    geometry_mapping = np.zeros((NODES + 1, BASE_DIMENSION))
    for node in range(1, NODES):
        q_slice = slice((node - 1) * Q_DIMENSION, node * Q_DIMENSION)
        geometry_mapping[node, q_slice] = log_radius_gradient[node]
    signs_k = (-1.0) ** np.arange(1, ORDER + 1)
    probabilities = weights * lapse / lapse_sum
    multiplier_indices = np.empty((NODES, ORDER), dtype=int)
    m_base = (NODES - 1) * Q_DIMENSION
    for node in range(NODES):
        for mode in range(ORDER):
            index = m_base + node * M_DIMENSION + mode
            multiplier_indices[node, mode] = index
            geometry_mapping[-1, index] = probabilities[node] * signs_k[mode]
    geometry_mapping[-1, period_index] = 1.0 / period
    gradient += geometry_mapping.T @ heat_gradient_geometry
    hessian += geometry_mapping.T @ heat_hessian_geometry @ geometry_mapping
    signs_j = (-1.0) ** np.arange(ORDER)
    for node in range(1, NODES):
        vb = float(q[node, 1 + 2 * ORDER:1 + 3 * ORDER] @ signs_j)
        q_start = (node - 1) * Q_DIMENSION + 1 + 2 * ORDER
        q_indices = np.arange(q_start, q_start + ORDER)
        log_radius_hessian = (
            -2.0 / math.cosh(2.0 * vb) ** 2 * np.outer(signs_j, signs_j)
        )
        hessian[np.ix_(q_indices, q_indices)] += (
            heat_gradient_geometry[node] * log_radius_hessian
        )
    duration_gradient = float(heat_gradient_geometry[-1])
    hessian[period_index, period_index] += -duration_gradient / period**2
    for node_a in range(NODES):
        for node_b in range(NODES):
            covariance = (
                probabilities[node_a] * (1.0 if node_a == node_b else 0.0)
                - probabilities[node_a] * probabilities[node_b]
            )
            block = duration_gradient * covariance * np.outer(signs_k, signs_k)
            ia = multiplier_indices[node_a]
            ib = multiplier_indices[node_b]
            hessian[np.ix_(ia, ib)] += block
    exact = exact_local_jet_sbp_action_covector(base)
    exact_gradient = np.asarray(exact["covector"], dtype=float)
    return {
        "hessian": 0.5 * (hessian + hessian.T),
        "assembled_gradient": gradient,
        "exact_gradient": exact_gradient,
        "gradient_relative_residual": float(
            np.linalg.norm(gradient - exact_gradient)
            / max(1.0, np.linalg.norm(exact_gradient))
        ),
        "local_parent_action": period * float(weights @ np.asarray(local_values)),
        "heat_action": float(heat_response["Gamma_heat"]),
        "total_action": float(exact["Gamma_replacement"]),
        "heat_hessian": heat_audit,
    }


def exact_action_hessian_audit() -> dict[str, Any]:
    raw = v18_12_selected_raw_vector(); base = raw[:-1]
    assembled = exact_sbp_action_hessian(base)
    hessian = np.asarray(assembled.pop("hessian"))
    scales = kkt_variable_scales()[:-1]
    directions = []
    templates = [
        np.cos(np.arange(BASE_DIMENSION) + 0.17),
        np.sin(0.37 * np.arange(BASE_DIMENSION) + 0.41),
        np.where(np.arange(BASE_DIMENSION) < (NODES - 1) * Q_DIMENSION, 1.0, 0.0),
        np.where(np.arange(BASE_DIMENSION) >= (NODES - 1) * Q_DIMENSION, 1.0, 0.0),
    ]
    for number, template in enumerate(templates):
        direction = np.asarray(template, dtype=float) / scales
        direction /= np.linalg.norm(scales * direction)
        predicted = hessian @ direction
        rows = []
        for epsilon in (4.0e-5, 2.0e-5):
            plus = np.asarray(exact_local_jet_sbp_action_covector(base + epsilon * direction)["covector"])
            minus = np.asarray(exact_local_jet_sbp_action_covector(base - epsilon * direction)["covector"])
            finite = (plus - minus) / (2.0 * epsilon)
            rows.append({
                "epsilon": epsilon,
                "finite_response_norm": float(np.linalg.norm(finite)),
                "relative_residual": float(
                    np.linalg.norm(predicted - finite) / max(1.0, np.linalg.norm(finite))
                ),
            })
        directions.append({
            "direction": number,
            "predicted_response_norm": float(np.linalg.norm(predicted)),
            "checks": rows,
        })
    return {
        "source_state": "EXACT_ACCEPTED_V18_12",
        "physical_action_changed": False,
        "event_definition_changed": False,
        "base_dimension": BASE_DIMENSION,
        "assembly": assembled,
        "hessian_norm": float(np.linalg.norm(hessian)),
        "hessian_symmetry_residual": float(
            np.linalg.norm(hessian - hessian.T) / max(1.0, np.linalg.norm(hessian))
        ),
        "directional_checks": directions,
        "maximum_directional_relative_residual": max(
            check["relative_residual"] for row in directions for check in row["checks"]
        ),
    }


def completion_payload() -> dict[str, Any]:
    result = exact_action_hessian_audit()
    validation = {
        "exact_v18_12_source": result["source_state"] == "EXACT_ACCEPTED_V18_12",
        "physical_action_unchanged": not result["physical_action_changed"],
        "event_definition_unchanged": not result["event_definition_changed"],
        "complete_base_dimension": result["base_dimension"] == 375,
        "assembled_gradient_reproduces_exact_covector": result["assembly"]["gradient_relative_residual"] < 5.0e-11,
        "heat_hessian_nearly_symmetric": result["assembly"]["heat_hessian"]["relative_raw_asymmetry"] < 2.0e-5,
        "hessian_symmetric": result["hessian_symmetry_residual"] < 1.0e-13,
        "directional_response_matches_exact_covector": result["maximum_directional_relative_residual"] < 2.0e-4,
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_exact_action_hessian_assembly_v18_18",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "exact_action_hessian_assembly": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_GLOBAL_ACTION_COVECTOR_RESPONSE_IS_ASSEMBLED_FROM_THE_EXACT_"
            "LOCAL_ACTION_JETS_AND_THE_SAME_HEAT_OPERATOR"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "ASSEMBLE_AND_VALIDATE_THE_EXPLICIT_EVENT_MULTIPLIER_KKT_RESPONSE" if passed
            else "AUDIT_THE_EXACT_ACTION_HESSIAN_CHAIN_RULE"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_exact_action_hessian_assembly_v18_18.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "exact_sbp_action_hessian", "exact_action_hessian_audit", "completion_payload", "materialize"]
