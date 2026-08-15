"""First safeguarded Newton step for the physical N=3 replacement KKT."""

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
    scaled_analytic_kkt_residual,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    anchored_kkt_dimensions,
    eta_legendre_minimum,
    kkt_variable_scales,
    pack_reduced,
    unpack_reduced,
)


VERSION = "v16.13"
CLASSIFICATION = "BHSM_N3_SAFEGUARDED_REPLACEMENT_KKT_NEWTON_STEP"
FULL_BHSM_COMPLETE = False


def artifact_seed_vector() -> np.ndarray:
    path = Path("artifacts/BHSM_aether_n3_replacement_global_kkt_v16_11.json")
    seed = json.loads(path.read_text(encoding="utf-8"))[
        "strictly_interior_N3_seed"
    ]
    return pack_reduced(
        np.asarray(seed["coordinates"]),
        np.asarray(seed["multipliers"]),
        float(seed["period"]),
        0.0,
    )


def scaled_action_gradient(y_base: np.ndarray) -> np.ndarray:
    scales = kkt_variable_scales()[:-1]
    result = replacement_action_covector(
        np.asarray(y_base, dtype=float) / scales
    )
    return np.asarray(result["covector"]) / scales


def kkt_jacobian_at(
    raw_vector: np.ndarray,
    *, relative_step: float = 1.0e-4,
) -> dict[str, Any]:
    raw = np.asarray(raw_vector, dtype=float)
    if raw.shape != (anchored_kkt_dimensions()["total_unknowns"],):
        raise ValueError("raw KKT vector has wrong dimension")
    scales = kkt_variable_scales()
    y = raw * scales
    y_base = y[:-1]
    base = raw[:-1]
    dimension = anchored_kkt_dimensions()["stationarity_equations"]
    hessian = np.empty((dimension, dimension))
    for column in range(dimension):
        step = relative_step * max(1.0, abs(float(y_base[column])))
        delta = np.zeros(dimension)
        delta[column] = step
        hessian[:, column] = (
            scaled_action_gradient(y_base + delta)
            - scaled_action_gradient(y_base - delta)
        ) / (2.0 * step)
    asymmetry = np.linalg.norm(hessian - hessian.T) / max(
        1.0, np.linalg.norm(hessian)
    )
    hessian = 0.5 * (hessian + hessian.T)
    event_scale = scales[-1]
    event_gradient = event_covector(base) / scales[:-1] / event_scale
    matrix = np.zeros((dimension + 1, dimension + 1))
    matrix[:-1, :-1] = hessian
    matrix[:-1, -1] = event_gradient
    matrix[-1, :-1] = event_gradient
    residual = np.concatenate((
        scaled_action_gradient(y_base),
        [event_value_from_base(base) / event_scale],
    ))
    return {
        "scaled_seed": y,
        "scaled_residual": residual,
        "KKT_jacobian": matrix,
        "symmetrization_relative_correction": float(asymmetry),
        "finite": bool(
            np.all(np.isfinite(matrix)) and np.all(np.isfinite(residual))
        ),
    }


def seed_kkt_jacobian(
    *, relative_step: float = 1.0e-4,
) -> dict[str, Any]:
    """Action Hessian and event border at the rho=0 seed."""

    return kkt_jacobian_at(
        artifact_seed_vector(), relative_step=relative_step
    )


def _minimum_node_eta(raw_vector: np.ndarray) -> float:
    unpacked = unpack_reduced(raw_vector)
    q = np.asarray(unpacked["coordinates"])
    m = np.asarray(unpacked["multipliers"])
    return float(min(
        eta_legendre_minimum(q[index], m[index])["minimum"]
        for index in range(len(q))
    ))


