"""Normalized exact-merit-gradient continuation from v16.47."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_post_basin_refresh_v16_25 import refreshed_system_at
from bhsm.interface.aether_n3_rank_aware_trust_step_v16_23 import projected_residual_and_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_third_physical_refresh_v16_29 import spectral_and_block_audit_from_system

VERSION = "v16.48"
CLASSIFICATION = "BHSM_N3_NORMALIZED_EXACT_MERIT_GRADIENT_CONTINUATION"
FULL_BHSM_COMPLETE = False
TRUST_RADII = (1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2)


def v16_47_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_strong_damping_continuation_v16_47.json"
    ).read_text(encoding="utf-8"))
    values = payload["strong_damping_continuation"]["strong_damping_trial_bank"]["best_accepted"]["raw_vector_hex"]
    raw = np.asarray([float.fromhex(value) for value in values])
    if raw.shape != (376,): raise ValueError("v16.47 vector has wrong dimension")
    return raw


def merit_gradient_trial_bank(
    matrix: np.ndarray, residual: np.ndarray, raw: np.ndarray,
) -> dict[str, Any]:
    scales = kkt_variable_scales(); y = raw * scales
    gradient = matrix.T @ residual
    gradient_norm = float(np.linalg.norm(gradient))
    direction = -gradient / gradient_norm
    initial_norm = float(np.linalg.norm(residual))
    trials: list[dict[str, Any]] = []
    accepted: list[tuple[float, np.ndarray, dict[str, Any]]] = []
    for radius in TRUST_RADII:
        step = radius * direction
        row: dict[str, Any] = {
            "trust_radius": radius,
            "pre_projection_step_norm": float(np.linalg.norm(step)),
            "linear_predicted_residual_norm": float(np.linalg.norm(residual + matrix @ step)),
        }
        try:
            candidate, candidate_residual = projected_residual_and_vector(y + step)
            raw_candidate = candidate / scales
            eta = _minimum_node_eta(raw_candidate)
            if eta <= 1e-5: raise ValueError("eta Legendre form became singular")
            norm = float(np.linalg.norm(candidate_residual))
            row.update({
                "domain_valid": True, "eta_minimum": eta,
                "residual_norm": norm, "residual_reduction": initial_norm - norm,
                "event_residual": float(candidate_residual[-1]),
                "post_projection_step_norm": float(np.linalg.norm(candidate - y)),
            })
            if norm < initial_norm: accepted.append((norm, candidate, row))
        except (FloatingPointError, ValueError, np.linalg.LinAlgError) as exc:
            row.update({"domain_valid": False, "exception": type(exc).__name__})
        trials.append(row)
    best = None
    if accepted:
        norm, vector, row = min(accepted, key=lambda item: item[0])
        best = {**row, "residual_norm": norm,
                "raw_vector_hex": [float(value).hex() for value in vector / scales]}
    return {
        "method": "normalized_negative_gradient_of_one_half_complete_KKT_residual_squared",
        "merit_gradient_norm": gradient_norm,
        "initial_residual_norm": initial_norm,
        "trial_count": len(trials),
        "residual_reducing_trial_count": len(accepted),
        "trials": trials,
        "best_accepted": best,
    }


def normalized_merit_continuation() -> dict[str, Any]:
    matrix, residual, raw = refreshed_system_at(v16_47_raw_vector())
    return {
        "fresh_physical_audit": spectral_and_block_audit_from_system(matrix, residual, raw),
        "normalized_merit_gradient_trial_bank": merit_gradient_trial_bank(matrix, residual, raw),
    }


def completion_payload() -> dict[str, Any]:
    result = normalized_merit_continuation(); audit = result["fresh_physical_audit"]
    bank = result["normalized_merit_gradient_trial_bank"]; best = bank["best_accepted"]
    validation = {
        "accepted_v16_47_residual_reproduced": math.isclose(audit["residual_norm"], 6.442521870987222, rel_tol=0.0, abs_tol=2e-9),
        "fresh_physical_jacobian_symmetric": audit["symmetric_relative_residual"] < 1e-14,
        "normalized_merit_gradient_nonzero": bank["merit_gradient_norm"] > 0.0,
        "trust_radius_grid_probed": bank["trial_count"] == len(TRUST_RADII),
        "at_least_one_joint_step_accepted": best is not None,
        "complete_residual_reduced": bool(best is not None and best["residual_norm"] < audit["residual_norm"]),
        "eta_domain_preserved": bool(best is not None and best["eta_minimum"] > 1e-5),
        "full_precision_state_preserved": bool(best is not None and len(best["raw_vector_hex"]) == 376),
    }
    return {
        "artifact": "BHSM_aether_n3_normalized_merit_gradient_v16_48",
        "version": VERSION, "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "normalized_merit_continuation": result,
        "status": "VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained": "JOINT_PARENT_GEOMETRY_AND_SOFT_EVENT_STATIONARITY_IN_THE_DECLARED_SOBOLEV_METRIC",
        "dependency_advanced": "SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation": "PROMOTE_THE_BEST_MERIT_DESCENT_OR_REDIRECT_TO_THE_REMAINING_PARENT_GEOMETRY_BLOCK",
        "validation": validation, "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, np.ndarray): return [_canonical(item) for item in value.tolist()]
    if isinstance(value, np.bool_): return bool(value)
    if isinstance(value, np.integer): return int(value)
    if isinstance(value, np.floating): value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value): raise ValueError("non-finite float")
        return round(value, 15)
    if isinstance(value, Mapping): return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)): return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_normalized_merit_gradient_v16_48.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path

__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "TRUST_RADII", "v16_47_raw_vector", "merit_gradient_trial_bank", "normalized_merit_continuation", "completion_payload", "deterministic_json", "materialize"]
