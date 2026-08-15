"""Fresh KKT spectrum after the accepted v16.26 robust-rank step."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_post_basin_refresh_v16_25 import refreshed_system_at
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    kkt_variable_scales,
)


VERSION = "v16.27"
CLASSIFICATION = "BHSM_N3_POST_MULTIRANK_FRESH_PHYSICAL_KKT"
FULL_BHSM_COMPLETE = False


def v16_26_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_post_basin_multirank_step_v16_26.json"
    ).read_text(encoding="utf-8"))
    values = payload["multirank_step"]["best_accepted"]["raw_vector_hex"]
    result = np.asarray([float.fromhex(value) for value in values])
    if result.shape != (376,):
        raise ValueError("v16.26 vector has wrong dimension")
    return result


def refreshed_multirank_system() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return refreshed_system_at(v16_26_raw_vector())


def spectral_and_block_audit() -> dict[str, Any]:
    matrix, residual, raw = refreshed_multirank_system()
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    scale = float(np.max(np.abs(eigenvalues)))
    coefficients = eigenvectors.T @ residual
    norm = float(np.linalg.norm(residual))
    q_count = 230
    m_count = 144
    rows = {}
    for cutoff in (1.0e-8, 1.0e-10, 1.0e-12, 1.0e-14):
        retained = np.abs(eigenvalues) > cutoff * scale
        direction = -eigenvectors[:, retained] @ (
            coefficients[retained] / eigenvalues[retained]
        )
        rows[f"relative_{cutoff:.0e}"] = {
            "rank": int(np.sum(retained)),
            "nullity": int(np.sum(~retained)),
            "fraction_outside_range": float(
                np.linalg.norm(coefficients[~retained]) / norm
            ),
            "unrestricted_direction_norm": float(np.linalg.norm(direction)),
        }
    return {
        "residual_norm": norm,
        "q_stationarity_norm": float(np.linalg.norm(residual[:q_count])),
        "multiplier_stationarity_norm": float(np.linalg.norm(
            residual[q_count:q_count + m_count]
        )),
        "period_stationarity": float(residual[-2]),
        "event_residual": float(residual[-1]),
        "event_multiplier_scaled": float(raw[-1] * kkt_variable_scales()[-1]),
        "spectral_scale": scale,
        "symmetric_relative_residual": float(
            np.linalg.norm(matrix - matrix.T) / max(1.0, np.linalg.norm(matrix))
        ),
        "tolerance_audit": rows,
    }


def completion_payload() -> dict[str, Any]:
    result = spectral_and_block_audit()
    validation = {
        "accepted_v16_26_residual_reproduced": math.isclose(
            result["residual_norm"], 21.947135009643,
            rel_tol=0.0, abs_tol=2.0e-9,
        ),
        "fresh_physical_jacobian_is_symmetric": (
            result["symmetric_relative_residual"] < 1.0e-14
        ),
        "all_residual_blocks_reported": all(math.isfinite(result[key]) for key in (
            "q_stationarity_norm",
            "multiplier_stationarity_norm",
            "period_stationarity",
            "event_residual",
        )),
    }
    return {
        "artifact": "BHSM_aether_n3_post_multirank_refresh_v16_27",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "post_multirank_refresh": result,
        "status": "ACTIVE",
        "dependency_advanced": (
            "REFRESHES_AND_BLOCK_DECOMPOSES_THE_COMMON_N3_KKT_AFTER_THE_"
            "ROBUST_RANK_80_RESIDUAL_REDUCTION"
        ),
        "active_calculation": (
            "CONTINUE_THE_JOINT_STATIONARITY_EVENT_SOLVE_USING_THE_NEW_"
            "RANK_AND_BLOCK_STRUCTURE"
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
    path = target / "BHSM_aether_n3_post_multirank_refresh_v16_27.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "v16_26_raw_vector",
    "refreshed_multirank_system",
    "spectral_and_block_audit",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
