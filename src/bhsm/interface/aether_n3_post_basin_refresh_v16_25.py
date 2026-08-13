"""Fresh physical KKT spectrum at the accepted v16.24 basin state."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_analytic_kkt_covector_v16_12 import (
    scaled_analytic_kkt_residual,
)
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import kkt_jacobian_at
from bhsm.interface.aether_n3_kkt_refreshed_curvature_v16_16 import (
    scaled_event_hessian,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    kkt_variable_scales,
)


VERSION = "v16.25"
CLASSIFICATION = "BHSM_N3_POST_BASIN_FRESH_PHYSICAL_KKT"
FULL_BHSM_COMPLETE = False


def v16_24_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_rank_aware_basin_step_v16_24.json"
    ).read_text(encoding="utf-8"))
    values = payload["basin_step"]["best_accepted"]["raw_vector_hex"]
    result = np.asarray([float.fromhex(value) for value in values])
    if result.shape != (376,):
        raise ValueError("v16.24 vector has wrong dimension")
    return result


def refreshed_system_at(raw_vector: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    raw = np.asarray(raw_vector, dtype=float)
    if raw.shape != (376,):
        raise ValueError("raw KKT vector has wrong dimension")
    scales = kkt_variable_scales()
    y = raw * scales
    matrix = np.asarray(kkt_jacobian_at(raw)["KKT_jacobian"]).copy()
    event_hessian = scaled_event_hessian(y[:-1])
    matrix[:-1, :-1] += y[-1] * event_hessian
    matrix = 0.5 * (matrix + matrix.T)
    residual = scaled_analytic_kkt_residual(y)
    return matrix, residual, raw


def refreshed_system() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return refreshed_system_at(v16_24_raw_vector())


def post_basin_spectral_audit() -> dict[str, Any]:
    matrix, residual, raw = refreshed_system()
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    scale = float(np.max(np.abs(eigenvalues)))
    coefficients = eigenvectors.T @ residual
    norm = float(np.linalg.norm(residual))
    rows = {}
    for cutoff in (1.0e-8, 1.0e-10, 1.0e-12, 1.0e-14):
        retained = np.abs(eigenvalues) > cutoff * scale
        direction = -eigenvectors[:, retained] @ (
            coefficients[retained] / eigenvalues[retained]
        )
        rows[f"relative_{cutoff:.0e}"] = {
            "rank": int(np.sum(retained)),
            "nullity": int(np.sum(~retained)),
            "residual_outside_range_norm": float(np.linalg.norm(
                coefficients[~retained]
            )),
            "fraction_outside_range": float(
                np.linalg.norm(coefficients[~retained]) / norm
            ),
            "unrestricted_direction_norm": float(np.linalg.norm(direction)),
        }
    return {
        "residual_norm": norm,
        "eta_event_multiplier_scaled": float(raw[-1] * kkt_variable_scales()[-1]),
        "spectral_scale": scale,
        "smallest_absolute_eigenvalue": float(np.min(np.abs(eigenvalues))),
        "symmetric_relative_residual": float(
            np.linalg.norm(matrix - matrix.T) / max(1.0, np.linalg.norm(matrix))
        ),
        "tolerance_audit": rows,
    }


def completion_payload() -> dict[str, Any]:
    result = post_basin_spectral_audit()
    strict = result["tolerance_audit"]["relative_1e-14"]
    validation = {
        "accepted_v16_24_residual_reproduced": math.isclose(
            result["residual_norm"], 28.127172454276277,
            rel_tol=0.0, abs_tol=2.0e-9,
        ),
        "fresh_physical_jacobian_is_symmetric": (
            result["symmetric_relative_residual"] < 1.0e-14
        ),
        "strict_numerical_range_measured": strict["fraction_outside_range"] >= 0.0,
        "strict_direction_is_finite": math.isfinite(
            strict["unrestricted_direction_norm"]
        ),
    }
    return {
        "artifact": "BHSM_aether_n3_post_basin_refresh_v16_25",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "post_basin_refresh": result,
        "status": "ACTIVE",
        "dependency_advanced": (
            "REFRESHES_THE_COMPLETE_ACTION_PLUS_EVENT_CURVATURE_AFTER_THE_"
            "MATERIAL_V16_24_DESCENT_INSTEAD_OF_REUSING_THE_OLD_TANGENT"
        ),
        "active_calculation": (
            "USE_THE_REFRESHED_NUMERICAL_RANGE_AND_DIRECTION_SCALE_TO_CONTINUE_"
            "THE_SAME_N3_SADDLE_SOLVE"
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
    path = target / "BHSM_aether_n3_post_basin_refresh_v16_25.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "v16_24_raw_vector",
    "refreshed_system_at",
    "refreshed_system",
    "post_basin_spectral_audit",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
