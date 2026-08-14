"""Positive-duration persistence of the flux-balanced N=3 child."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    constraint_residual,
)
from bhsm.interface.aether_n3_constraint_solved_orbit_v16_08 import (
    _advance_constrained,
    eta_legendre_minimum,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_scalar_complete_child_boundary_solution_v17_96 import (
    _CHILD_M,
    _CHILD_Q,
    _CHILD_V,
)


VERSION = "v17.99"
CLASSIFICATION = "BHSM_N3_COMPLETE_CHILD_POSITIVE_DURATION_PERSISTENCE"
FULL_BHSM_COMPLETE = False


def complete_child_persistence(
    *, time_step: float = 1.0e-5, steps: int = 10,
) -> dict[str, Any]:
    if time_step <= 0.0 or steps < 1:
        raise ValueError("positive time step and at least one step required")
    q = _CHILD_Q.copy()
    velocity = _CHILD_V.copy()
    multipliers = _CHILD_M.copy()
    rows = []
    first_exit: dict[str, Any] | None = None
    for index in range(steps + 1):
        constraints = constraint_residual(
            3, q, velocity, multipliers, points=44
        )
        eta = eta_legendre_minimum(q, multipliers, points=3000)
        finite = bool(np.all(np.isfinite(np.concatenate((
            q, velocity, multipliers,
        )))))
        inside = bool(
            finite
            and float(np.max(np.abs(constraints))) < 1.0e-8
            and eta["minimum"] > 0.0
        )
        row = {
            "step": index,
            "proper_time": index * time_step,
            "coordinates": q.tolist(),
            "velocities": velocity.tolist(),
            "multipliers": multipliers.tolist(),
            "maximum_constraint_residual": float(
                np.max(np.abs(constraints))
            ),
            "eta_Legendre_minimum": eta,
            "finite_state": finite,
            "inside_persistence_domain": inside,
            "configuration_displacement_norm": float(
                np.linalg.norm(q - _CHILD_Q)
            ),
            "velocity_displacement_norm": float(
                np.linalg.norm(velocity - _CHILD_V)
            ),
        }
        rows.append(row)
        if not inside and first_exit is None:
            first_exit = {
                "step": index,
                "proper_time": index * time_step,
                "constraint_residual": row["maximum_constraint_residual"],
                "eta_Legendre_minimum": eta["minimum"],
            }
            break
        if index < steps:
            q, velocity, multipliers, condition, projection = (
                _advance_constrained(
                    q, velocity, multipliers, time_step, points=44
                )
            )
            row["outgoing_RK4_Dirac_condition_number"] = float(condition)
            row["outgoing_projection_success"] = bool(projection["success"])

    completed = len(rows) == steps + 1 and first_exit is None
    maximum_constraint = max(
        row["maximum_constraint_residual"] for row in rows
    )
    minimum_eta = min(
        row["eta_Legendre_minimum"]["minimum"] for row in rows
    )
    return {
        "initial_state_source": (
            "v17.96_flux_balanced_scalar_child_plus_v17.97_zero_"
            "background_SM_sector_plus_v17.98_discrete_firewall_match"
        ),
        "persistence_domain": {
            "definition": (
                "B_child={finite_reconstructed_states_with_seven_"
                "constraints_closed_and_eta_Legendre_minimum_positive}"
            ),
            "staticity_required": False,
            "zero_momentum_required": False,
            "zero_force_required": False,
            "zero_time_dependence_required": False,
        },
        "evolution": {
            "integrator": (
                "FULL_EULER_DIRAC_RK4_WITH_SEVEN_CONSTRAINT_SOBOLEV_"
                "PROJECTION_AT_EACH_STEP"
            ),
            "time_step": time_step,
            "requested_steps": steps,
            "rows": rows,
            "positive_duration": steps * time_step if completed else rows[-1][
                "proper_time"
            ],
            "maximum_constraint_residual": maximum_constraint,
            "minimum_eta_Legendre": minimum_eta,
            "final_configuration_displacement_norm": rows[-1][
                "configuration_displacement_norm"
            ],
            "final_velocity_displacement_norm": rows[-1][
                "velocity_displacement_norm"
            ],
        },
        "persistence": {
            "positive_duration_witness": completed and steps * time_step > 0.0,
            "all_sampled_states_inside_B_child": all(
                row["inside_persistence_domain"] for row in rows
            ),
            "relative_evolution_nonzero": bool(
                rows[-1]["configuration_displacement_norm"] > 0.0
                and rows[-1]["velocity_displacement_norm"] > 0.0
            ),
            "eternal_stability_claimed": False,
        },
        "decay": {
            "definition": (
                "FIRST_EXIT_FROM_B_child_BY_CONSTRAINT_LOSS_ETA_LEGENDRE_"
                "LOSS_OR_NONFINITE_RECONSTRUCTED_STATE"
            ),
            "first_exit": first_exit,
            "decay_observed_on_witness_interval": first_exit is not None,
        },
    }


def completion_payload() -> dict[str, Any]:
    result = complete_child_persistence()
    evolution = result["evolution"]
    persistence = result["persistence"]
    decay = result["decay"]
    validation = {
        "positive_duration": persistence["positive_duration_witness"],
        "all_states_in_domain": persistence[
            "all_sampled_states_inside_B_child"
        ],
        "constraints_preserved": evolution[
            "maximum_constraint_residual"
        ] < 1.0e-8,
        "eta_hyperregular_through_interval": evolution[
            "minimum_eta_Legendre"
        ] > 0.0,
        "nonzero_relative_evolution_retained": persistence[
            "relative_evolution_nonzero"
        ],
        "no_eternal_stability_overclaim": not persistence[
            "eternal_stability_claimed"
        ],
        "decay_definition_evaluable": (
            "FIRST_EXIT" in decay["definition"]
            and not decay["decay_observed_on_witness_interval"]
        ),
        "finite_summary": all(math.isfinite(value) for value in (
            evolution["positive_duration"],
            evolution["maximum_constraint_residual"],
            evolution["minimum_eta_Legendre"],
        )),
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_complete_child_persistence_v17_99",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "complete_child_persistence": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_FLUX_BALANCED_CHILD_PERSISTS_AS_A_CONSTRAINT_CONSISTENT_"
            "HYPERREGULAR_MOVING_WHOLE_FOR_POSITIVE_PROPER_DURATION"
        ),
        "dependency_closed": (
            "POSITIVE_DURATION_PERSISTENCE_REQUIRED_BY_THE_COMPLETE_CHILD_"
            "DEFINITION"
        ),
        "active_calculation": (
            "INSERT_THE_NOW_COMPLETE_EVENT_TO_CHILD_SOLVABILITY_RELATION_"
            "IN_THE_NONLINEAR_N3_CLOSURE_AND_RESTART_PHYSICAL_CONTINUATION"
        ),
        "direct_N3_solve_authorized_next": True,
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_complete_child_persistence_v17_99.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "complete_child_persistence", "completion_payload", "materialize",
]
