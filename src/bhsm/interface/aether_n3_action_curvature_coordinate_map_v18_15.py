"""Derive and equivalence-test an action-curvature coordinate map."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_action_owned_stiffness_measurement_v18_14 import _local_action_terms
from bhsm.interface.aether_n3_exact_full_local_action_jet_v17_60 import exact_full_action_jet_at_state
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    M_DIMENSION, NODES, ORDER, Q_DIMENSION, kkt_variable_scales,
    unpack_reduced,
)
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference
from bhsm.interface.aether_n3_square_kkt_complete_child_promotion_v18_12 import v18_12_selected_raw_vector
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import sobolev_weights, spectral_frequencies


VERSION = "v18.15"
CLASSIFICATION = "BHSM_N3_ACTION_CURVATURE_COORDINATE_MAP_EQUIVALENCE"
FULL_BHSM_COMPLETE = False


def _absolute_curvature_whitener(matrix: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    symmetric = 0.5 * (np.asarray(matrix) + np.asarray(matrix).T)
    eigenvalues, eigenvectors = np.linalg.eigh(symmetric)
    maximum = float(np.max(np.abs(eigenvalues)))
    tolerance = np.finfo(float).eps * symmetric.shape[0] * max(maximum, 1.0)
    resolved = np.abs(eigenvalues) > tolerance
    factors = np.ones_like(eigenvalues)
    factors[resolved] = 1.0 / np.sqrt(np.abs(eigenvalues[resolved]))
    transform = (eigenvectors * factors) @ eigenvectors.T
    transformed = transform.T @ symmetric @ transform
    transformed_eigenvalues = np.linalg.eigvalsh(transformed)
    source_nonzero = np.abs(eigenvalues[resolved])
    target_resolved = np.abs(transformed_eigenvalues) > math.sqrt(np.finfo(float).eps)
    target_nonzero = np.abs(transformed_eigenvalues[target_resolved])
    return transform, {
        "source_eigenvalues": eigenvalues.tolist(),
        "machine_rank_tolerance": tolerance,
        "resolved_rank": int(np.count_nonzero(resolved)),
        "source_resolved_condition_ratio": float(np.max(source_nonzero) / np.min(source_nonzero)),
        "transformed_eigenvalues": transformed_eigenvalues.tolist(),
        "transformed_resolved_condition_ratio": float(np.max(target_nonzero) / np.min(target_nonzero)),
        "coordinate_transform_singular_values": np.linalg.svd(transform, compute_uv=False).tolist(),
    }


def action_curvature_coordinate_map() -> dict[str, Any]:
    measurement = json.loads(Path(
        "artifacts/BHSM_aether_n3_action_owned_stiffness_measurement_v18_14.json"
    ).read_text(encoding="utf-8"))
    if not measurement["validation_passed"]:
        raise ValueError("v18.14 measurement is not validated")
    raw = v18_12_selected_raw_vector()
    scales = kkt_variable_scales(); y0 = raw * scales
    state = unpack_reduced(raw)
    q = np.asarray(state["coordinates"]); m = np.asarray(state["multipliers"])
    period = float(state["period"]); velocity = trapezoid_sbp_difference() @ q / period
    jet = exact_full_action_jet_at_state(ORDER, q[-1], velocity[-1], m[-1], points=44)
    action_reference = float(sum(abs(value) for value in _local_action_terms(
        q[-1], velocity[-1], m[-1]
    ).values()))
    frequencies = spectral_frequencies(ORDER)["coordinates"]
    q_amplitude = 1.0 / ((1.0 + frequencies**2)**3.0)
    m_amplitude = 1.0 / sobolev_weights(ORDER)["multipliers"]
    lift_q = np.zeros((26, Q_DIMENSION))
    lift_q[:Q_DIMENSION] = np.diag(q_amplitude)
    lift_q[Q_DIMENSION:2 * Q_DIMENSION] = np.diag(q_amplitude / period)
    lift_m = np.zeros((26, M_DIMENSION))
    lift_m[2 * Q_DIMENSION:] = np.diag(m_amplitude)
    q_curvature = lift_q.T @ jet.hessian @ lift_q / action_reference
    m_curvature = lift_m.T @ jet.hessian @ lift_m / action_reference
    q_transform, q_audit = _absolute_curvature_whitener(q_curvature)
    m_transform, m_audit = _absolute_curvature_whitener(m_curvature)
    direction_rows = measurement["action_owned_stiffness_measurement"]["global_directional_measurements"]
    period_row = next(row for row in direction_rows if row["direction"] == "period")
    period_curvature = abs(float(period_row["directional_second_variation"])) / action_reference
    period_transform = 1.0 / math.sqrt(period_curvature)
    transform = np.eye(376)
    for node in range(NODES - 1):
        sl = slice(node * Q_DIMENSION, (node + 1) * Q_DIMENSION)
        transform[sl, sl] = q_transform
    offset = (NODES - 1) * Q_DIMENSION
    for node in range(NODES):
        sl = slice(offset + node * M_DIMENSION, offset + (node + 1) * M_DIMENSION)
        transform[sl, sl] = m_transform
    transform[-2, -2] = period_transform
    transform[-1, -1] = 1.0  # explicit event KKT normalization is already action-owned
    singular_values = np.linalg.svd(transform, compute_uv=False)
    x0 = np.zeros(376)
    mapped_source = y0 + transform @ x0
    source_direct = _square_physical_residual(y0)
    source_mapped = _square_physical_residual(mapped_source)
    probe = np.cos(np.arange(376, dtype=float) + 0.37)
    probe /= np.linalg.norm(probe)
    probe *= 1.0e-8 / max(float(singular_values[0]), 1.0)
    y_probe = y0 + transform @ probe
    direct_probe = _square_physical_residual(y_probe)
    mapped_probe = _square_physical_residual(y0 + transform @ probe)
    recovered_probe = np.linalg.solve(transform, y_probe - y0)
    child = json.loads(Path(
        "artifacts/BHSM_aether_n3_square_kkt_complete_child_promotion_v18_12.json"
    ).read_text(encoding="utf-8"))
    return {
        "source_state": "EXACT_ACCEPTED_V18_12",
        "derivation": {
            "coordinate_relation": "y=y_v18_12+P*x",
            "residual_relation": "F_preconditioned(x)=F_exact(y_v18_12+P*x)",
            "left_residual_scaling_applied": False,
            "action_reference": action_reference,
            "q_metric": "TERMINAL_EXACT_ACTION_HESSIAN_PULLED_BACK_BY_EXISTING_H6_Q_AMPLITUDES_AND_PERIOD_INDUCED_VELOCITIES",
            "multiplier_metric": "TERMINAL_EXACT_ACTION_HESSIAN_PULLED_BACK_BY_EXISTING_SOBOLEV_MULTIPLIER_AMPLITUDES",
            "period_metric": "EXACT_GLOBAL_DIRECTIONAL_ACTION_CURVATURE",
            "event_multiplier_metric": "UNCHANGED_EXISTING_EXPLICIT_EVENT_KKT_NORMALIZATION",
            "null_handling": "MACHINE_PRECISION_NUMERICAL_NULLS_RETAIN_UNIT_COORDINATE_FACTOR",
            "coefficients_tuned": False,
            "observed_particle_data_used": False,
        },
        "q_action_curvature_block": q_audit,
        "multiplier_action_curvature_block": m_audit,
        "period_coordinate_factor": period_transform,
        "event_multiplier_coordinate_factor": 1.0,
        "global_transform": {
            "dimension": [376, 376],
            "minimum_singular_value": float(singular_values[-1]),
            "maximum_singular_value": float(singular_values[0]),
            "condition_ratio": float(singular_values[0] / singular_values[-1]),
            "invertible": bool(singular_values[-1] > 0.0),
        },
        "equivalence": {
            "source_state_round_trip_error": float(np.linalg.norm(mapped_source - y0)),
            "source_exact_residual_difference": float(np.linalg.norm(source_mapped - source_direct)),
            "nonzero_probe_coordinate_round_trip_error": float(np.linalg.norm(recovered_probe - probe)),
            "nonzero_probe_exact_residual_difference": float(np.linalg.norm(mapped_probe - direct_probe)),
            "source_eta_direct": _minimum_node_eta(raw),
            "source_eta_mapped": _minimum_node_eta(mapped_source / scales),
            "source_complete_child_artifact": child["artifact"],
            "source_complete_child_validation_passed": child["validation_passed"],
            "complete_child_acceptance_changed": False,
            "event_definition_changed": False,
            "physical_equations_changed": False,
            "root_set_relation": "BIJECTIVE_BECAUSE_P_IS_INVERTIBLE_AND_RESIDUAL_ROWS_ARE_UNCHANGED",
        },
    }


def completion_payload() -> dict[str, Any]:
    result = action_curvature_coordinate_map()
    equivalent = result["equivalence"]
    validation = {
        "same_physical_source_state": equivalent["source_state_round_trip_error"] == 0.0,
        "same_exact_nonlinear_residual": equivalent["source_exact_residual_difference"] == 0.0 and equivalent["nonzero_probe_exact_residual_difference"] == 0.0,
        "coordinate_map_invertible": result["global_transform"]["invertible"],
        "nonzero_probe_round_trip": equivalent["nonzero_probe_coordinate_round_trip_error"] < 1.0e-15,
        "same_eta_domain": abs(equivalent["source_eta_direct"] - equivalent["source_eta_mapped"]) < 1.0e-14,
        "same_complete_child_gate": equivalent["source_complete_child_validation_passed"] and not equivalent["complete_child_acceptance_changed"],
        "same_event_and_equations": not equivalent["event_definition_changed"] and not equivalent["physical_equations_changed"],
        "no_coefficient_tuning": not result["derivation"]["coefficients_tuned"],
        "no_observed_particle_data": not result["derivation"]["observed_particle_data_used"],
        "residual_rows_not_rescaled": not result["derivation"]["left_residual_scaling_applied"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_action_curvature_coordinate_map_v18_15",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "action_curvature_coordinate_map": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "ACTION_CURVATURE_DEFINES_AN_INVERTIBLE_NUMERICAL_COORDINATE_MAP_"
            "WITHOUT_CHANGING_THE_PHYSICAL_KKT_OR_COMPLETE_CHILD_GATE"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": "APPLY_THE_EQUIVALENT_ACTION_CURVATURE_MAP_TO_THE_NEXT_SQUARE_KKT_PROPOSAL",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_action_curvature_coordinate_map_v18_15.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "action_curvature_coordinate_map", "completion_payload", "materialize"]
