"""SR1 continuation of the safeguarded N=3 replacement KKT solve."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_analytic_kkt_covector_v16_12 import (
    scaled_analytic_kkt_residual,
)
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import (
    _minimum_node_eta,
    seed_kkt_jacobian,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    kkt_variable_scales,
)


VERSION = "v16.14"
CLASSIFICATION = "BHSM_N3_REPLACEMENT_KKT_SR1_CONTINUATION"
FULL_BHSM_COMPLETE = False


def v16_13_accepted_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_kkt_newton_step_v16_13.json"
    ).read_text(encoding="utf-8"))
    values = payload["newton_step"]["accepted"]["raw_vector_hex"]
    result = np.asarray([float.fromhex(value) for value in values])
    if result.shape != (376,):
        raise ValueError("v16.13 accepted vector has wrong dimension")
    return result


def sr1_continuation(
    *,
    iterations: int = 12,
    trust_radius: float = 1.0e-1,
) -> dict[str, Any]:
    if iterations < 1 or trust_radius <= 0.0:
        raise ValueError("positive iteration count and trust radius required")
    assembled = seed_kkt_jacobian()
    matrix = np.asarray(assembled["KKT_jacobian"]).copy()
    scales = kkt_variable_scales()
    y = v16_13_accepted_raw_vector() * scales
    residual = scaled_analytic_kkt_residual(y)
    initial_norm = float(np.linalg.norm(residual))
    rows = []
    termination = "ITERATION_LIMIT"
    for iteration in range(1, iterations + 1):
        direction = np.linalg.lstsq(
            matrix, -residual, rcond=1.0e-10
        )[0]
        direction_norm = float(np.linalg.norm(direction))
        direction *= min(
            1.0, trust_radius / max(direction_norm, 1.0e-300)
        )
        accepted = None
        for backtrack in range(18):
            fraction = 0.5**backtrack
            step = fraction * direction
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
            termination = "SAFEGUARDED_SR1_STEP_NOT_FOUND"
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
        sr1_updated = abs(denominator) > threshold
        if sr1_updated:
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
            "unrestricted_direction_norm": direction_norm,
            "accepted_step_norm": float(np.linalg.norm(step)),
            "SR1_updated": sr1_updated,
        })
    final_raw = y / scales
    return {
        "initial_residual_norm": initial_norm,
        "final_residual_norm": float(np.linalg.norm(residual)),
        "final_event_residual": float(residual[-1]),
        "final_eta_minimum": _minimum_node_eta(final_raw),
        "iterations_requested": iterations,
        "iterations_accepted": len(rows),
        "termination": termination,
        "rows": rows,
        "final_raw_vector_hex": [float(value).hex() for value in final_raw],
    }


def completion_payload() -> dict[str, Any]:
    result = sr1_continuation()
    validation = {
        "at_least_one_step_accepted": result["iterations_accepted"] > 0,
        "complete_residual_reduced": (
            result["final_residual_norm"] < result["initial_residual_norm"]
        ),
        "eta_domain_preserved": result["final_eta_minimum"] > 1.0e-5,
        "state_preserved_at_full_float_precision": len(
            result["final_raw_vector_hex"]
        ) == 376,
    }
    return {
        "artifact": "BHSM_aether_n3_kkt_sr1_continuation_v16_14",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "continuation": result,
        "dependency_advanced": (
            "MULTIPLE_NONLINEAR_DOMAIN-PRESERVING_STEPS_OF_THE_COMMON_N3_"
            "REPLACEMENT_EVENT-KKT_SOLVE"
        ),
        "active_calculation": (
            "REFRESH_THE_PHYSICAL_KKT_JACOBIAN_IF_SR1_STALLS_OR_CONTINUE_"
            "TO_THE_STATIONARY_SOFT_EVENT"
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
    path = target / "BHSM_aether_n3_kkt_sr1_continuation_v16_14.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "v16_13_accepted_raw_vector", "sr1_continuation", "completion_payload",
    "deterministic_json", "materialize",
]
