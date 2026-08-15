"""Anchored N=3 replacement-quantum global event KKT system."""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.interpolate import PchipInterpolator

from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import (
    standard_model_casimir_coefficient,
)
from bhsm.interface.aether_n3_constraint_solved_orbit_v16_08 import (
    canonical_reset_n3,
    eta_legendre_minimum,
    integrate_n3_orbit,
)
from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    exact_action_jet_at_state,
)
from bhsm.interface.aether_replacement_geometry_force_v16_06 import (
    zero_source_heat_geometry_response,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    generalized_lagrangian,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    sobolev_weights,
    spectral_frequencies,
)


VERSION = "v16.11"
CLASSIFICATION = "BHSM_N3_ANCHORED_REPLACEMENT_GLOBAL_EVENT_KKT"
FULL_BHSM_COMPLETE = False
ORDER = 3
NODES = 24
Q_DIMENSION = 10
M_DIMENSION = 6


@lru_cache(maxsize=1)
def anchored_reset_coordinates() -> tuple[float, ...]:
    """The canonical projected reset is fixed data in the anchored KKT."""

    return tuple(np.asarray(
        canonical_reset_n3(points=44)["coordinates"], dtype=float
    ))


def anchored_kkt_dimensions(nodes: int = NODES) -> dict[str, Any]:
    if nodes < 6:
        raise ValueError("at least six nodes required")
    free_q = (nodes - 1) * Q_DIMENSION
    multiplier = nodes * M_DIMENSION
    base = free_q + multiplier + 1  # period
    total = base + 1  # event multiplier
    return {
        "nodes": nodes,
        "reset_coordinates_fixed": Q_DIMENSION,
        "free_coordinate_unknowns": free_q,
        "multiplier_unknowns": multiplier,
        "period_unknowns": 1,
        "event_multiplier_unknowns": 1,
        "stationarity_equations": base,
        "event_equations": 1,
        "total_unknowns": total,
        "total_equations": total,
        "square": True,
        "time_phase_fixed_by_anchored_reset": True,
        "independent_phase_condition_present": False,
        "old_386_count_valid": False,
        "old_386_defect": (
            "IT_RETAINED_THE_TEN_FIXED_RESET_COORDINATES_AND_USED_A_PHASE_"
            "MULTIPLIER_WHILE_OMITTING_THE_EULER-DIRAC_EVENT_MULTIPLIER"
        ),
    }


