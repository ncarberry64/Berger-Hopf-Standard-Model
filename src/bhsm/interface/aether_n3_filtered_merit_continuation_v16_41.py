"""Fresh spectrally filtered merit continuation from the v16.40 state."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_post_basin_refresh_v16_25 import refreshed_system_at
from bhsm.interface.aether_n3_rank_aware_trust_step_v16_23 import (
    projected_residual_and_vector,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    kkt_variable_scales,
)
from bhsm.interface.aether_n3_third_physical_refresh_v16_29 import (
    spectral_and_block_audit_from_system,
)


VERSION = "v16.41"
CLASSIFICATION = "BHSM_N3_FRESH_SPECTRALLY_FILTERED_MERIT_CONTINUATION"
FULL_BHSM_COMPLETE = False
FILTER_RELATIVE_SCALES = (1.0e-8, 1.0e-10, 1.0e-12, 1.0e-14)
STEP_FRACTIONS = (1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625)


def v16_40_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_combined_fresh_continuation_v16_40.json"
    ).read_text(encoding="utf-8"))
    values = payload["combined_fresh_continuation"]["multirank_step"]["best_accepted"]["raw_vector_hex"]
    result = np.asarray([float.fromhex(value) for value in values])
    if result.shape != (376,):
        raise ValueError("v16.40 vector has wrong dimension")
    return result


def filtered_trial_bank_from_system(
    matrix: np.ndarray, residual: np.ndarray, raw: np.ndarray,
) -> dict[str, Any]:
    scales = kkt_variable_scales()
    y = raw * scales
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    spectral_scale = float(np.max(np.abs(eigenvalues)))
    coefficients = eigenvectors.T @ residual
    initial_norm = float(np.linalg.norm(residual))
    trials: list[dict[str, Any]] = []
    accepted: list[tuple[float, np.ndarray, dict[str, Any]]] = []
    for relative_filter in FILTER_RELATIVE_SCALES:
        mu = relative_filter * spectral_scale
        factors = eigenvalues / (eigenvalues**2 + mu**2)
        direction = -eigenvectors @ (factors * coefficients)
        direction_norm = float(np.linalg.norm(direction))
        for fraction in STEP_FRACTIONS:
            step = fraction * direction
            row: dict[str, Any] = {
                "relative_filter_scale": relative_filter,
                "absolute_filter_scale": mu,
                "step_fraction": fraction,
                "unrestricted_direction_norm": direction_norm,
                "pre_projection_step_norm": float(np.linalg.norm(step)),
                "linear_predicted_residual_norm": float(np.linalg.norm(residual + matrix @ step)),
            }
            try:
                candidate, candidate_residual = projected_residual_and_vector(y + step)
                raw_candidate = candidate / scales
                eta_minimum = _minimum_node_eta(raw_candidate)
                if eta_minimum <= 1.0e-5:
                    raise ValueError("eta Legendre form became singular")
                candidate_norm = float(np.linalg.norm(candidate_residual))
                row.update({
                    "domain_valid": True,
                    "eta_minimum": eta_minimum,
                    "residual_norm": candidate_norm,
                    "residual_reduction": initial_norm - candidate_norm,
                    "event_residual": float(candidate_residual[-1]),
                    "post_projection_step_norm": float(np.linalg.norm(candidate - y)),
                })
                if candidate_norm < initial_norm:
                    accepted.append((candidate_norm, candidate, row))
            except (FloatingPointError, ValueError, np.linalg.LinAlgError) as exc:
                row.update({"domain_valid": False, "exception": type(exc).__name__})
            trials.append(row)
    best_payload = None
    if accepted:
        best_norm, best_vector, best_row = min(accepted, key=lambda item: item[0])
        best_payload = {
            **best_row,
            "residual_norm": best_norm,
            "raw_vector_hex": [float(value).hex() for value in best_vector / scales],
        }
    return {
        "method": "Levenberg-Marquardt_filter_lambda_over_lambda_squared_plus_mu_squared",
        "initial_residual_norm": initial_norm,
        "trial_count": len(trials),
        "residual_reducing_trial_count": len(accepted),
        "trials": trials,
        "best_accepted": best_payload,
    }


def filtered_continuation() -> dict[str, Any]:
    matrix, residual, raw = refreshed_system_at(v16_40_raw_vector())
    return {
        "fresh_physical_audit": spectral_and_block_audit_from_system(matrix, residual, raw),
        "filtered_trial_bank": filtered_trial_bank_from_system(matrix, residual, raw),
    }


def completion_payload() -> dict[str, Any]:
    result = filtered_continuation()
    audit, bank = result["fresh_physical_audit"], result["filtered_trial_bank"]
    best = bank["best_accepted"]
    validation = {
        "accepted_v16_40_residual_reproduced": math.isclose(audit["residual_norm"], 6.604262580172, rel_tol=0.0, abs_tol=2.0e-9),
        "fresh_physical_jacobian_symmetric": audit["symmetric_relative_residual"] < 1.0e-14,
        "all_filter_fractions_probed": bank["trial_count"] == 28,
        "at_least_one_filtered_step_accepted": best is not None,
        "complete_residual_reduced": bool(best is not None and best["residual_norm"] < audit["residual_norm"]),
        "eta_domain_preserved": bool(best is not None and best["eta_minimum"] > 1.0e-5),
    }
    return {
        "artifact": "BHSM_aether_n3_filtered_merit_continuation_v16_41",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "filtered_continuation": result,
        "status": "VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained": "JOINT_EVENT_BACKGROUND_UPSTREAM_OF_PERSISTENT_RETURNED_PARTICLE_OPERATORS",
        "dependency_advanced": "SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation": "REFRESH_AT_THE_ACCEPTED_FILTERED_STATE_AND_CONTINUE_JOINT_CLOSURE",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, np.ndarray): return [_canonical(item) for item in value.tolist()]
    if isinstance(value, np.bool_): return bool(value)
    if isinstance(value, np.integer): return int(value)
    if isinstance(value, np.floating): value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value): raise ValueError("non-finite float")
        return round(value, 12)
    if isinstance(value, Mapping): return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)): return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_filtered_merit_continuation_v16_41.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "FILTER_RELATIVE_SCALES", "STEP_FRACTIONS", "v16_40_raw_vector", "filtered_trial_bank_from_system", "filtered_continuation", "completion_payload", "deterministic_json", "materialize"]
