"""Flux-balanced scalar event-to-child boundary solution at N=3."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    constraint_residual,
)
from bhsm.interface.aether_n3_admissible_child_cauchy_germ_v17_95 import (
    _trace_jacobian,
)
from bhsm.interface.aether_n3_child_constraint_cauchy_match_v17_94 import (
    _metric_radial_flux_covector,
)
from bhsm.interface.aether_n3_constraint_solved_orbit_v16_08 import (
    eta_legendre_minimum,
    exact_euler_dirac_acceleration,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    ORDER,
    unpack_reduced,
)
from bhsm.interface.aether_n3_required_child_cauchy_flux_v17_93 import (
    _canonical_pair,
)
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import (
    trapezoid_sbp_difference,
)
from bhsm.interface.aether_n3_scale_corrected_period_log_continuation_v17_76 import (
    v17_75_selected_raw_vector,
)


VERSION = "v17.96"
CLASSIFICATION = "BHSM_N3_SCALAR_COMPLETE_CHILD_BOUNDARY_SOLUTION"
FULL_BHSM_COMPLETE = False


_CHILD_Q = np.asarray([
    -0.00045965051596293, 0.02188002162100341,
    -0.01316529625950673, -0.02724528557417241,
    0.05741371898475173, -0.24544586628824214,
    0.00029483877378688, -0.08294341175226508,
    0.0276546641374421, 0.1382788342530939,
])
_CHILD_V = np.asarray([
    -0.3164417848600975, -0.14920507980732411,
    0.17271181547738393, -0.02396343522464803,
    -4.0689119493341845, -8.074368121715992,
    -2.0294204088499255, 0.3613752490579798,
    0.6009106918162113, 0.19656981161692708,
])
_CHILD_M = np.asarray([
    1.0487240321478257, 0.05889554316669618,
    0.8875389632874776, -0.15203345944831215,
    -0.12757562361675134, 0.8036660742821818,
])


def scalar_complete_child_boundary_solution() -> dict[str, Any]:
    state = unpack_reduced(v17_75_selected_raw_vector())
    q_history = np.asarray(state["coordinates"], dtype=float)
    multiplier_history = np.asarray(state["multipliers"], dtype=float)
    velocity_history = (
        trapezoid_sbp_difference() @ q_history / float(state["period"])
    )
    q_event = q_history[-1]
    velocity_event = velocity_history[-1]
    multipliers_event = multiplier_history[-1]
    event_momentum, _, event_lift, _ = _canonical_pair(
        q_event, velocity_event, multipliers_event
    )
    child_momentum, child_force, child_lift, _ = _canonical_pair(
        _CHILD_Q, _CHILD_V, _CHILD_M
    )

    trace_residual = _trace_jacobian() @ (_CHILD_Q - q_event)
    constraints = constraint_residual(
        ORDER, _CHILD_Q, _CHILD_V, _CHILD_M, points=44
    )
    momentum_residual = child_momentum - event_momentum
    eta_margin = eta_legendre_minimum(_CHILD_Q, _CHILD_M, points=10000)
    dynamics = exact_euler_dirac_acceleration(
        ORDER, _CHILD_Q, _CHILD_V, _CHILD_M, points=44
    )
    acceleration = np.asarray(dynamics["acceleration"], dtype=float)
    multiplier_rate = np.asarray(dynamics["multiplier_rate"], dtype=float)
    tangent_scale = max(
        1.0,
        float(np.max(np.abs(_CHILD_V))),
        float(np.max(np.abs(acceleration))),
        float(np.max(np.abs(multiplier_rate))),
    )
    event_covector, event_raw = _metric_radial_flux_covector(
        q_event, multipliers_event
    )
    child_covector, child_raw = _metric_radial_flux_covector(
        _CHILD_Q, _CHILD_M
    )
    event_flux = event_lift.T @ event_covector
    child_flux = child_lift.T @ child_covector

    flux_rows = []
    for relative_step in (8.0e-4, 4.0e-4, 2.0e-4, 1.0e-4):
        epsilon = relative_step / tangent_scale
        plus, _, _, _ = _canonical_pair(
            _CHILD_Q + epsilon * _CHILD_V,
            _CHILD_V + epsilon * acceleration,
            _CHILD_M + epsilon * multiplier_rate,
        )
        minus, _, _, _ = _canonical_pair(
            _CHILD_Q - epsilon * _CHILD_V,
            _CHILD_V - epsilon * acceleration,
            _CHILD_M - epsilon * multiplier_rate,
        )
        momentum_rate = (plus - minus) / (2.0 * epsilon)
        required_flux = -momentum_rate + child_force - event_flux
        residual = child_flux - required_flux
        flux_rows.append({
            "relative_step": relative_step,
            "absolute_step": epsilon,
            "attachment_momentum_rate": momentum_rate.tolist(),
            "required_child_flux": required_flux.tolist(),
            "dynamic_flux_residual": residual.tolist(),
            "dynamic_flux_residual_norm": float(np.linalg.norm(residual)),
        })
    flux_envelope = max(
        row["dynamic_flux_residual_norm"] for row in flux_rows
    )

    return {
        "source_event": "v17.75_selected_fine_period_log_mix_state",
        "child_state": {
            "coordinates": _CHILD_Q.tolist(),
            "velocities": _CHILD_V.tolist(),
            "multipliers": _CHILD_M.tolist(),
            "velocity_norm": float(np.linalg.norm(_CHILD_V)),
            "acceleration": acceleration.tolist(),
            "multiplier_rate": multiplier_rate.tolist(),
            "Dirac_condition_number": float(
                dynamics["Dirac_condition_number"]
            ),
            "eta_Legendre_minimum": eta_margin,
        },
        "F_child_scalar": {
            "trace_residual": trace_residual.tolist(),
            "maximum_trace_residual": float(np.max(np.abs(trace_residual))),
            "seven_constraint_residual": constraints.tolist(),
            "maximum_constraint_residual": float(np.max(np.abs(constraints))),
            "attachment_momentum_residual": momentum_residual.tolist(),
            "attachment_momentum_residual_norm": float(
                np.linalg.norm(momentum_residual)
            ),
            "event_projected_flux": event_flux.tolist(),
            "event_raw_metric_flux": event_raw,
            "child_projected_flux": child_flux.tolist(),
            "child_raw_metric_flux": child_raw,
            "child_instantaneous_force": child_force.tolist(),
            "resolved_momentum_rate_flux_rows": flux_rows,
            "dynamic_flux_residual_envelope": flux_envelope,
            "closed_to_resolved_derivative_tolerance": flux_envelope < 2.0e-5,
        },
        "selection_rule": (
            "CONTINUE_FROM_THE_V17_95_ADMISSIBLE_GERM_AND_SOLVE_THE_SAME_"
            "THREE_TRACE_SEVEN_CONSTRAINT_TWO_MOMENTUM_TWO_DYNAMIC_FLUX_"
            "ROWS_WITH_POSITIVE_ETA_HYPERREGULARITY"
        ),
        "interpretation": (
            "FINITE_NONZERO_VELOCITY_ACCELERATION_MOMENTUM_FORCE_AND_"
            "ONE_SIDED_FLUX_PERSIST;ONLY_THE_COUPLED_RELATIVE_BOUNDARY_"
            "RESIDUAL_IS_REQUIRED_TO_VANISH"
        ),
        "complete_F_child_ledger": {
            "gravity_eta_scalar_Cauchy_Calderon_block": "CLOSED_HERE",
            "event_core_pregeometric_generator_block": "OPEN",
            "gauge_spinor_ghost_Calderon_projector": "OPEN",
            "positive_time_persistence_interval": "OPEN",
            "complete_F_child_closed": False,
        },
    }


def completion_payload() -> dict[str, Any]:
    result = scalar_complete_child_boundary_solution()
    state = result["child_state"]
    scalar = result["F_child_scalar"]
    ledger = result["complete_F_child_ledger"]
    validation = {
        "trace_closed": scalar["maximum_trace_residual"] < 2.0e-9,
        "seven_constraints_closed": scalar[
            "maximum_constraint_residual"
        ] < 1.0e-9,
        "two_momenta_closed": scalar[
            "attachment_momentum_residual_norm"
        ] < 1.0e-7,
        "eta_hyperregular": state["eta_Legendre_minimum"]["minimum"] > 0.0,
        "nonzero_relative_motion_retained": state["velocity_norm"] > 1.0,
        "four_step_flux_envelope_closed": scalar[
            "closed_to_resolved_derivative_tolerance"
        ],
        "missing_blocks_not_hidden": (
            ledger["event_core_pregeometric_generator_block"] == "OPEN"
            and ledger["gauge_spinor_ghost_Calderon_projector"] == "OPEN"
            and ledger["positive_time_persistence_interval"] == "OPEN"
            and not ledger["complete_F_child_closed"]
        ),
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_scalar_complete_child_boundary_solution_v17_96",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "scalar_complete_child_boundary_solution": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_EVENT_SELECTS_A_CONSTRAINT_CONSISTENT_MOVING_CHILD_GERM_"
            "WHOSE_GRAVITY_ETA_SCALAR_DYNAMIC_BOUNDARY_LAW_CLOSES"
        ),
        "dependency_closed": (
            "N3_EVENT_TO_CHILD_GRAVITY_ETA_SCALAR_CAUCHY_CALDERON_MAP"
        ),
        "active_calculation": (
            "CLOSE_THE_EVENT_CORE_AND_GAUGE_SPINOR_GHOST_PROJECTED_"
            "CALDERON_BLOCKS_THEN_EVOLVE_A_POSITIVE_PERSISTENCE_INTERVAL"
        ),
        "direct_N3_solve_authorized_next": False,
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / (
        "BHSM_aether_n3_scalar_complete_child_boundary_solution_v17_96.json"
    )
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "scalar_complete_child_boundary_solution", "completion_payload",
    "materialize",
]
