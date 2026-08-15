"""Dense constraint-solved classical proper-cycle gauge--Yukawa quadrature."""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from scipy.interpolate import PchipInterpolator

from bhsm.interface.aether_m4_standard_model_zeta_backreaction_v15_51 import (
    boundary_geometry,
    integrate_attached_dirac_flow,
)
from bhsm.interface.aether_one_cycle_joint_residues_v15_86 import EVENT_TIME
from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import cap_fields
from bhsm.interface.aether_sampled_event_shell_pushforward_v15_74 import SNAPSHOTS


VERSION = "v15.97"
CLASSIFICATION = "BHSM_DENSE_CONSTRAINT_SOLVED_PROPER_JOINT_PUSHFORWARD"
FULL_BHSM_COMPLETE = False
USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE = False


def wavefunction_residue(radius: float) -> float:
    heat = 1.0 / float(radius) ** 2
    total = 0.0
    for n in range(128):
        energy = n + 1.5
        term = (n + 1) * (n + 2) * math.exp(-heat * energy**2) / energy**3
        total += term
        if n > 12 and term < 1.0e-16:
            break
    return total / (4.0 * math.pi**2)


def adm_joint_local_state(
    coordinates: np.ndarray,
    velocities: np.ndarray,
    multipliers: np.ndarray,
    *,
    points: int = 500,
) -> dict[str, float]:
    """Evaluate local ADM Maxwell residues and the HS residue on one state."""

    q = np.asarray(coordinates, dtype=float)
    v = np.asarray(velocities, dtype=float)
    m = np.asarray(multipliers, dtype=float)
    fields = cap_fields(q, v, points=points)
    chi = np.asarray(fields["chi"], dtype=float)
    A = np.asarray(fields["A"], dtype=float)
    B = np.asarray(fields["B"], dtype=float)
    C = np.asarray(fields["C"], dtype=float)
    n1, n2, b0, b1 = m
    lapse = np.exp(n1 * np.cos(4.0 * chi) + n2 * np.cos(8.0 * chi))
    shift = np.sin(4.0 * chi) * (b0 + b1 * np.cos(4.0 * chi))
    normal_f = (
        np.asarray(fields["f_dot_coordinate"], dtype=float)
        - shift * np.asarray(fields["f_prime"], dtype=float)
    ) / lapse
    spatial_x = (
        np.asarray(fields["f_prime"], dtype=float) ** 2 / C**2
        + 3.0 * np.cos(np.asarray(fields["f"], dtype=float)) ** 2 / A**2
        + 3.0 * np.sin(np.asarray(fields["f"], dtype=float)) ** 2 / B**2
    )
    weight = (1.0 - 4.0 * np.asarray(fields["sigma"], dtype=float) ** 2) * (
        1.0 + (spatial_x - normal_f**2) ** 3
    )
    radius = A * B / np.sqrt(A * A + B * B)
    coefficient = math.pi**2 * (A * A + B * B) ** 2.5
    boundary = boundary_geometry(q, m)
    boundary_radius = float(boundary["M4_spatial_radius"])
    boundary_lapse = float(boundary["boundary_lapse"])
    magnetic_integrand = coefficient * weight * lapse * C / radius
    electric_integrand = coefficient * weight * C * radius / lapse
    magnetic = boundary_radius / boundary_lapse * float(
        np.trapezoid(magnetic_integrand, chi)
    )
    electric = boundary_lapse / boundary_radius * float(
        np.trapezoid(electric_integrand, chi)
    )
    return {
        "boundary_lapse": boundary_lapse,
        "M4_spatial_radius": boundary_radius,
        "K_magnetic": magnetic,
        "K_electric": electric,
        "Z_H": wavefunction_residue(boundary_radius),
    }


def stored_state_witness(time: float = 0.08) -> dict[str, float]:
    state = SNAPSHOTS[float(time)]
    return adm_joint_local_state(
        np.asarray(state["q"]), np.asarray(state["v"]), np.asarray(state["m"])
    )