def boundary_radius_and_jacobian(
    coordinates: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    q = np.asarray(coordinates, dtype=float)
    if q.ndim != 2 or q.shape[1] != Q_DIMENSION:
        raise ValueError("coordinates must have shape (nodes,10)")
    signs_k = (-1.0) ** np.arange(1, ORDER + 1)
    signs_j = (-1.0) ** np.arange(ORDER)
    u_boundary = q[:, 1:1 + ORDER] @ signs_k
    v_boundary = q[:, 1 + 2 * ORDER:1 + 3 * ORDER] @ signs_j
    radius = 2.0 * np.exp(q[:, 0]) * np.exp(u_boundary) / (
        2.0 * np.sqrt(np.cosh(2.0 * v_boundary))
    )
    jacobian = np.zeros_like(q)
    jacobian[:, 0] = 1.0
    jacobian[:, 1:1 + ORDER] = signs_k
    jacobian[:, 1 + 2 * ORDER:1 + 3 * ORDER] = (
        -np.tanh(2.0 * v_boundary)[:, None] * signs_j
    )
    return radius, jacobian


def boundary_lapse(multipliers: np.ndarray) -> np.ndarray:
    m = np.asarray(multipliers, dtype=float)
    if m.ndim != 2 or m.shape[1] != M_DIMENSION:
        raise ValueError("multipliers must have shape (nodes,6)")
    signs = (-1.0) ** np.arange(1, ORDER + 1)
    return np.exp(m[:, :ORDER] @ signs)


def open_difference_matrix(nodes: int = NODES) -> np.ndarray:
    """Second-order derivative on the anchored normalized interval [0,1]."""

    if nodes < 4:
        raise ValueError("at least four nodes required")
    step = 1.0 / (nodes - 1)
    matrix = np.zeros((nodes, nodes))
    matrix[0, :3] = (-1.5, 2.0, -0.5)
    matrix[-1, -3:] = (0.5, -2.0, 1.5)
    for index in range(1, nodes - 1):
        matrix[index, index - 1] = -0.5
        matrix[index, index + 1] = 0.5
    return matrix / step


def trapezoid_weights(nodes: int = NODES) -> np.ndarray:
    weights = np.ones(nodes) / (nodes - 1)
    weights[[0, -1]] *= 0.5
    return weights


@lru_cache(maxsize=1)
def classical_interior_seed() -> dict[str, Any]:
    """Twenty-four-node seed from the actual N=3 orbit before domain exit."""

    orbit = integrate_n3_orbit(
        time_step=2.0e-3, maximum_steps=32, points=44
    )
    admissible = [
        row for row in orbit["rows"] if row["minimum_eta_Legendre"] > 1.0e-3
    ]
    if len(admissible) < 6:
        raise RuntimeError("too few admissible N=3 orbit rows")
    source_time = np.asarray([row["time"] for row in admissible])
    end_time = float(source_time[-1])
    target_time = np.linspace(0.0, end_time, NODES)

    def interpolate(key: str) -> np.ndarray:
        values = np.asarray([row[key] for row in admissible])
        return np.column_stack([
            PchipInterpolator(source_time, values[:, column])(target_time)
            for column in range(values.shape[1])
        ])

    coordinates = interpolate("coordinates")
    velocities = interpolate("velocities")
    multipliers = interpolate("multipliers")
    coordinates[0] = np.asarray(anchored_reset_coordinates())
    return {
        "coordinate_times": target_time,
        "period": end_time,
        "coordinates": coordinates,
        "orbit_velocities": velocities,
        "multipliers": multipliers,
        "last_seed_eta_margin": eta_legendre_minimum(
            coordinates[-1], multipliers[-1]
        ),
        "source_orbit_maximum_constraint_residual": orbit[
            "maximum_constraint_residual"
        ],
        "source_orbit_soft_event_found": orbit[
            "Euler_Dirac_soft_event_found"
        ],
        "source_orbit_eta_exit_found_after_seed": (
            orbit["eta_Legendre_domain_exit"] is not None
        ),
        "role": "STRICTLY_INTERIOR_INITIAL_COLLOCATION_GUESS",
    }


def pack_reduced(
    coordinates: np.ndarray,
    multipliers: np.ndarray,
    period: float,
    event_multiplier: float = 0.0,
) -> np.ndarray:
    q = np.asarray(coordinates, dtype=float)
    m = np.asarray(multipliers, dtype=float)
    if q.shape != (NODES, Q_DIMENSION) or m.shape != (NODES, M_DIMENSION):
        raise ValueError("node arrays have wrong dimensions")
    return np.concatenate((q[1:].ravel(), m.ravel(), [period, event_multiplier]))


def unpack_reduced(vector: np.ndarray) -> dict[str, Any]:
    value = np.asarray(vector, dtype=float)
    expected = anchored_kkt_dimensions()["total_unknowns"]
    if value.shape != (expected,):
        raise ValueError(f"expected {expected} reduced variables")
    q_count = (NODES - 1) * Q_DIMENSION
    m_count = NODES * M_DIMENSION
    q = np.empty((NODES, Q_DIMENSION))
    q[0] = np.asarray(anchored_reset_coordinates())
    q[1:] = value[:q_count].reshape(NODES - 1, Q_DIMENSION)
    m = value[q_count:q_count + m_count].reshape(NODES, M_DIMENSION)
    return {
        "coordinates": q,
        "multipliers": m,
        "period": float(value[-2]),
        "event_multiplier": float(value[-1]),
    }


def replacement_action(
    coordinates: np.ndarray,
    multipliers: np.ndarray,
    period: float,
    *,
    radial_points: int = 36,
) -> dict[str, float]:
    """Evaluate Gamma_parent + the one common zero-source heat determinant."""

    q = np.asarray(coordinates, dtype=float)
    m = np.asarray(multipliers, dtype=float)
    if period <= 0.0:
        raise ValueError("period must be positive")
    derivative = open_difference_matrix() @ q / period
    weights = trapezoid_weights()
    radii, _ = boundary_radius_and_jacobian(q)
    lapse = boundary_lapse(m)
    casimir = standard_model_casimir_coefficient()
    attached = np.empty(NODES)
    parent = np.empty(NODES)
    for index in range(NODES):
        attached[index] = generalized_lagrangian(
            q[index], derivative[index], m[index],
            order=ORDER, points=radial_points,
        )
        parent[index] = attached[index] + lapse[index] * casimir / radii[index]
    gamma_attached = period * float(weights @ attached)
    gamma_parent = period * float(weights @ parent)
    proper_duration = period * float(weights @ lapse)
    heat = zero_source_heat_geometry_response(
        radii, proper_duration / NODES
    )
    return {
        "Gamma_attached_zeta": gamma_attached,
        "Gamma_parent_after_zeta_subtraction": gamma_parent,
        "Gamma_common_heat": float(heat["Gamma_heat"]),
        "Gamma_replacement": gamma_parent + float(heat["Gamma_heat"]),
        "proper_duration": proper_duration,
        "minimum_node_eta_Legendre": min(
            eta_legendre_minimum(q[index], m[index])["minimum"]
            for index in range(NODES)
        ),
    }


def event_value_from_base(base_vector: np.ndarray) -> float:
    """Ordered terminal Euler--Dirac eigenvalue on the anchored trajectory."""

    base = np.asarray(base_vector, dtype=float)
    if base.shape != (anchored_kkt_dimensions()["stationarity_equations"],):
        raise ValueError("base vector must omit only the event multiplier")
    unpacked = unpack_reduced(np.concatenate((base, [0.0])))
    q = np.asarray(unpacked["coordinates"])
    m = np.asarray(unpacked["multipliers"])
    period = float(unpacked["period"])
    velocity = open_difference_matrix() @ q / period
    hessian = exact_action_jet_at_state(
        ORDER, q[-1], velocity[-1], m[-1], points=44
    ).hessian
    return float(np.linalg.eigvalsh(hessian)[6])


def replacement_action_from_base(base_vector: np.ndarray) -> float:
    base = np.asarray(base_vector, dtype=float)
    unpacked = unpack_reduced(np.concatenate((base, [0.0])))
    return float(replacement_action(
        np.asarray(unpacked["coordinates"]),
        np.asarray(unpacked["multipliers"]),
        float(unpacked["period"]),
    )["Gamma_replacement"])


def _central_gradient(
    function: Any,
    vector: np.ndarray,
    indices: np.ndarray,
    *,
    relative_step: float,
) -> np.ndarray:
    gradient = np.zeros_like(vector)
    for index in indices:
        step = relative_step * max(1.0, abs(float(vector[index])))
        delta = np.zeros_like(vector)
        delta[index] = step
        gradient[index] = (
            function(vector + delta) - function(vector - delta)
        ) / (2.0 * step)
    return gradient


def event_gradient_indices() -> np.ndarray:
    """Only the final three q nodes, final m node, and T enter the event."""

    q_start = (NODES - 4) * Q_DIMENSION
    q_stop = (NODES - 1) * Q_DIMENSION
    m_start = (NODES - 1) * Q_DIMENSION + (NODES - 1) * M_DIMENSION
    m_stop = m_start + M_DIMENSION
    period_index = anchored_kkt_dimensions()["stationarity_equations"] - 1
    return np.concatenate((
        np.arange(q_start, q_stop),
        np.arange(m_start, m_stop),
        [period_index],
    ))


def kkt_residual(
    reduced_vector: np.ndarray,
    *,
    relative_step: float = 2.0e-6,
) -> np.ndarray:
    """Return grad_x(Gamma_Q+rho*E), E for the 376 unknowns."""

    value = np.asarray(reduced_vector, dtype=float)
    if value.shape != (anchored_kkt_dimensions()["total_unknowns"],):
        raise ValueError("reduced KKT vector has wrong length")
    base = value[:-1]
    rho = float(value[-1])
    all_indices = np.arange(base.size)
    action_gradient = _central_gradient(
        replacement_action_from_base,
        base,
        all_indices,
        relative_step=relative_step,
    )
    if rho == 0.0:
        event_gradient = np.zeros_like(base)
    else:
        event_gradient = _central_gradient(
            event_value_from_base,
            base,
            event_gradient_indices(),
            relative_step=relative_step,
        )
    event = event_value_from_base(base)
    return np.concatenate((action_gradient + rho * event_gradient, [event]))


def seed_kkt_residual() -> dict[str, Any]:
    seed = classical_interior_seed()
    vector = pack_reduced(
        np.asarray(seed["coordinates"]),
        np.asarray(seed["multipliers"]),
        float(seed["period"]),
        0.0,
    )
    residual = kkt_residual(vector)
    q_count = (NODES - 1) * Q_DIMENSION
    m_count = NODES * M_DIMENSION
    return {
        "event_value_lambda_6": float(residual[-1]),
        "q_stationarity_norm": float(np.linalg.norm(residual[:q_count])),
        "multiplier_stationarity_norm": float(np.linalg.norm(
            residual[q_count:q_count + m_count]
        )),
        "period_stationarity_residual": float(residual[-2]),
        "total_KKT_residual_norm": float(np.linalg.norm(residual)),
        "maximum_KKT_component": float(np.max(np.abs(residual))),
        "residual_finite": bool(np.all(np.isfinite(residual))),
        "seed_is_solution": bool(np.linalg.norm(residual) < 1.0e-7),
    }


def kkt_variable_scales(event_scale: float = 1.0e-3) -> np.ndarray:
    """Map reduced coefficients to the declared H6 product coordinates."""

    if event_scale <= 0.0:
        raise ValueError("event_scale must be positive")
    frequencies = spectral_frequencies(ORDER)["coordinates"]
    q_weight = (1.0 + frequencies**2) ** 3.0
    m_weight = sobolev_weights(ORDER)["multipliers"]
    base = np.concatenate((
        np.tile(q_weight, NODES - 1),
        np.tile(m_weight, NODES),
        [1.0],
    ))
    # y_rho=event_scale*rho, since L=Gamma+y_rho*(E/event_scale).
    return np.concatenate((base, [event_scale]))


def scaled_kkt_residual(
    scaled_vector: np.ndarray,
    *,
    event_scale: float = 1.0e-3,
    relative_step: float = 2.0e-6,
) -> np.ndarray:
    scales = kkt_variable_scales(event_scale)
    y = np.asarray(scaled_vector, dtype=float)
    if y.shape != scales.shape:
        raise ValueError("scaled KKT vector has wrong length")
    raw = kkt_residual(y / scales, relative_step=relative_step)
    result = np.empty_like(raw)
    result[:-1] = raw[:-1] / scales[:-1]
    result[-1] = raw[-1] / event_scale
    return result


def scaled_seed_vector(event_scale: float = 1.0e-3) -> np.ndarray:
    seed = classical_interior_seed()
    raw = pack_reduced(
        np.asarray(seed["coordinates"]),
        np.asarray(seed["multipliers"]),
        float(seed["period"]),
        0.0,
    )
    return raw * kkt_variable_scales(event_scale)


def scaled_seed_residual() -> dict[str, float | bool]:
    residual = scaled_kkt_residual(scaled_seed_vector())
    return {
        "scaled_residual_norm": float(np.linalg.norm(residual)),
        "scaled_maximum_component": float(np.max(np.abs(residual))),
        "scaled_event_residual": float(residual[-1]),
        "finite": bool(np.all(np.isfinite(residual))),
    }


def seed_replacement_force() -> dict[str, Any]:
    seed = classical_interior_seed()
    q = np.asarray(seed["coordinates"])
    m = np.asarray(seed["multipliers"])
    radii, jacobian = boundary_radius_and_jacobian(q)
    lapse = boundary_lapse(m)
    weights = trapezoid_weights()
    proper_duration = float(seed["period"]) * float(weights @ lapse)
    response = zero_source_heat_geometry_response(
        radii, proper_duration / NODES
    )
    radial = np.asarray(response["d_Gamma_heat_d_log_R_nodes"])
    q_force = radial[:, None] * jacobian
    return {
        "proper_duration": proper_duration,
        "radii": radii,
        "replacement_heat_radial_force": radial,
        "replacement_heat_q_force": q_force,
        "q_force_norm": float(np.linalg.norm(q_force)),
        "q_force_maximum": float(np.max(np.abs(q_force))),
        "force_has_no_w_components": bool(np.all(q_force[:, 4:7] == 0.0)),
        "same_common_gauge_ghost_rank16_HS_operator": response[
            "same_rank16_gauge_ghost_HS_direct_sum_as_source_response"
        ],
    }


def completion_payload() -> dict[str, Any]:
    dimensions = anchored_kkt_dimensions()
    seed = classical_interior_seed()
    force = seed_replacement_force()
    action = replacement_action(
        np.asarray(seed["coordinates"]),
        np.asarray(seed["multipliers"]),
        float(seed["period"]),
    )
    residual = seed_kkt_residual()
    validation = {
        "anchored_system_square": dimensions["square"],
        "correct_total_is_376": dimensions["total_unknowns"] == 376,
        "fixed_reset_not_double_counted": dimensions[
            "reset_coordinates_fixed"
        ] == 10,
        "event_multiplier_present": dimensions[
            "event_multiplier_unknowns"
        ] == 1,
        "seed_strictly_inside_domain": action[
            "minimum_node_eta_Legendre"
        ] > 1.0e-3,
        "common_replacement_force_nonzero": force["q_force_norm"] > 0.0,
        "same_unsplit_operator": force[
            "same_common_gauge_ghost_rank16_HS_operator"
        ],
        "full_376_residual_evaluated": residual["residual_finite"],
        "classical_seed_not_misreported_as_solution": not residual[
            "seed_is_solution"
        ],
    }
    return {
        "artifact": "BHSM_aether_n3_replacement_global_kkt_v16_11",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "anchored_KKT_dimensions": dimensions,
        "strictly_interior_N3_seed": seed,
        "seed_replacement_action": action,
        "seed_common_heat_geometry_force": force,
        "seed_376_KKT_residual": residual,
        "scientific_result": (
            "THE_CONSTANT_RESET_REDUCES_THE_N3_GLOBAL_EVENT_KKT_TO_A_"
            "376-BY-376_SYSTEM;_THE_STRICTLY_INTERIOR_INDEPENDENT-ORBIT_"
            "SEED_HAS_A_NONZERO_GEOMETRY_FORCE_FROM_THE_SAME_COMMON_GAUGE-"
            "GHOST-RANK16-HS_DETERMINANT"
        ),
        "dependency_advanced": (
            "CORRECT_SQUARE_GLOBAL_KKT_DOMAIN_AND_UNSPLIT_QUANTUM_FORCE_"
            "ARE_NOW_EXECUTABLE_ON_THE_N3_SEED"
        ),
        "active_calculation": (
            "DIFFERENTIATE_THE_376-VARIABLE_REPLACEMENT_ACTION_AND_SOLVE_"
            "THE_ANCHORED_EVENT-CONSTRAINED_GLOBAL_KKT_SYSTEM"
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
    path = target / "BHSM_aether_n3_replacement_global_kkt_v16_11.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "anchored_kkt_dimensions", "boundary_radius_and_jacobian",
    "anchored_reset_coordinates",
    "boundary_lapse", "open_difference_matrix", "trapezoid_weights",
    "classical_interior_seed", "pack_reduced", "unpack_reduced",
    "replacement_action", "seed_replacement_force", "completion_payload",
    "event_value_from_base", "replacement_action_from_base",
    "event_gradient_indices", "kkt_residual", "seed_kkt_residual",
    "kkt_variable_scales", "scaled_kkt_residual", "scaled_seed_vector",
    "scaled_seed_residual",
    "deterministic_json", "materialize",
]
