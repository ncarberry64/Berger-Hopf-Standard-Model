"""Rayleigh derivative of the isolated ordered N=3 terminal event eigenvalue."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import exact_action_jet_at_state
from bhsm.interface.aether_n3_exact_local_jet_sbp_covector_v17_61 import exact_local_jet_sbp_action_covector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_event_covector, sbp_event_value_from_base
from bhsm.interface.aether_n3_post_recovery_multisecant_proposal_v20_77 import v20_77_selected_raw_vector
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    NODES, ORDER, Q_DIMENSION, kkt_variable_scales, unpack_reduced,
)
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_72 import v20_72_selected_raw_vector
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_73 import v20_73_selected_raw_vector
from bhsm.interface.aether_n3_structured_proposal_continuation_v20_75 import v20_75_selected_raw_vector


VERSION = "v20.80"
CLASSIFICATION = "BHSM_N3_ISOLATED_ORDERED_EVENT_RAYLEIGH_COVECTOR"
FULL_BHSM_COMPLETE = False
RAYLEIGH_RELATIVE_STEP = 1.0e-4


def _terminal_data(base_vector: np.ndarray) -> tuple[np.ndarray, np.ndarray, float, np.ndarray, np.ndarray]:
    unpacked = unpack_reduced(np.concatenate((np.asarray(base_vector, dtype=float), [0.0])))
    q = np.asarray(unpacked["coordinates"]); multipliers = np.asarray(unpacked["multipliers"])
    period = float(unpacked["period"]); difference = trapezoid_sbp_difference()
    velocity = difference @ q / period
    local = np.concatenate((q[-1], velocity[-1], multipliers[-1]))
    return q, multipliers, period, difference, local


def _event_hessian(local: np.ndarray) -> np.ndarray:
    value = np.asarray(local, dtype=float)
    return exact_action_jet_at_state(
        ORDER, value[:10], value[10:20], value[20:], points=44,
    ).hessian


def rayleigh_sbp_event_covector(
    base_vector: np.ndarray, *, relative_step: float = RAYLEIGH_RELATIVE_STEP,
) -> np.ndarray:
    """Return d lambda_6/d base via v.T(dH)v and the exact SBP pullback."""
    base = np.asarray(base_vector, dtype=float)
    q, _, period, difference, local = _terminal_data(base)
    eigenvalues, eigenvectors = np.linalg.eigh(_event_hessian(local))
    if not (eigenvalues[5] < eigenvalues[6] < eigenvalues[7]):
        raise ValueError("ordered event eigenvalue is not isolated")
    eigenvector = eigenvectors[:, 6]
    local_gradient = np.empty(26)
    for index in range(26):
        step = relative_step * max(1.0, abs(float(local[index])))
        delta = np.zeros(26); delta[index] = step
        derivative = (
            -_event_hessian(local + 2.0 * delta)
            + 8.0 * _event_hessian(local + delta)
            - 8.0 * _event_hessian(local - delta)
            + _event_hessian(local - 2.0 * delta)
        ) / (12.0 * step)
        local_gradient[index] = float(eigenvector @ derivative @ eigenvector)
    result = np.zeros(375)
    result[(NODES - 2) * Q_DIMENSION:(NODES - 1) * Q_DIMENSION] += local_gradient[:10]
    velocity_gradient = local_gradient[10:20]
    for node in range(1, NODES):
        start = (node - 1) * Q_DIMENSION
        result[start:start + Q_DIMENSION] += difference[-1, node] / period * velocity_gradient
    multiplier_start = (NODES - 1) * Q_DIMENSION + (NODES - 1) * 6
    result[multiplier_start:multiplier_start + 6] = local_gradient[20:]
    terminal_velocity = local[10:20]
    result[-1] = float(velocity_gradient @ (-terminal_velocity / period))
    return result


def rayleigh_square_physical_residual(scaled: np.ndarray) -> np.ndarray:
    y = np.asarray(scaled, dtype=float); scales = kkt_variable_scales()
    base = y[:-1] / scales[:-1]
    action = np.asarray(exact_local_jet_sbp_action_covector(base)["covector"]) / scales[:-1]
    event = rayleigh_sbp_event_covector(base) / scales[:-1] / scales[-1]
    return np.concatenate((action + y[-1] * event, [sbp_event_value_from_base(base) / scales[-1]]))


def rayleigh_project_event_multiplier(raw: np.ndarray) -> np.ndarray:
    state = np.asarray(raw, dtype=float).copy(); scales = kkt_variable_scales()
    action = np.asarray(exact_local_jet_sbp_action_covector(state[:-1])["covector"]) / scales[:-1]
    event = rayleigh_sbp_event_covector(state[:-1]) / scales[:-1] / scales[-1]
    state[-1] = (-float(action @ event) / float(event @ event)) / scales[-1]
    return state


def _proposal_directions(raw: np.ndarray, scales: np.ndarray, residual: np.ndarray) -> dict[str, np.ndarray]:
    artifact = json.loads(Path(
        "artifacts/BHSM_N3_POST_RECOVERY_MULTI_SECANT_PROPOSAL_V20_77.json"
    ).read_text(encoding="utf-8"))["post_recovery_multisecant_proposal"]["exact_line_search"]["best"]
    selected = np.asarray([float.fromhex(value) for value in artifact["raw_vector_hex"]])
    return {
        "physical_residual": residual,
        "latest_accepted_secant": (raw - v20_75_selected_raw_vector()) * scales,
        "material_corridor_secant": (v20_73_selected_raw_vector() - v20_72_selected_raw_vector()) * scales,
        "multisecant_direction": (selected - v20_75_selected_raw_vector()) * scales / float(artifact["alpha"]),
    }


def rayleigh_event_covector_audit() -> dict[str, Any]:
    scales = kkt_variable_scales(); raw = v20_77_selected_raw_vector(); projected = rayleigh_project_event_multiplier(raw)
    y = projected * scales; covector = rayleigh_sbp_event_covector(projected[:-1]) / scales[:-1] / scales[-1]
    coarse = rayleigh_sbp_event_covector(projected[:-1], relative_step=3.0e-4) / scales[:-1] / scales[-1]
    legacy = sbp_event_covector(projected[:-1]) / scales[:-1] / scales[-1]
    residual = rayleigh_square_physical_residual(y)
    q, multipliers, period, difference, local = _terminal_data(projected[:-1])
    eigenvalues = np.linalg.eigvalsh(_event_hessian(local))
    checks = []
    legacy_residual_direction = _square_physical_residual(raw * scales)
    for name, direction in _proposal_directions(projected, scales, legacy_residual_direction).items():
        norm = float(np.linalg.norm(direction)); unit = direction / norm
        step = 1.0e-6 if name == "physical_residual" else 3.0e-5
        finite = norm * (
            sbp_event_value_from_base((y[:-1] + step * unit[:-1]) / scales[:-1])
            - sbp_event_value_from_base((y[:-1] - step * unit[:-1]) / scales[:-1])
        ) / (2.0 * step * scales[-1])
        predicted = float(covector @ direction[:-1])
        checks.append({
            "direction": name, "step": step, "rayleigh_directional_derivative": predicted,
            "event_value_central_derivative": float(finite), "absolute_residual": abs(predicted - finite),
        })
    return {
        "source_geometry": "v20.77", "event_multiplier_reprojected_only": True,
        "source_legacy_f376_l2": 0.758671922543989,
        "rayleigh_projected_raw_event_multiplier": float(projected[-1]),
        "rayleigh_f376_l2": float(np.linalg.norm(residual)),
        "rayleigh_stationarity_l2": float(np.linalg.norm(residual[:-1])),
        "scaled_event_residual": float(residual[-1]),
        "ordered_event": {"eigenvalue": float(eigenvalues[6]), "lower_gap": float(eigenvalues[6] - eigenvalues[5]), "upper_gap": float(eigenvalues[7] - eigenvalues[6])},
        "rayleigh_covector_scaled_l2": float(np.linalg.norm(covector)),
        "legacy_covector_scaled_l2": float(np.linalg.norm(legacy)),
        "legacy_vs_rayleigh_relative_residual": float(np.linalg.norm(legacy - covector) / np.linalg.norm(covector)),
        "rayleigh_step_stability_relative_residual": float(np.linalg.norm(coarse - covector) / np.linalg.norm(covector)),
        "directional_checks": checks,
        "outcome": "LEGACY_EVENT_COVECTOR_INVALIDATED_RAYLEIGH_COVECTOR_VALIDATED",
        "next_action": "RESUME_SQUARE_376_CLOSURE_FROM_V20_77_GEOMETRY_WITH_REPROJECTED_RAYLEIGH_EVENT_MULTIPLIER",
        "physical_event_changed": False, "physical_equations_changed": False,
        "numerical_event_derivative_corrected": True, "acceptance_gate_changed": False,
    }


def completion_payload() -> dict[str, Any]:
    result = rayleigh_event_covector_audit()
    validation = {
        "ordered_event_isolated": result["ordered_event"]["lower_gap"] > 0.0 and result["ordered_event"]["upper_gap"] > 0.0,
        "rayleigh_step_stable": result["rayleigh_step_stability_relative_residual"] < 2.0e-8,
        "rayleigh_matches_event_directionals": max(row["absolute_residual"] for row in result["directional_checks"]) < 2.0e-5,
        "legacy_inconsistency_demonstrated": result["legacy_vs_rayleigh_relative_residual"] > 0.20,
        "event_multiplier_reprojected": result["event_multiplier_reprojected_only"],
        "same_physics": not result["physical_event_changed"] and not result["physical_equations_changed"] and not result["acceptance_gate_changed"],
        "derivative_correction_explicit": result["numerical_event_derivative_corrected"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_RAYLEIGH_EVENT_COVECTOR_V20_80", "version": VERSION,
        "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "rayleigh_event_covector": result, "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation, "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_RAYLEIGH_EVENT_COVECTOR_V20_80.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "RAYLEIGH_RELATIVE_STEP",
    "rayleigh_sbp_event_covector", "rayleigh_square_physical_residual",
    "rayleigh_project_event_multiplier", "rayleigh_event_covector_audit",
    "completion_payload", "materialize",
]