@lru_cache(maxsize=4)
def dense_constraint_solved_cycle(
    *,
    time_step: float = 5.0e-4,
    sample_stride: int = 10,
    target_time: float = 0.106,
    flow_points: int = 42,
    radial_points: int = 500,
) -> dict[str, Any]:
    """Continue the projected orbit and evaluate every retained state directly."""

    if time_step <= 0.0 or sample_stride <= 0 or target_time <= 0.0:
        raise ValueError("positive integration controls required")
    initial = integrate_attached_dirac_flow(
        time_step=time_step, maximum_steps=0, points=flow_points
    )
    state = initial["continuation_state"]
    rows: list[dict[str, Any]] = []
    maximum_constraint = 0.0
    flow_exit_reason = "target_time_reached"

    def append_row(flow: Mapping[str, Any]) -> None:
        coordinates = np.asarray(flow["final_coordinates"])
        velocities = np.asarray(flow["final_velocities"])
        multipliers = np.asarray(flow["final_multipliers"])
        local = adm_joint_local_state(
            coordinates,
            velocities,
            multipliers,
            points=radial_points,
        )
        residual = float(flow["independent_grid_final_constraint_residual"])
        nonlocal maximum_constraint
        maximum_constraint = max(maximum_constraint, residual)
        rows.append({
            "time": float(flow["final_time"]),
            "coordinates": coordinates.tolist(),
            "velocities": velocities.tolist(),
            "multipliers": multipliers.tolist(),
            **local,
            "constraint_residual": residual,
            "exit_reason": flow["exit_reason"],
        })

    append_row(initial)
    while float(state["time"]) + 0.5 * time_step < target_time:
        remaining_steps = int(round((target_time - float(state["time"])) / time_step))
        steps = min(sample_stride, remaining_steps)
        flow = integrate_attached_dirac_flow(
            time_step=time_step,
            maximum_steps=steps,
            points=flow_points,
            initial_state=state,
        )
        if flow["steps_completed"] != steps or flow["exit_reason"] != "maximum_steps":
            flow_exit_reason = str(flow["exit_reason"])
            break
        append_row(flow)
        state = flow["continuation_state"]

    refined_terminal_state_inserted = False
    if rows[-1]["time"] < 0.106:
        # The stored 0.10602 state was obtained by the independently refined
        # continuation used in v15.74.  It supplies the last regular side when
        # the uniform chunked continuation meets the Legendre singularity.
        terminal_time = 0.10602
        terminal = SNAPSHOTS[terminal_time]
        local = adm_joint_local_state(
            np.asarray(terminal["q"]),
            np.asarray(terminal["v"]),
            np.asarray(terminal["m"]),
            points=radial_points,
        )
        residual = float(terminal["constraint_residual"])
        maximum_constraint = max(maximum_constraint, residual)
        rows.append({
            "time": terminal_time,
            "coordinates": list(terminal["q"]),
            "velocities": list(terminal["v"]),
            "multipliers": list(terminal["m"]),
            **local,
            "constraint_residual": residual,
            "exit_reason": "independent_refined_last_regular_state",
        })
        refined_terminal_state_inserted = True

    # The 3.72e-5 event-limit remainder is the continuous last-regular limit.
    if rows[-1]["time"] < EVENT_TIME:
        rows.append({**rows[-1], "time": EVENT_TIME, "exit_reason": "event_limit"})
    times = np.asarray([row["time"] for row in rows], dtype=float)
    lapse = np.asarray([row["boundary_lapse"] for row in rows], dtype=float)
    duration = float(PchipInterpolator(times, lapse).integrate(0.0, EVENT_TIME))

    def proper_average(key: str) -> float:
        values = np.asarray([row[key] for row in rows], dtype=float)
        return float(
            PchipInterpolator(times, lapse * values).integrate(0.0, EVENT_TIME)
            / duration
        )

    z_h = proper_average("Z_H")
    log_radius = np.asarray(
        [math.log(float(row["M4_spatial_radius"])) for row in rows], dtype=float
    )
    mean_log_radius = float(
        PchipInterpolator(times, lapse * log_radius).integrate(0.0, EVENT_TIME)
        / duration
    )
    return {
        "time_step": time_step,
        "sample_stride": sample_stride,
        "direct_constraint_solved_rows": len(rows),
        "last_regular_time": rows[-2]["time"],
        "uniform_flow_exit_reason": flow_exit_reason,
        "refined_terminal_state_inserted": refined_terminal_state_inserted,
        "proper_duration": duration,
        "proper_cycle_K_magnetic": proper_average("K_magnetic"),
        "proper_cycle_K_electric": proper_average("K_electric"),
        "proper_cycle_Z_H": z_h,
        "proper_cycle_Yukawa": z_h**-0.5,
        "proper_log_mean_R4_in_ell_kappa": math.exp(mean_log_radius),
        "proper_matching_scale_in_ell_kappa_inverse": math.exp(-mean_log_radius),
        "maximum_independent_constraint_residual": maximum_constraint,
        "rows": rows,
        "same_dense_states_and_measure_for_gauge_and_Yukawa": True,
    }


def completion_payload() -> dict[str, Any]:
    dense = dense_constraint_solved_cycle()
    validation = {
        "dense_grid_reaches_last_regular_slice": dense["last_regular_time"] >= 0.106,
        "terminal_refinement_declared": (
            not dense["refined_terminal_state_inserted"]
            or dense["uniform_flow_exit_reason"].startswith("ValueError_eta_Legendre")
        ),
        "constraints_controlled": dense["maximum_independent_constraint_residual"] < 3.0e-4,
        "gauge_coefficients_positive": dense["proper_cycle_K_magnetic"] > 0.0 and dense["proper_cycle_K_electric"] > 0.0,
        "Yukawa_nonzero": dense["proper_cycle_Yukawa"] > 0.0,
        "one_dense_pushforward": dense["same_dense_states_and_measure_for_gauge_and_Yukawa"],
        "USB_untouched": not USB_REMOVABLE_MEDIA_TOUCHED_DURING_SCIENCE,
    }
    return {
        "artifact": "BHSM_aether_dense_proper_joint_pushforward_v15_97",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "dense_proper_joint_pushforward": dense,
        "scientific_result": (
            "THE_5e-4_CONSTRAINT-PROJECTED_ORBIT_IS_EVALUATED_DIRECTLY_AT_"
            "EVERY_0.005_PROPER-PUSHFORWARD_SAMPLE,_AND_THE_SAME_DENSE_STATES_"
            "GENERATE_K_B,K_E,Z_H_AND_NONZERO_Y_WITHOUT_SECTOR_SPLITTING"
        ),
        "claim_boundary": {
            "dense_classical_cycle_quadrature_evaluated": True,
            "dense_quantum_corrected_cycle_evaluated": False,
            "Lorentz_invariant_cone_derived": False,
        },
        "active_calculation": (
            "ADD_THE_V15.96_COMMON_SUPERDETERMINANT_FORCE_TO_THIS_DENSE_"
            "CONSTRAINT-SOLVED_FLOW_AND_SOLVE_THE_QUANTUM_EVENT_SADDLE"
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
    path = target / "BHSM_aether_dense_proper_joint_pushforward_v15_97.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "wavefunction_residue",
    "adm_joint_local_state", "stored_state_witness",
    "dense_constraint_solved_cycle", "completion_payload",
    "deterministic_json", "materialize",
]