def safeguarded_seed_newton_step(
    *,
    relative_step: float = 1.0e-4,
    trust_radius: float = 1.0e-1,
) -> dict[str, Any]:
    assembled = seed_kkt_jacobian(relative_step=relative_step)
    matrix = np.asarray(assembled["KKT_jacobian"])
    residual = np.asarray(assembled["scaled_residual"])
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    direction = np.linalg.lstsq(matrix, -residual, rcond=1.0e-10)[0]
    newton_norm = float(np.linalg.norm(direction))
    trust_factor = min(1.0, trust_radius / max(newton_norm, 1.0e-300))
    direction *= trust_factor
    predicted = residual + matrix @ direction
    seed_norm = float(np.linalg.norm(residual))
    scales = kkt_variable_scales()
    y0 = np.asarray(assembled["scaled_seed"])
    trials = []
    accepted: dict[str, Any] | None = None
    for backtrack in range(18):
        fraction = 0.5**backtrack
        candidate = y0 + fraction * direction
        raw_candidate = candidate / scales
        try:
            eta_minimum = _minimum_node_eta(raw_candidate)
            if eta_minimum <= 1.0e-5:
                raise ValueError("eta Legendre form became singular")
            candidate_residual = scaled_analytic_kkt_residual(candidate)
            candidate_norm = float(np.linalg.norm(candidate_residual))
            row = {
                "backtrack": backtrack,
                "fraction": fraction,
                "eta_minimum": eta_minimum,
                "residual_norm": candidate_norm,
                "event_residual": float(candidate_residual[-1]),
                "domain_valid": True,
            }
            trials.append(row)
            if candidate_norm < seed_norm:
                accepted = {
                    **row,
                    "scaled_vector": candidate,
                    "raw_vector": raw_candidate,
                }
                break
        except (FloatingPointError, ValueError, np.linalg.LinAlgError) as exc:
            trials.append({
                "backtrack": backtrack,
                "fraction": fraction,
                "domain_valid": False,
                "exception": type(exc).__name__,
            })
    return {
        "relative_difference_step": relative_step,
        "trust_radius": trust_radius,
        "seed_residual_norm": seed_norm,
        "seed_eta_minimum": _minimum_node_eta(artifact_seed_vector()),
        "jacobian_symmetrization_relative_correction": assembled[
            "symmetrization_relative_correction"
        ],
        "jacobian_largest_singular_value": float(singular_values[0]),
        "jacobian_smallest_singular_value": float(singular_values[-1]),
        "jacobian_condition_number": float(
            singular_values[0] / singular_values[-1]
        ),
        "numerical_ranks": {
            f"relative_{tolerance:.0e}": int(np.sum(
                singular_values > tolerance * singular_values[0]
            ))
            for tolerance in (1.0e-8, 1.0e-10, 1.0e-12)
        },
        "unrestricted_newton_direction_norm": newton_norm,
        "trust_factor": trust_factor,
        "trusted_linear_predicted_residual_norm": float(
            np.linalg.norm(predicted)
        ),
        "trials": trials,
        "accepted": accepted,
    }


def completion_payload() -> dict[str, Any]:
    result = safeguarded_seed_newton_step()
    accepted = result["accepted"]
    validation = {
        "complete_jacobian_finite": math.isfinite(
            result["jacobian_condition_number"]
        ),
        "eta_domain_preserved": bool(
            accepted is not None and accepted["eta_minimum"] > 1.0e-5
        ),
        "complete_residual_reduced": bool(
            accepted is not None
            and accepted["residual_norm"] < result["seed_residual_norm"]
        ),
    }
    if accepted is not None:
        accepted = dict(accepted)
        accepted["raw_vector_hex"] = [
            float(value).hex() for value in accepted["raw_vector"]
        ]
        accepted.pop("scaled_vector")
        accepted.pop("raw_vector")
    return {
        "artifact": "BHSM_aether_n3_kkt_newton_step_v16_13",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "newton_step": {**result, "accepted": accepted},
        "dependency_advanced": (
            "FIRST_DOMAIN-PRESERVING_RESIDUAL-REDUCING_STEP_OF_THE_COMMON_"
            "N3_REPLACEMENT_EVENT-KKT_SOLVE"
        ),
        "active_calculation": (
            "ITERATE_THE_SAFEGUARDED_KKT_SOLVE_TO_A_NONLINEAR_STATIONARY_EVENT"
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
    path = target / "BHSM_aether_n3_kkt_newton_step_v16_13.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "artifact_seed_vector", "scaled_action_gradient", "kkt_jacobian_at",
    "seed_kkt_jacobian",
    "safeguarded_seed_newton_step", "completion_payload",
    "deterministic_json", "materialize",
]
