"""Rank-aware trust-region step for the ill-conditioned v16.21 N=3 KKT."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_analytic_kkt_covector_v16_12 import (
    event_covector,
    event_value_from_base,
    replacement_action_covector,
)
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_kkt_range_nullspace_audit_v16_21 import (
    refreshed_jacobian_and_residual,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    kkt_variable_scales,
)


VERSION = "v16.23"
CLASSIFICATION = "BHSM_N3_RANK_AWARE_TRUST_REGION_STEP"
FULL_BHSM_COMPLETE = False


def projected_residual_and_vector(
    scaled_vector: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Project rho and evaluate the residual with one action-covector call."""

    y = np.asarray(scaled_vector, dtype=float).copy()
    if y.shape != (376,):
        raise ValueError("scaled KKT vector has wrong dimension")
    scales = kkt_variable_scales()
    raw_base = y[:-1] / scales[:-1]
    action = np.asarray(
        replacement_action_covector(raw_base)["covector"]
    ) / scales[:-1]
    event = event_covector(raw_base) / scales[:-1] / scales[-1]
    y[-1] = -float(action @ event) / float(event @ event)
    residual = np.concatenate((
        action + y[-1] * event,
        [event_value_from_base(raw_base) / scales[-1]],
    ))
    return y, residual


def exact_event_multiplier_projection(scaled_vector: np.ndarray) -> np.ndarray:
    """Minimize base stationarity in rho while leaving the base point fixed."""

    return projected_residual_and_vector(scaled_vector)[0]


def rank_aware_trial_bank(
    *,
    relative_cutoffs: tuple[float, ...] = (1.0e-8, 1.0e-10, 1.0e-12, 1.0e-14),
    trust_radii: tuple[float, ...] = (2.0e-1, 1.0e-1, 5.0e-2, 2.0e-2, 1.0e-2, 5.0e-3),
) -> dict[str, Any]:
    """Probe truncated spectral Newton directions without changing the action."""

    matrix, residual, raw = refreshed_jacobian_and_residual()
    scales = kkt_variable_scales()
    y = raw * scales
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    spectral_scale = float(np.max(np.abs(eigenvalues)))
    coefficients = eigenvectors.T @ residual
    initial_norm = float(np.linalg.norm(residual))
    trials: list[dict[str, Any]] = []
    accepted: list[tuple[float, np.ndarray, dict[str, Any]]] = []

    for cutoff in relative_cutoffs:
        retained = np.abs(eigenvalues) > cutoff * spectral_scale
        direction = -eigenvectors[:, retained] @ (
            coefficients[retained] / eigenvalues[retained]
        )
        unrestricted_norm = float(np.linalg.norm(direction))
        range_floor = float(np.linalg.norm(coefficients[~retained]))
        for trust_radius in trust_radii:
            trusted = direction * min(
                1.0, trust_radius / max(unrestricted_norm, 1.0e-300)
            )
            predicted_norm = float(np.linalg.norm(residual + matrix @ trusted))
            candidate, candidate_residual = projected_residual_and_vector(y + trusted)
            raw_candidate = candidate / scales
            row: dict[str, Any] = {
                "relative_cutoff": cutoff,
                "rank": int(np.sum(retained)),
                "trust_radius": trust_radius,
                "unrestricted_direction_norm": unrestricted_norm,
                "pre_projection_step_norm": float(np.linalg.norm(trusted)),
                "linear_predicted_residual_norm": predicted_norm,
                "linear_range_floor": range_floor,
            }
            try:
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
            "scaled_vector_hex": [float(value).hex() for value in best_vector],
            "raw_vector_hex": [
                float(value).hex() for value in best_vector / scales
            ],
            "residual_norm": best_norm,
        }
    return {
        "initial_residual_norm": initial_norm,
        "initial_eta_minimum": _minimum_node_eta(raw),
        "spectral_scale": spectral_scale,
        "trial_count": len(trials),
        "residual_reducing_trial_count": len(accepted),
        "trials": trials,
        "best_accepted": best_payload,
    }


def completion_payload() -> dict[str, Any]:
    result = rank_aware_trial_bank()
    best = result["best_accepted"]
    validation = {
        "all_requested_spectral_cutoffs_probed": result["trial_count"] == 24,
        "at_least_one_rank_aware_step_accepted": best is not None,
        "complete_residual_reduced": bool(
            best is not None
            and best["residual_norm"] < result["initial_residual_norm"]
        ),
        "eta_domain_preserved": bool(
            best is not None and best["eta_minimum"] > 1.0e-5
        ),
    }
    return {
        "artifact": "BHSM_aether_n3_rank_aware_trust_step_v16_23",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "status": "VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "rank_aware_step": result,
        "dependency_advanced": (
            "TESTS_THE_V16_21_CASE_1_DIAGNOSIS_BY_APPLYING_TRUNCATED_SPECTRAL_"
            "TRUST_STEPS_TO_THE_SAME_ANCHORED_N3_KKT_WITH_EXACT_RHO_PROJECTION"
        ),
        "active_calculation": (
            "ITERATE_ACCEPTED_RANK_AWARE_STEPS_WITH_FRESH_PHYSICAL_JACOBIANS_"
            "OR_REDIRECT_TO_THE_IDENTIFIED_DISCRETIZATION_DEFECT_IF_NONE_REDUCES_"
            "THE_COMPLETE_RESIDUAL"
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
    path = target / "BHSM_aether_n3_rank_aware_trust_step_v16_23.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "projected_residual_and_vector",
    "exact_event_multiplier_projection",
    "rank_aware_trial_bank",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
