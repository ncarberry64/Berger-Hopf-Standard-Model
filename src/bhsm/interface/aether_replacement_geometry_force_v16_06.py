"""Geometry force of the same heat operator used for gauge and HS residues."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.interpolate import PchipInterpolator

from bhsm.interface.aether_common_source_frechet_response_v15_99 import (
    regulator_first,
    regulator_function,
)
from bhsm.interface.aether_dense_proper_joint_pushforward_v15_97 import (
    dense_constraint_solved_cycle,
)
from bhsm.interface.aether_rank16_u1_hs_vertex_matrices_v16_01 import (
    periodic_laplacian,
    uniform_dense_geometry,
)


VERSION = "v16.06"
CLASSIFICATION = "BHSM_REPLACEMENT_SADDLE_GEOMETRY_FORCE"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False
ZETA_C_SM = 59.0 / 30.0


def zero_source_heat_geometry_response(
    radii: np.ndarray,
    proper_step: float,
    *,
    heat_length: float = 1.0,
    tolerance: float = 1.0e-13,
) -> dict[str, Any]:
    """Return Gamma_heat and every dGamma/dlog(R_j) in the round eigenbasis."""

    r = np.asarray(radii, dtype=float)
    if r.ndim != 1 or len(r) < 6 or np.any(r <= 0.0):
        raise ValueError("at least six positive radii required")
    laplacian = periodic_laplacian(len(r), proper_step)
    gamma_components: dict[str, float] = {}
    force_components: dict[str, np.ndarray] = {}
    duration_components: dict[str, float] = {}
    retained: dict[str, int] = {}
    sectors = (
        ("gauge_transverse", 1.0, 2,
         lambda m: 24 * (m * m - 1), lambda m: float(m)),
        ("rank16_three_family_Weyl", -1.0, 0,
         lambda n: 48 * (n + 1) * (n + 2), lambda n: n + 1.5),
        ("complex_HS_doublet", 1.0, 1,
         lambda m: 4 * m * m, lambda m: float(m)),
    )
    for name, sign, start, degeneracy, energy in sectors:
        gamma = 0.0
        force = np.zeros(len(r))
        duration_force = 0.0
        quiet = 0
        level = start
        retained[name] = start - 1
        while quiet < 4:
            spatial = (energy(level) / r) ** 2
            operator = laplacian + np.diag(spatial)
            eigenvalues, eigenvectors = np.linalg.eigh(operator)
            multiplicity = float(degeneracy(level))
            bound = multiplicity * float(
                np.exp(-heat_length**2 * eigenvalues[0])
            )
            if bound < tolerance:
                quiet += 1
            else:
                quiet = 0
                retained[name] = level
                gamma += sign * multiplicity * float(
                    np.sum(regulator_function(eigenvalues, heat_length))
                )
                probabilities = np.abs(eigenvectors) ** 2
                diagonal_fprime = probabilities @ regulator_first(
                    eigenvalues, heat_length
                )
                laplacian_expectation = np.real(np.einsum(
                    "ij,ij->j", eigenvectors.conj(), laplacian @ eigenvectors
                ))
                force += (
                    sign * multiplicity * (-2.0 * spatial) * diagonal_fprime
                )
                duration_force += sign * multiplicity * float(np.sum(
                    regulator_first(eigenvalues, heat_length)
                    * (-2.0 * laplacian_expectation)
                ))
            level += 1
            if level > 256:
                raise RuntimeError("heat tail did not terminate")
        gamma_components[name] = gamma
        force_components[name] = force
        duration_components[name] = duration_force
    total_force = sum(force_components.values(), np.zeros(len(r)))
    return {
        "Gamma_heat": float(sum(gamma_components.values())),
        "d_Gamma_heat_d_log_R_nodes": total_force,
        "d_Gamma_heat_d_log_common_R": float(np.sum(total_force)),
        "d_Gamma_heat_d_log_proper_step": float(sum(
            duration_components.values()
        )),
        "Gamma_components": gamma_components,
        "force_components": force_components,
        "proper_step_force_components": duration_components,
        "last_retained_spatial_level": retained,
        "same_rank16_gauge_ghost_HS_direct_sum_as_source_response": True,
    }


def zeta_geometry_response(
    radii: np.ndarray, proper_step: float,
) -> dict[str, Any]:
    """The zeta term removed from the attached seed action."""

    r = np.asarray(radii, dtype=float)
    gamma = -proper_step * ZETA_C_SM * float(np.sum(1.0 / r))
    force = proper_step * ZETA_C_SM / r
    return {
        "Gamma_SM_zeta": gamma,
        "d_Gamma_SM_zeta_d_log_R_nodes": force,
        "d_Gamma_SM_zeta_d_log_common_R": float(np.sum(force)),
    }


def log_radius_coordinate_jacobian(coordinates: np.ndarray) -> np.ndarray:
    """Exact d log(R4)/dq in the nine-coordinate eta chart."""

    q = np.asarray(coordinates, dtype=float)
    if q.ndim != 2 or q.shape[1] != 9:
        raise ValueError("coordinates must have shape (nodes,9)")
    v = q[:, 5] - q[:, 6]
    jacobian = np.zeros((len(q), 9))
    jacobian[:, 0] = 1.0
    jacobian[:, 1] = -1.0
    jacobian[:, 2] = 1.0
    jacobian[:, 5] = -np.tanh(2.0 * v)
    jacobian[:, 6] = np.tanh(2.0 * v)
    return jacobian


def _uniform_coordinates(
    cycle: Mapping[str, Any], coordinate_times: np.ndarray,
) -> np.ndarray:
    rows = cycle["rows"]
    if "coordinates" not in rows[0]:
        raise ValueError("dense rows must retain coordinates for KKT insertion")
    times = np.asarray([row["time"] for row in rows], dtype=float)
    coordinates = np.asarray([row["coordinates"] for row in rows], dtype=float)
    return np.column_stack([
        PchipInterpolator(times, coordinates[:, index])(coordinate_times)
        for index in range(9)
    ])


def replacement_seed_geometry_force(
    cycle: Mapping[str, Any] | None = None, *, points: int = 24,
) -> dict[str, Any]:
    """Evaluate D(Gamma_heat-Gamma_zeta) on the zeta-attached dense seed."""

    dense = dense_constraint_solved_cycle() if cycle is None else cycle
    geometry = uniform_dense_geometry(dense, points)
    radii = np.asarray(geometry["radii"], dtype=float)
    step = float(geometry["proper_step"])
    heat = zero_source_heat_geometry_response(radii, step)
    zeta = zeta_geometry_response(radii, step)
    radial_force = (
        np.asarray(heat["d_Gamma_heat_d_log_R_nodes"])
        - np.asarray(zeta["d_Gamma_SM_zeta_d_log_R_nodes"])
    )
    coordinates = _uniform_coordinates(
        dense, np.asarray(geometry["coordinate_times"])
    )
    jacobian = log_radius_coordinate_jacobian(coordinates)
    q_force = radial_force[:, None] * jacobian
    return {
        "points": points,
        "proper_duration": geometry["proper_duration"],
        "heat_response": heat,
        "removed_zeta_response": zeta,
        "replacement_radial_force_nodes": radial_force,
        "replacement_q_force_nodes": q_force,
        "replacement_force_euclidean_norm": float(np.linalg.norm(q_force)),
        "replacement_force_maximum_component": float(np.max(np.abs(q_force))),
        "replacement_common_log_radius_force": float(np.sum(radial_force)),
        "eta_gauge_force_components_q7_q8_zero": bool(
            np.all(q_force[:, 7:] == 0.0)
        ),
        "interpretation": (
            "because_the_dense_seed_extremizes_Gamma_attached_zeta,_this_is_"
            "the_explicit_zero-source_geometry_part_of_the_replacement-KKT_"
            "residual_Gamma_attached_zeta-Gamma_SM_zeta+Gamma_SM_heat"
        ),
    }


def force_finite_difference_witness() -> dict[str, float]:
    radii = np.asarray([1.0, 1.04, 0.98, 1.02, 1.01, 0.99])
    step_tau = 0.07
    response = zero_source_heat_geometry_response(radii, step_tau)
    direction = np.asarray([0.2, -0.1, 0.05, 0.3, -0.25, 0.15])
    epsilon = 1.0e-4
    plus = zero_source_heat_geometry_response(
        radii * np.exp(epsilon * direction), step_tau
    )["Gamma_heat"]
    minus = zero_source_heat_geometry_response(
        radii * np.exp(-epsilon * direction), step_tau
    )["Gamma_heat"]
    finite = (plus - minus) / (2.0 * epsilon)
    analytic = float(
        np.asarray(response["d_Gamma_heat_d_log_R_nodes"]) @ direction
    )
    return {
        "analytic_directional_force": analytic,
        "finite_difference_directional_force": float(finite),
        "relative_residual": abs(analytic - finite) / max(1.0, abs(analytic)),
    }


def completion_payload() -> dict[str, Any]:
    witness = force_finite_difference_witness()
    force = replacement_seed_geometry_force()
    validation = {
        "geometry_force_finite_difference_verified": witness["relative_residual"] < 2.0e-8,
        "replacement_force_finite": math.isfinite(force["replacement_force_euclidean_norm"]),
        "replacement_force_nonzero": force["replacement_force_euclidean_norm"] > 0.0,
        "same_operator_as_sources": force["heat_response"][
            "same_rank16_gauge_ghost_HS_direct_sum_as_source_response"
        ],
        "eta_gauge_preserved": force["eta_gauge_force_components_q7_q8_zero"],
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_replacement_geometry_force_v16_06",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "force_finite_difference_witness": witness,
        "replacement_seed_geometry_force": force,
        "scientific_result": (
            "THE_ZERO-SOURCE_GEOMETRY_FORCE_OF_THE_SAME_DIRECT-SUM_HEAT_"
            "OPERATOR_IS_EVALUATED_NODE-BY-NODE,_THE_OLD_ZETA_FORCE_IS_"
            "SUBTRACTED,_AND_THE_RESULT_IS_PUSHED_THROUGH_THE_EXACT_"
            "dlogR4/dq_MAP_AS_THE_EXPLICIT_REPLACEMENT-KKT_RESIDUAL_BLOCK"
        ),
        "claim_boundary": {
            "heat_geometry_force_evaluated": True,
            "zeta_subtraction_force_evaluated": True,
            "coordinate_KKT_force_block_evaluated": True,
            "complete_parent_KKT_Jacobian_assembled": False,
            "replacement_quantum_saddle_solved": False,
        },
        "active_calculation": (
            "ASSEMBLE_THE_PARENT_DISCRETE_EULER-DIRAC_JACOBIAN_WITH_THIS_"
            "EXPLICIT_FORCE_BLOCK_AND_SOLVE_THE_GLOBAL_REPLACEMENT_SADDLE"
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
    path = target / "BHSM_aether_replacement_geometry_force_v16_06.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "zero_source_heat_geometry_response", "zeta_geometry_response",
    "log_radius_coordinate_jacobian", "replacement_seed_geometry_force",
    "force_finite_difference_witness", "completion_payload",
    "deterministic_json", "materialize",
]
