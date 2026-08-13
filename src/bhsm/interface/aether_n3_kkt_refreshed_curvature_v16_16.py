"""Refresh the N=3 KKT Jacobian including nonzero event curvature."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_analytic_kkt_covector_v16_12 import (
    event_value_from_base,
    scaled_analytic_kkt_residual,
)
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import (
    _minimum_node_eta,
    kkt_jacobian_at,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    event_gradient_indices,
    kkt_variable_scales,
)


VERSION = "v16.16"
CLASSIFICATION = "BHSM_N3_KKT_REFRESHED_NONZERO_EVENT_CURVATURE"
FULL_BHSM_COMPLETE = False


def v16_15_final_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_kkt_extended_continuation_v16_15.json"
    ).read_text(encoding="utf-8"))
    values = payload["continuation"]["final_raw_vector_hex"]
    result = np.asarray([float.fromhex(value) for value in values])
    if result.shape != (376,):
        raise ValueError("v16.15 vector has wrong dimension")
    return result


def scaled_event_hessian(
    y_base: np.ndarray,
    *,
    relative_step: float = 1.0e-4,
    event_scale: float = 1.0e-3,
) -> np.ndarray:
    """Second derivative of E/event_scale on its exact 37-variable support."""

    y = np.asarray(y_base, dtype=float)
    scales = kkt_variable_scales(event_scale)[:-1]
    support = event_gradient_indices()
    hessian = np.zeros((len(y), len(y)))
    steps = relative_step * np.maximum(1.0, np.abs(y[support]))

    def event(vector: np.ndarray) -> float:
        return event_value_from_base(vector / scales) / event_scale

    center = event(y)
    for left, left_index in enumerate(support):
        left_delta = np.zeros_like(y)
        left_delta[left_index] = steps[left]
        plus = event(y + left_delta)
        minus = event(y - left_delta)
        hessian[left_index, left_index] = (
            plus - 2.0 * center + minus
        ) / steps[left] ** 2
        for right in range(left + 1, len(support)):
            right_index = support[right]
            right_delta = np.zeros_like(y)
            right_delta[right_index] = steps[right]
            value = (
                event(y + left_delta + right_delta)
                - event(y + left_delta - right_delta)
                - event(y - left_delta + right_delta)
                + event(y - left_delta - right_delta)
            ) / (4.0 * steps[left] * steps[right])
            hessian[left_index, right_index] = value
            hessian[right_index, left_index] = value
    return hessian


def refreshed_continuation_from(
    raw_vector: np.ndarray,
    *,
    iterations: int = 20,
    trust_radius: float = 1.0e-1,
) -> dict[str, Any]:
    raw = np.asarray(raw_vector, dtype=float)
    if raw.shape != (376,):
        raise ValueError("raw KKT vector has wrong dimension")
    scales = kkt_variable_scales()
    y = raw * scales
    assembled = kkt_jacobian_at(raw)
    matrix = np.asarray(assembled["KKT_jacobian"]).copy()
    event_hessian = scaled_event_hessian(y[:-1])
    matrix[:-1, :-1] += y[-1] * event_hessian
    matrix = 0.5 * (matrix + matrix.T)
    residual = scaled_analytic_kkt_residual(y)
    initial_norm = float(np.linalg.norm(residual))
    rows = []
    termination = "ITERATION_LIMIT"
    for iteration in range(1, iterations + 1):
        direction = np.linalg.lstsq(
            matrix, -residual, rcond=1.0e-10
        )[0]
        unrestricted_norm = float(np.linalg.norm(direction))
        direction *= min(
            1.0, trust_radius / max(unrestricted_norm, 1.0e-300)
        )
        accepted = None
        for backtrack in range(18):
            step = (0.5**backtrack) * direction
            candidate = y + step
            raw_candidate = candidate / scales
            try:
                eta_minimum = _minimum_node_eta(raw_candidate)
                if eta_minimum <= 1.0e-5:
                    raise ValueError("eta Legendre form became singular")
                candidate_residual = scaled_analytic_kkt_residual(candidate)
                candidate_norm = float(np.linalg.norm(candidate_residual))
            except (FloatingPointError, ValueError, np.linalg.LinAlgError):
                continue
            if candidate_norm < float(np.linalg.norm(residual)):
                accepted = (
                    step, candidate, candidate_residual,
                    candidate_norm, eta_minimum, backtrack,
                )
                break
        if accepted is None:
            termination = "REFRESHED_SR1_STEP_NOT_FOUND"
            break
        (
            step, candidate, candidate_residual,
            candidate_norm, eta_minimum, backtrack,
        ) = accepted
        residual_change = candidate_residual - residual
        defect = residual_change - matrix @ step
        denominator = float(defect @ step)
        threshold = 1.0e-8 * float(
            np.linalg.norm(defect) * np.linalg.norm(step)
        )
        updated = abs(denominator) > threshold
        if updated:
            matrix += np.outer(defect, defect) / denominator
            matrix = 0.5 * (matrix + matrix.T)
        y = candidate
        residual = candidate_residual
        rows.append({
            "iteration": iteration,
            "backtracks": backtrack,
            "residual_norm": candidate_norm,
            "event_residual": float(residual[-1]),
            "eta_minimum": eta_minimum,
            "unrestricted_direction_norm": unrestricted_norm,
            "accepted_step_norm": float(np.linalg.norm(step)),
            "SR1_updated": updated,
        })
    final_raw = y / scales
    return {
        "initial_residual_norm": initial_norm,
        "initial_event_residual": float(
            scaled_analytic_kkt_residual(raw * scales)[-1]
        ),
        "event_multiplier_rho": float(raw[-1]),
        "scaled_event_curvature_norm": float(np.linalg.norm(event_hessian)),
        "event_curvature_KKT_contribution_norm": float(
            abs(y[-1]) * np.linalg.norm(event_hessian)
        ),
        "final_residual_norm": float(np.linalg.norm(residual)),
        "final_event_residual": float(residual[-1]),
        "final_eta_minimum": _minimum_node_eta(final_raw),
        "iterations_requested": iterations,
        "iterations_accepted": len(rows),
        "termination": termination,
        "rows": rows,
        "final_raw_vector_hex": [float(value).hex() for value in final_raw],
    }


def refreshed_continuation(
    *,
    iterations: int = 20,
    trust_radius: float = 1.0e-1,
) -> dict[str, Any]:
    return refreshed_continuation_from(
        v16_15_final_raw_vector(),
        iterations=iterations,
        trust_radius=trust_radius,
    )


def completion_payload() -> dict[str, Any]:
    result = refreshed_continuation()
    validation = {
        "nonzero_event_curvature_inserted": (
            result["event_curvature_KKT_contribution_norm"] > 0.0
        ),
        "at_least_one_refreshed_step_accepted": (
            result["iterations_accepted"] > 0
        ),
        "complete_residual_reduced": (
            result["final_residual_norm"] < result["initial_residual_norm"]
        ),
        "eta_domain_preserved": result["final_eta_minimum"] > 1.0e-5,
    }
    return {
        "artifact": "BHSM_aether_n3_kkt_refreshed_curvature_v16_16",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "refreshed_continuation": result,
        "dependency_advanced": (
            "NONZERO_EVENT-MULTIPLIER_CURVATURE_INSERTED_IN_THE_REFRESHED_"
            "PHYSICAL_N3_KKT_JACOBIAN"
        ),
        "active_calculation": (
            "CONTINUE_REFRESHED_NEWTON-SR1_STEPS_TO_THE_STATIONARY_SOFT_EVENT"
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
    path = target / "BHSM_aether_n3_kkt_refreshed_curvature_v16_16.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "v16_15_final_raw_vector", "scaled_event_hessian",
    "refreshed_continuation_from", "refreshed_continuation",
    "completion_payload",
    "deterministic_json", "materialize",
]
