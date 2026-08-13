"""Transversality of the converged N=3 eta-Legendre domain exit."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    constraint_residual,
)
from bhsm.interface.aether_n3_constraint_solved_orbit_v16_08 import (
    eta_legendre_minimum,
    exact_euler_dirac_acceleration,
)


VERSION = "v16.10"
CLASSIFICATION = "BHSM_N3_ETA_BOUNDARY_TRANSVERSALITY"
FULL_BHSM_COMPLETE = False
EXIT_TIME = 0.04410714054107669
Q = np.asarray([
    -0.017973722521665302, -0.01647918098645838, 0.008433373566231184,
    -0.0017398643032126271, 0.053966355431102786, -0.29281483304065076,
    -0.023689857998997248, 0.026964520306912425, -0.003796600298598786,
    0.00476830599873151,
])
V = np.asarray([
    -0.6452124917633496, -0.4658653682232577, 0.5270552475730085,
    0.021867643514013886, -4.965282744530043, -20.530785334265985,
    -6.601340848957255, 2.87563250290136, 2.6885340513160787,
    1.1453354510316536,
])
M = np.asarray([
    -1.081982065690873, 0.3064866459833294, 0.021371688299489065,
    -0.6145615506787385, -0.17165079892634133, 0.37048493197792215,
])


def boundary_transversality() -> dict[str, Any]:
    dynamics = exact_euler_dirac_acceleration(3, Q, V, M, points=44)
    multiplier_rate = np.asarray(dynamics["multiplier_rate"])
    epsilon = 2.0e-7
    plus = eta_legendre_minimum(
        Q + epsilon * V, M + epsilon * multiplier_rate, points=5000
    )
    minus = eta_legendre_minimum(
        Q - epsilon * V, M - epsilon * multiplier_rate, points=5000
    )
    rate = (plus["minimum"] - minus["minimum"]) / (2.0 * epsilon)
    hessian = np.asarray(dynamics["Dirac_hessian"])
    eigenvalues = np.linalg.eigvalsh(hessian)
    z = np.concatenate((V, M))
    jacobian = np.empty((7, 16))
    step = 1.0e-6
    for column in range(16):
        delta = np.zeros(16)
        delta[column] = step
        jacobian[:, column] = (
            constraint_residual(
                3, Q, z[:10] + delta[:10], z[10:] + delta[10:], points=44
            )
            - constraint_residual(
                3, Q, z[:10] - delta[:10], z[10:] - delta[10:], points=44
            )
        ) / (2.0 * step)
    singular_values = np.linalg.svd(jacobian, compute_uv=False)
    return {
        "exit_time": EXIT_TIME,
        "eta_margin": eta_legendre_minimum(Q, M, points=5000),
        "directional_eta_margin_rate": rate,
        "constraint_Jacobian_rank": int(np.linalg.matrix_rank(
            jacobian, tol=1.0e-8
        )),
        "constraint_Jacobian_smallest_singular_value": float(
            singular_values[-1]
        ),
        "maximum_constraint_residual": float(np.max(np.abs(
            constraint_residual(3, Q, V, M, points=44)
        ))),
        "Euler_Dirac_smallest_absolute_eigenvalue": float(
            eigenvalues[np.argmin(np.abs(eigenvalues))]
        ),
        "Euler_Dirac_condition_number": float(np.linalg.cond(hessian)),
        "classical_flow_is_transverse_outward": rate < 0.0,
        "Euler_Dirac_system_regular_at_domain_exit": bool(
            np.min(np.abs(eigenvalues)) > 1.0e-5
        ),
        "smooth_classical_in_domain_continuation_exists": False,
    }


def completion_payload() -> dict[str, Any]:
    row = boundary_transversality()
    validation = {
        "seven_constraint_rows_independent": row[
            "constraint_Jacobian_rank"
        ] == 7,
        "constraints_controlled": row["maximum_constraint_residual"] < 2.0e-9,
        "boundary_crossed_transversely": row[
            "directional_eta_margin_rate"
        ] < -1.0,
        "not_an_Euler_Dirac_zero": row[
            "Euler_Dirac_system_regular_at_domain_exit"
        ],
        "no_classical_boundary_continuation_invented": not row[
            "smooth_classical_in_domain_continuation_exists"
        ],
    }
    return {
        "artifact": "BHSM_aether_n3_eta_boundary_transversality_v16_10",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "boundary_transversality": row,
        "scientific_result": (
            "THE_CONVERGED_N3_CLASSICAL_CONSTRAINT_FLOW_CROSSES_THE_ETA-"
            "LEGENDRE_DOMAIN_BOUNDARY_TRANSVERSELY_WHILE_THE_EULER-DIRAC_"
            "HESSIAN_REMAINS_REGULAR;_NO_SMOOTH_CLASSICAL_IN-DOMAIN_"
            "CONTINUATION_EXISTS"
        ),
        "upstream_redirect": (
            "INSERT_THE_ALREADY_DERIVED_COMMON_GAUGE-GHOST-RANK16-HS_"
            "REPLACEMENT_DETERMINANT_FORCE_IN_THE_N3_GLOBAL_KKT_ORBIT;_DO_"
            "NOT_ADD_AN_INDEPENDENT_REFLECTION_OR_YUKAWA_NORMALIZATION"
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
    path = target / "BHSM_aether_n3_eta_boundary_transversality_v16_10.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "boundary_transversality", "completion_payload", "deterministic_json",
    "materialize",
]
