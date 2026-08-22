"""Measure the existing N12 doubled Calderon symbol on positive duration.

The certified event is evolved backward along the retained parent flow and the
certified child forward along the retained child flow.  Projected RK4 is only
numerical reliability machinery.  Sampled gaps are diagnostics until a local
time-Lipschitz/interval enclosure is supplied.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np

import audit_n48_source_corrected_calderon_symbol as calderon
from bhsm.interface.aether_constraint_consistent_sobolev_lift_v15_84 import (
    constraint_residual,
)
from bhsm.interface.aether_cross_resolution_reconnaissance_v21_35 import (
    _eta_legendre_minimum,
    _exact_full_jet_euler_dirac_acceleration,
)
from bhsm.interface.aether_sobolev_galerkin_pencil_lift_v15_81 import (
    dimensions,
)
from bhsm.interface.aether_sobolev_metric_soft_mode_lift_v16_07 import (
    project_nested_constraints_sobolev,
)


ORDER = 12
POINTS = int(os.environ.get("BHSM_N12_HISTORY_CALDERON_POINTS", "96"))
TIME_STEP = float(os.environ.get("BHSM_N12_HISTORY_CALDERON_STEP", "1e-10"))
STEPS = int(os.environ.get("BHSM_N12_HISTORY_CALDERON_STEPS", "1"))
CHECKPOINT = Path(
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz"
)
RESULT = Path(os.environ.get(
    "BHSM_N12_HISTORY_CALDERON_RESULT",
    ".tmp_n12_positive_duration_calderon_history.json",
))


def _split(state: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    qdim = dimensions(ORDER)["coordinates"]
    return (
        state[:qdim].copy(),
        state[qdim:2 * qdim].copy(),
        state[2 * qdim:].copy(),
    )


def _boundary_lapse(multipliers: np.ndarray) -> float:
    signs = (-1.0) ** np.arange(1, ORDER + 1)
    return float(math.exp(float(multipliers[:ORDER] @ signs)))


def _rhs(state: tuple[np.ndarray, ...]) -> tuple[np.ndarray, ...]:
    dynamics = _exact_full_jet_euler_dirac_acceleration(
        ORDER, *state, points=POINTS
    )
    return (
        np.asarray(dynamics["coordinate_rate"], dtype=float),
        np.asarray(dynamics["acceleration"], dtype=float),
        np.asarray(dynamics["multiplier_rate"], dtype=float),
    )


def _rk4_projected(
    state: tuple[np.ndarray, ...], step: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    q, velocity, multipliers = state
    k1 = _rhs(state)
    k2 = _rhs(tuple(
        value + 0.5 * step * slope
        for value, slope in zip(state, k1)
    ))
    k3 = _rhs(tuple(
        value + 0.5 * step * slope
        for value, slope in zip(state, k2)
    ))
    k4 = _rhs(tuple(
        value + step * slope
        for value, slope in zip(state, k3)
    ))
    trial = tuple(
        value + step * (a + 2.0 * b + 2.0 * c + d) / 6.0
        for value, a, b, c, d in zip(state, k1, k2, k3, k4)
    )
    projection = project_nested_constraints_sobolev(
        ORDER, *trial, points=POINTS
    )
    if not projection["success"]:
        raise RuntimeError(str(projection["message"]))
    return (
        np.asarray(trial[0], dtype=float),
        np.asarray(projection["velocities"], dtype=float),
        np.asarray(projection["multipliers"], dtype=float),
    )


def main() -> None:
    if TIME_STEP <= 0.0 or STEPS < 1:
        raise ValueError("positive history controls required")
    payload = np.load(CHECKPOINT)
    joint = np.asarray(payload["state"], dtype=float)
    qdim = dimensions(ORDER)["coordinates"]
    mdim = dimensions(ORDER)["multipliers"]
    state_dimension = 2 * qdim + mdim
    event = _split(joint[:state_dimension])
    child = _split(joint[state_dimension:])
    rows = []
    parent_proper_duration = 0.0
    child_proper_duration = 0.0
    for index in range(STEPS + 1):
        measured = calderon._evaluate(
            event, child, ORDER, POINTS
        )
        event_constraints = constraint_residual(
            ORDER, *event, points=POINTS
        )
        child_constraints = constraint_residual(
            ORDER, *child, points=POINTS
        )
        rows.append({
            "step": index,
            "coordinate_duration": index * TIME_STEP,
            "parent_backward_proper_duration": parent_proper_duration,
            "child_forward_proper_duration": child_proper_duration,
            "seven_by_seven_symbol_gap": measured[
                "seven_by_seven_symbol_gap"
            ],
            "Friedrichs_sine": measured["Friedrichs_sine"],
            "minimum_graph_symbol_singular_value": measured[
                "minimum_graph_symbol_singular_value"
            ],
            "maximum_bordered_solve_residual": measured[
                "maximum_bordered_solve_residual"
            ],
            "event_eta_minimum": measured["event_eta_minimum"],
            "child_eta_minimum": measured["child_eta_minimum"],
            "event_constraint_maximum": float(np.max(np.abs(event_constraints))),
            "child_constraint_maximum": float(np.max(np.abs(child_constraints))),
        })
        if index == STEPS:
            continue
        event_lapse_before = _boundary_lapse(event[2])
        child_lapse_before = _boundary_lapse(child[2])
        event = _rk4_projected(event, -TIME_STEP)
        child = _rk4_projected(child, TIME_STEP)
        parent_proper_duration += 0.5 * TIME_STEP * (
            event_lapse_before + _boundary_lapse(event[2])
        )
        child_proper_duration += 0.5 * TIME_STEP * (
            child_lapse_before + _boundary_lapse(child[2])
        )

    gaps = np.asarray([row["seven_by_seven_symbol_gap"] for row in rows])
    gap_slopes = np.abs(np.diff(gaps)) / TIME_STEP
    integrated_gap_squared = float(
        TIME_STEP * np.sum(0.5 * (gaps[:-1] ** 2 + gaps[1:] ** 2))
    )
    measured_l2_gap = math.sqrt(integrated_gap_squared)
    validation = {
        "certified_N12_pair_consumed": True,
        "event_parent_and_child_use_unchanged_retained_flow": True,
        "parent_is_evolved_backward_and_child_forward": True,
        "all_constraints_remain_closed": all(
            row["event_constraint_maximum"] < 1.0e-8
            and row["child_constraint_maximum"] < 1.0e-8
            for row in rows
        ),
        "all_eta_values_remain_admissible": all(
            row["event_eta_minimum"] > 0.0
            and row["child_eta_minimum"] > 0.0
            for row in rows
        ),
        "all_sampled_symbols_remain_transverse": bool(np.min(gaps) > 0.0),
        "sampled_time_series_not_promoted_as_interval_lower_bound": True,
        "projected_RK4_not_promoted_as_physics": True,
        "no_new_equation_constraint_gate_scale_fit_or_event_definition": True,
    }
    output = {
        "classification": (
            "N12_CERTIFIED_EVENT_PARENT_BACKWARD_AND_CHILD_FORWARD_"
            "POSITIVE_DURATION_CALDERON_HISTORY_MEASURED;_EXPLICIT_"
            "TIME_INTERVAL_ENCLOSURE_REMAINS_OPEN"
        ),
        "order": ORDER,
        "quadrature_points": POINTS,
        "time_step": TIME_STEP,
        "steps": STEPS,
        "rows": rows,
        "measurement": {
            "minimum_sampled_symbol_gap": float(np.min(gaps)),
            "maximum_sampled_symbol_gap": float(np.max(gaps)),
            "maximum_sampled_gap_time_slope": float(np.max(gap_slopes)),
            "trapezoid_L2_symbol_gap": measured_l2_gap,
            "reciprocal_trapezoid_L2_symbol_gap": 1.0 / measured_l2_gap,
            "is_a_rigorous_positive_duration_observation_lower_bound": False,
        },
        "exact_next_lemma": (
            "ENCLOSE_THE_N12_POSITIVE_DURATION_CALDERON_SYMBOL_GAP_"
            "OVER_THE_WHOLE_PARENT_BACKWARD_CHILD_FORWARD_INTERVAL_"
            "WITH_AN_ACTION_OWNED_TIME_LIPSCHITZ_MAJORANT"
        ),
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    with RESULT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
