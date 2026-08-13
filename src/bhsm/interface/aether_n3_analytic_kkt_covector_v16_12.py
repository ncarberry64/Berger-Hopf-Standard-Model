"""Chain-rule covector for the anchored N=3 replacement KKT system."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import (
    standard_model_casimir_coefficient,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    M_DIMENSION,
    NODES,
    ORDER,
    Q_DIMENSION,
    anchored_kkt_dimensions,
    boundary_lapse,
    boundary_radius_and_jacobian,
    classical_interior_seed,
    event_gradient_indices,
    event_value_from_base,
    kkt_variable_scales,
    open_difference_matrix,
    pack_reduced,
    replacement_action_from_base,
    trapezoid_weights,
    unpack_reduced,
)
from bhsm.interface.aether_replacement_geometry_force_v16_06 import (
    zero_source_heat_geometry_response,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    generalized_lagrangian,
)


VERSION = "v16.12"
CLASSIFICATION = "BHSM_N3_COMMON_REPLACEMENT_ANALYTIC_KKT_COVECTOR"
FULL_BHSM_COMPLETE = False


def _local_first_derivatives(
    q: np.ndarray,
    velocity: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int,
    relative_step: float,
) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    value = generalized_lagrangian(
        q, velocity, multipliers, order=ORDER, points=points
    )
    dq = np.empty(Q_DIMENSION)
    for index in range(Q_DIMENSION):
        step = relative_step * max(1.0, abs(float(q[index])))
        delta = np.zeros(Q_DIMENSION)
        delta[index] = step
        dq[index] = (
            generalized_lagrangian(
                q + delta, velocity, multipliers, order=ORDER, points=points
            )
            - generalized_lagrangian(
                q - delta, velocity, multipliers, order=ORDER, points=points
            )
        ) / (2.0 * step)
    dv = np.empty(Q_DIMENSION)
    for index in range(Q_DIMENSION):
        step = relative_step * max(1.0, abs(float(velocity[index])))
        delta = np.zeros(Q_DIMENSION)
        delta[index] = step
        dv[index] = (
            generalized_lagrangian(
                q, velocity + delta, multipliers, order=ORDER, points=points
            )
            - generalized_lagrangian(
                q, velocity - delta, multipliers, order=ORDER, points=points
            )
        ) / (2.0 * step)
    dm = np.empty(M_DIMENSION)
    for index in range(M_DIMENSION):
        step = relative_step * max(1.0, abs(float(multipliers[index])))
        delta = np.zeros(M_DIMENSION)
        delta[index] = step
        dm[index] = (
            generalized_lagrangian(
                q, velocity, multipliers + delta, order=ORDER, points=points
            )
            - generalized_lagrangian(
                q, velocity, multipliers - delta, order=ORDER, points=points
            )
        ) / (2.0 * step)
    return value, dq, dv, dm


def replacement_action_covector(
    base_vector: np.ndarray,
    *,
    radial_points: int = 36,
    relative_step: float = 2.0e-6,
) -> dict[str, Any]:
    """Return Gamma and its 375-component anchored chain-rule covector."""

    base = np.asarray(base_vector, dtype=float)
    expected = anchored_kkt_dimensions()["stationarity_equations"]
    if base.shape != (expected,):
        raise ValueError("base vector must omit only the event multiplier")
    unpacked = unpack_reduced(np.concatenate((base, [0.0])))
    q = np.asarray(unpacked["coordinates"])
    m = np.asarray(unpacked["multipliers"])
    period = float(unpacked["period"])
    if period <= 0.0:
        raise ValueError("period must be positive")

    difference = open_difference_matrix()
    weights = trapezoid_weights()
    velocity = difference @ q / period
    attached = np.empty(NODES)
    dq_local = np.empty((NODES, Q_DIMENSION))
    dv_local = np.empty((NODES, Q_DIMENSION))
    dm_local = np.empty((NODES, M_DIMENSION))
    for node in range(NODES):
        (
            attached[node], dq_local[node], dv_local[node], dm_local[node]
        ) = _local_first_derivatives(
            q[node], velocity[node], m[node], points=radial_points,
            relative_step=relative_step,
        )

    radii, log_radius_jacobian = boundary_radius_and_jacobian(q)
    lapse = boundary_lapse(m)
    casimir = standard_model_casimir_coefficient()
    restored_zeta = lapse * casimir / radii
    parent = attached + restored_zeta
    dq_local -= restored_zeta[:, None] * log_radius_jacobian
    lapse_signs = (-1.0) ** np.arange(1, ORDER + 1)
    dm_local[:, :ORDER] += restored_zeta[:, None] * lapse_signs

    dq = (
        period * weights[:, None] * dq_local
        + difference.T @ (weights[:, None] * dv_local)
    )
    dm = period * weights[:, None] * dm_local
    proper_lapse_sum = float(weights @ lapse)
    proper_duration = period * proper_lapse_sum
    heat = zero_source_heat_geometry_response(
        radii, proper_duration / NODES
    )
    radial_force = np.asarray(heat["d_Gamma_heat_d_log_R_nodes"])
    dq += radial_force[:, None] * log_radius_jacobian
    duration_force = float(heat["d_Gamma_heat_d_log_proper_step"])
    dm[:, :ORDER] += (
        duration_force
        * (weights * lapse / proper_lapse_sum)[:, None]
        * lapse_signs
    )
    dperiod = float(weights @ (
        parent - np.einsum("ij,ij->i", dv_local, velocity)
    )) + duration_force / period
    covector = np.concatenate((dq[1:].ravel(), dm.ravel(), [dperiod]))
    gamma = period * float(weights @ parent) + float(heat["Gamma_heat"])
    return {
        "Gamma_replacement": gamma,
        "covector": covector,
        "coordinate_covector": dq,
        "multiplier_covector": dm,
        "period_covector": dperiod,
        "proper_duration": proper_duration,
        "heat_log_proper_step_covector": duration_force,
        "same_common_gauge_ghost_rank16_HS_operator": heat[
            "same_rank16_gauge_ghost_HS_direct_sum_as_source_response"
        ],
    }


def event_covector(
    base_vector: np.ndarray,
    *,
    relative_step: float = 2.0e-7,
) -> np.ndarray:
    base = np.asarray(base_vector, dtype=float)
    result = np.zeros_like(base)
    for index in event_gradient_indices():
        step = relative_step * max(1.0, abs(float(base[index])))
        delta = np.zeros_like(base)
        delta[index] = step
        result[index] = (
            event_value_from_base(base + delta)
            - event_value_from_base(base - delta)
        ) / (2.0 * step)
    return result


def analytic_kkt_residual(reduced_vector: np.ndarray) -> np.ndarray:
    value = np.asarray(reduced_vector, dtype=float)
    if value.shape != (anchored_kkt_dimensions()["total_unknowns"],):
        raise ValueError("reduced KKT vector has wrong length")
    base = value[:-1]
    rho = float(value[-1])
    action = replacement_action_covector(base)
    stationarity = np.asarray(action["covector"])
    if rho != 0.0:
        stationarity = stationarity + rho * event_covector(base)
    return np.concatenate((stationarity, [event_value_from_base(base)]))


def scaled_analytic_kkt_residual(
    scaled_vector: np.ndarray, *, event_scale: float = 1.0e-3,
) -> np.ndarray:
    scales = kkt_variable_scales(event_scale)
    y = np.asarray(scaled_vector, dtype=float)
    raw = analytic_kkt_residual(y / scales)
    result = np.empty_like(raw)
    result[:-1] = raw[:-1] / scales[:-1]
    result[-1] = raw[-1] / event_scale
    return result


def seed_vector() -> np.ndarray:
    seed = classical_interior_seed()
    return pack_reduced(
        np.asarray(seed["coordinates"]), np.asarray(seed["multipliers"]),
        float(seed["period"]), 0.0,
    )


def chain_rule_directional_witness() -> dict[str, float]:
    vector = seed_vector()
    base = vector[:-1]
    covector = np.asarray(replacement_action_covector(base)["covector"])
    scales = kkt_variable_scales()[:-1]
    direction = np.cos(np.arange(base.size, dtype=float) + 0.37) / scales
    direction /= np.linalg.norm(direction)
    epsilon = 2.0e-6
    finite = (
        replacement_action_from_base(base + epsilon * direction)
        - replacement_action_from_base(base - epsilon * direction)
    ) / (2.0 * epsilon)
    analytic = float(covector @ direction)
    return {
        "analytic_directional_derivative": analytic,
        "finite_difference_directional_derivative": float(finite),
        "relative_residual": abs(analytic - finite) / max(1.0, abs(finite)),
    }


def completion_payload() -> dict[str, Any]:
    witness = chain_rule_directional_witness()
    vector = seed_vector()
    residual = analytic_kkt_residual(vector)
    scales = kkt_variable_scales()
    scaled = np.empty_like(residual)
    scaled[:-1] = residual[:-1] / scales[:-1]
    scaled[-1] = residual[-1] / 1.0e-3
    validation = {
        "chain_rule_matches_full_action_finite_difference": (
            witness["relative_residual"] < 2.0e-5
        ),
        "complete_376_covector_finite": bool(np.all(np.isfinite(residual))),
        "same_unsplit_operator": replacement_action_covector(vector[:-1])[
            "same_common_gauge_ghost_rank16_HS_operator"
        ],
        "proper_time_covector_nonzero": abs(replacement_action_covector(
            vector[:-1]
        )["heat_log_proper_step_covector"]) > 0.0,
    }
    return {
        "artifact": "BHSM_aether_n3_analytic_kkt_covector_v16_12",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "chain_rule_directional_witness": witness,
        "seed_residual": {
            "raw_norm": float(np.linalg.norm(residual)),
            "scaled_norm": float(np.linalg.norm(scaled)),
            "event_eigenvalue": float(residual[-1]),
            "scaled_event_residual": float(scaled[-1]),
        },
        "scientific_result": (
            "THE_375-COMPONENT_REPLACEMENT-ACTION_COVECTOR_NOW_INCLUDES_"
            "THE_RADIUS_AND_PROPER-TIME_RESPONSES_OF_ONE_COMMON_GAUGE-"
            "GHOST-RANK16-HS_PUSHFORWARD_AND_CLOSES_THE_MISSING_CHAIN-RULE_BLOCK"
        ),
        "dependency_advanced": (
            "THE_376-VARIABLE_N3_KKT_RESIDUAL_IS_NOW_ASSEMBLED_WITH_THE_"
            "FULL_COMMON_PUSHFORWARD_COVECTOR"
        ),
        "active_calculation": (
            "SOLVE_THE_ANALYTICALLY_ASSEMBLED_376-VARIABLE_EVENT-KKT_SYSTEM"
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
    path = target / "BHSM_aether_n3_analytic_kkt_covector_v16_12.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "replacement_action_covector", "event_covector",
    "analytic_kkt_residual", "scaled_analytic_kkt_residual", "seed_vector",
    "chain_rule_directional_witness", "completion_payload",
    "deterministic_json", "materialize",
]
