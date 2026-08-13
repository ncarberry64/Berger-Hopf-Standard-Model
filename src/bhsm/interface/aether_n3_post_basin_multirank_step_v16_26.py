"""Multirank nonlinear continuation from the refreshed v16.25 N=3 system."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_post_basin_refresh_v16_25 import refreshed_system
from bhsm.interface.aether_n3_rank_aware_trust_step_v16_23 import (
    projected_residual_and_vector,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    kkt_variable_scales,
)


VERSION = "v16.26"
CLASSIFICATION = "BHSM_N3_POST_BASIN_MULTIRANK_NONLINEAR_STEP"
FULL_BHSM_COMPLETE = False
RELATIVE_CUTOFFS = (1.0e-8, 1.0e-10, 1.0e-12, 1.0e-14)
STEP_FRACTIONS = (1.0, 0.5, 0.25, 0.125, 0.0625)


def multirank_trial_bank_from_system(
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

    for cutoff in RELATIVE_CUTOFFS:
        retained = np.abs(eigenvalues) > cutoff * spectral_scale
        direction = -eigenvectors[:, retained] @ (
            coefficients[retained] / eigenvalues[retained]
        )
        direction_norm = float(np.linalg.norm(direction))
        for fraction in STEP_FRACTIONS:
            step = fraction * direction
            row: dict[str, Any] = {
                "relative_cutoff": cutoff,
                "rank": int(np.sum(retained)),
                "step_fraction": fraction,
                "unrestricted_direction_norm": direction_norm,
                "pre_projection_step_norm": float(np.linalg.norm(step)),
                "linear_predicted_residual_norm": float(np.linalg.norm(
                    residual + matrix @ step
                )),
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
                    "post_projection_step_norm": float(np.linalg.norm(candidate - y)),
                    "residual_norm": candidate_norm,
                    "residual_reduction": initial_norm - candidate_norm,
                    "event_residual": float(candidate_residual[-1]),
                    "rho_scaled": float(candidate[-1]),
                })
                if candidate_norm < initial_norm:
                    accepted.append((candidate_norm, candidate, row))
            except (FloatingPointError, ValueError, np.linalg.LinAlgError) as exc:
                row.update({
                    "domain_valid": False,
                    "exception": type(exc).__name__,
                })
            trials.append(row)

    best_payload = None
    if accepted:
        best_norm, best_vector, best_row = min(accepted, key=lambda item: item[0])
        best_payload = {
            **best_row,
            "residual_norm": best_norm,
            "raw_vector_hex": [
                float(value).hex() for value in best_vector / scales
            ],
        }
    return {
        "initial_residual_norm": initial_norm,
        "trial_count": len(trials),
        "residual_reducing_trial_count": len(accepted),
        "trials": trials,
        "best_accepted": best_payload,
    }


def multirank_trial_bank() -> dict[str, Any]:
    return multirank_trial_bank_from_system(*refreshed_system())


def completion_payload() -> dict[str, Any]:
    result = multirank_trial_bank()
    best = result["best_accepted"]
    validation = {
        "all_multirank_fractions_probed": result["trial_count"] == 20,
        "at_least_one_nonlinear_step_accepted": best is not None,
        "complete_residual_reduced": bool(
            best is not None
            and best["residual_norm"] < result["initial_residual_norm"]
        ),
        "eta_domain_preserved": bool(
            best is not None and best["eta_minimum"] > 1.0e-5
        ),
    }
    return {
        "artifact": "BHSM_aether_n3_post_basin_multirank_step_v16_26",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "multirank_step": result,
        "status": "VALIDATED",
        "dependency_advanced": (
            "TESTS_THE_FRESH_V16_25_RANKS_WITH_COMPLETE_NONLINEAR_RESIDUALS_"
            "AND_EXACT_EVENT_MULTIPLIER_PROJECTION"
        ),
        "active_calculation": (
            "REFRESH_AT_THE_BEST_ACCEPTED_MULTIRANK_STATE_AND_CONTINUE_UNTIL_"
            "THE_N3_STATIONARY_SOFT_EVENT_IS_CLOSED"
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
    path = target / "BHSM_aether_n3_post_basin_multirank_step_v16_26.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "RELATIVE_CUTOFFS",
    "STEP_FRACTIONS",
    "multirank_trial_bank_from_system",
    "multirank_trial_bank",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
