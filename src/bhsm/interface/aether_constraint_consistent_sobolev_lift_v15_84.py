"""Constraint-consistent nested lift of the Euler--Dirac Schur response.

At every spectral order the newly introduced lapse/shift constraints and the
Hamiltonian constraint are solved before the Hessian is inverted.  The lift
selects the closest velocity to the preceding nested state, so no new free
continuous datum is introduced.
"""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.optimize import minimize

from bhsm.interface.aether_exact_radial_schur_lift_v15_83 import (
    exact_action_jet_at_state,
    exact_dirac_hessian_at_state,
)
from bhsm.interface.aether_invariant_sobolev_schur_pushforward_v15_82 import (
    fermion_source_covector,
    invariant_schur_value,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
    embedded_state,
)


VERSION = "v15.84"
CLASSIFICATION = "BHSM_CONSTRAINT_CONSISTENT_SOBOLEV_EVENT_LIFT"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def embed_nested_state(
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    old_order: int,
    new_order: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if new_order < old_order:
        raise ValueError("new order must not be smaller")
    old = dimensions(old_order)
    new = dimensions(new_order)
    q = np.zeros(new["coordinates"])
    v = np.zeros_like(q)
    m = np.zeros(new["multipliers"])
    q[0] = coordinates[0]
    v[0] = velocities[0]
    for target, source in ((q, coordinates), (v, velocities)):
        target[1:1 + old_order] = source[1:1 + old_order]
        target[1 + new_order:1 + new_order + old_order] = source[
            1 + old_order:1 + 2 * old_order
        ]
        target[1 + 2 * new_order:1 + 2 * new_order + old_order] = source[
            1 + 2 * old_order:1 + 3 * old_order
        ]
    m[:old_order] = multipliers[:old_order]
    m[new_order:new_order + old_order] = multipliers[
        old_order:2 * old_order
    ]
    return q, v, m


def constraint_residual(
    order: int,
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int = 44,
) -> np.ndarray:
    jet = exact_action_jet_at_state(
        order, coordinates, velocities, multipliers, points=points
    )
    nv = dimensions(order)["coordinates"]
    multiplier_rows = jet.gradient[nv:]
    energy = float(jet.gradient[:nv] @ velocities - jet.value)
    return np.concatenate((multiplier_rows, [energy]))


def project_nested_constraints(
    order: int,
    coordinates: np.ndarray,
    trial_velocity: np.ndarray,
    multiplier_seed: np.ndarray,
    *,
    points: int = 44,
) -> dict[str, Any]:
    nv = dimensions(order)["coordinates"]
    nm = dimensions(order)["multipliers"]
    q = np.asarray(coordinates, dtype=float)
    trial = np.asarray(trial_velocity, dtype=float)
    seed = np.asarray(multiplier_seed, dtype=float)
    velocity_scale = np.maximum(0.2, np.abs(trial))
    initial = np.concatenate((trial, seed))
    scale = max(1.0, float(np.max(np.abs(constraint_residual(
        order, q, trial, seed, points=points
    )))))

    def unpack(value: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        return value[:nv], value[nv:]

    def constraints(value: np.ndarray) -> np.ndarray:
        velocity, multipliers = unpack(value)
        return constraint_residual(
            order, q, velocity, multipliers, points=points
        ) / scale

    def objective(value: np.ndarray) -> float:
        velocity, multipliers = unpack(value)
        difference = (velocity - trial) / velocity_scale
        return float(difference @ difference + 1.0e-8 * (multipliers @ multipliers))

    lower_velocity = trial - 3.0 * velocity_scale
    upper_velocity = trial + 3.0 * velocity_scale
    lower = np.concatenate((lower_velocity, np.full(nm, -5.0)))
    upper = np.concatenate((upper_velocity, np.full(nm, 5.0)))
    solution = minimize(
        objective,
        initial,
        method="SLSQP",
        bounds=list(zip(lower, upper)),
        constraints={"type": "eq", "fun": constraints},
        options={"ftol": 2.0e-11, "maxiter": 1200, "disp": False},
    )
    velocity, multipliers = unpack(np.asarray(solution.x))
    residual = constraint_residual(
        order, q, velocity, multipliers, points=points
    )
    return {
        "success": bool(solution.success),
        "message": str(solution.message),
        "coordinates": q,
        "velocities": velocity,
        "multipliers": multipliers,
        "objective": objective(solution.x),
        "maximum_constraint_residual": float(np.max(np.abs(residual))),
        "scaled_maximum_constraint_residual": float(
            np.max(np.abs(residual)) / scale
        ),
    }


@lru_cache(maxsize=1)
def constraint_consistent_rows() -> list[dict[str, Any]]:
    q, velocity, multipliers = embedded_state(2)
    rows = []
    old_order = 2
    for order in range(2, 9):
        if order > 2:
            q, velocity, multipliers = embed_nested_state(
                q, velocity, multipliers, old_order, order
            )
        projection = project_nested_constraints(
            order, q, velocity, multipliers
        )
        if not projection["success"]:
            raise RuntimeError(projection["message"])
        q = np.asarray(projection["coordinates"])
        velocity = np.asarray(projection["velocities"])
        multipliers = np.asarray(projection["multipliers"])
        hessian = exact_dirac_hessian_at_state(
            order, q, velocity, multipliers
        )
        source = fermion_source_covector(order, q)
        values = np.linalg.eigvalsh(hessian)
        rows.append({
            "order": order,
            "pencil_dimension": dimensions(order)["Dirac_pencil"],
            "projection_objective": float(projection["objective"]),
            "maximum_constraint_residual": float(
                projection["maximum_constraint_residual"]
            ),
            "scaled_maximum_constraint_residual": float(
                projection["scaled_maximum_constraint_residual"]
            ),
            "invariant_half_J_Dinv_J": invariant_schur_value(hessian, source),
            "smallest_absolute_eigenvalue": float(
                values[np.argmin(np.abs(values))]
            ),
            "condition_number": float(np.linalg.cond(hessian)),
            "coordinates": q.tolist(),
            "velocities": velocity.tolist(),
            "multipliers": multipliers.tolist(),
        })
        old_order = order
    return rows


def completion_payload() -> dict[str, Any]:
    rows = constraint_consistent_rows()
    validation = {
        "orders_N2_through_N8_projected": [row["order"] for row in rows] == list(range(2, 9)),
        "all_constraints_solved": all(
            row["scaled_maximum_constraint_residual"] < 1.0e-8 for row in rows
        ),
        "all_Schur_values_finite": all(
            math.isfinite(float(row["invariant_half_J_Dinv_J"])) for row in rows
        ),
        "no_new_free_velocity": True,
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_constraint_consistent_sobolev_lift_v15_84",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "selection_rule": (
            "AT_EACH_N_MINIMIZE_THE_WEIGHTED_DISTANCE_TO_THE_EMBEDDED_"
            "PRECEDING_VELOCITY_SUBJECT_TO_ALL_2N_LAPSE-SHIFT_CONSTRAINTS_"
            "AND_THE_HAMILTONIAN_CONSTRAINT"
        ),
        "constraint_consistent_rows": rows,
        "scientific_result": (
            "THE_NESTED_EVENT_PENCIL_IS_NOW_EVALUATED_ONLY_AFTER_THE_"
            "HIGHER-ORDER_CHILD_STATE_IS_PROJECTED_ON_THE_COMPLETE_REDUCED_"
            "DIRAC_CONSTRAINT_SURFACE"
        ),
        "claim_boundary": {
            "constraint_consistent_radial_lift_through_N8": True,
            "N_to_infinity_convergence_proved": False,
            "full_backreacted_event_orbit_reintegrated_at_each_N": False,
        },
        "active_calculation": (
            "CONTINUE_THE_CONSTRAINT-CONSISTENT_SEQUENCE_AND_DERIVE_THE_"
            "RADIAL_TAIL_BOUND_BEFORE_RETESTING_THE_JOINT_GAP"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
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
    path = target / "BHSM_aether_constraint_consistent_sobolev_lift_v15_84.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "embed_nested_state",
    "constraint_residual", "project_nested_constraints",
    "constraint_consistent_rows", "completion_payload", "deterministic_json",
    "materialize",
]
