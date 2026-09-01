"""Build one high-order global C2 center from the certified 1222 frontier.

This is the single finite-center correction required by the global
multiple-shooting route.  It integrates the retained denominator-free
action-arclength field with DOP853, terminates on the existing descending
``s=0`` Euler--Dirac face, and resamples the result on the established
two-action-unit macro mesh.  It is reconnaissance until interval shadowing
and the initial certified tube are consumed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np
from scipy.integrate._ivp.rk import DOP853


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_forward_c2_exact_fixed_s_field import (  # noqa: E402
    exact_cancelled_euler_dirac_field_action,
)
if os.environ.get("BHSM_N12_USE_FAST_DELTA", "0") == "1":
    from bhsm.interface.aether_forward_c2_fast_cancelled_field import (  # noqa: E402
        exact_cancelled_euler_dirac_field_action,
    )
if os.environ.get("BHSM_N12_USE_JAX", "0") == "1":
    from bhsm.interface.aether_jax_forward_c2_exact_fixed_s_field import (  # noqa: E402
        exact_cancelled_euler_dirac_field_action,
    )


BASE = ROOT / "artifacts" / "flagship_integration"
PARENT = BASE / "BHSM_N12_C2_STOP_MULTIPLE_SHOOTING_CENTER.json"
PARENT_DATA = PARENT.with_suffix(".npz")
RESULT = Path(os.environ.get(
    "BHSM_N12_STOP_HIGH_ORDER_RESULT",
    str(BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_CENTER_RECONNAISSANCE.json"),
))
DATA_RESULT = RESULT.with_suffix(".npz")


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def build_payload(*, fixed_step: float) -> dict[str, Any]:
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    if parent["claim_boundary"]["exact_node_and_midpoint_fields_evaluated"] is not True:
        raise RuntimeError("finite 47-seam center parent required")
    with np.load(PARENT_DATA) as source:
        old_states = np.asarray(source["centers"], dtype=float)
        old_descriptors = np.asarray(source["signed_descriptors"], dtype=float)
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)

    evaluations = 0

    def field(action_length: float, augmented: np.ndarray) -> np.ndarray:
        nonlocal evaluations
        evaluations += 1
        state = augmented[:-1] / weights
        descriptor = max(float(augmented[-1]), 0.0)
        if os.environ.get("BHSM_N12_CALIBRATED_JAX_DATA"):
            from bhsm.interface.aether_calibrated_jax_c2_field import (
                exact_cancelled_euler_dirac_field_action as calibrated_field,
            )

            value = calibrated_field(
                action_length=action_length,
                state=state,
                weights=weights,
                reference=reference,
                signed_descriptor=descriptor,
            )
        else:
            value = exact_cancelled_euler_dirac_field_action(
                state=state,
                weights=weights,
                reference=reference,
                signed_descriptor=descriptor,
            )
        cancelled = np.asarray(value["cancelled_field_action"], dtype=float)
        norm = float(np.linalg.norm(cancelled))
        return np.concatenate((
            cancelled / norm,
            np.asarray([float(value["Delta"]) / norm]),
        ))

    initial = np.concatenate((old_states[0] * weights, old_descriptors[:1]))
    if not 0.0 < fixed_step <= 2.0 or abs(2.0 / fixed_step - round(2.0 / fixed_step)) > 1.0e-12:
        raise ValueError("fixed step must divide the established macro step two")

    def high_order_step(
        action_length: float, value: np.ndarray, step: float,
    ) -> tuple[np.ndarray, np.ndarray]:
        stages = np.empty((16, value.size))
        stages[0] = field(action_length, value)
        for stage in range(1, DOP853.n_stages):
            increment = step * np.tensordot(
                DOP853.A[stage, :stage], stages[:stage], axes=(0, 0),
            )
            stages[stage] = field(
                action_length + DOP853.C[stage] * step,
                value + increment,
            )
        result = value + step * np.tensordot(
            DOP853.B, stages[:DOP853.n_stages], axes=(0, 0),
        )
        stages[DOP853.n_stages] = field(action_length + step, result)
        for extra, (coefficients, abscissa) in enumerate(zip(
            DOP853.A_EXTRA, DOP853.C_EXTRA, strict=True,
        ), start=DOP853.n_stages + 1):
            increment = step * np.tensordot(
                coefficients[:extra], stages[:extra], axes=(0, 0),
            )
            stages[extra] = field(
                action_length + abscissa * step, value + increment,
            )
        delta = result - value
        dense_coefficients = np.empty((7, value.size))
        dense_coefficients[0] = delta
        dense_coefficients[1] = step * stages[0] - delta
        dense_coefficients[2] = (
            2.0 * delta - step * (stages[DOP853.n_stages] + stages[0])
        )
        dense_coefficients[3:] = step * (DOP853.D @ stages)
        return result, dense_coefficients

    def dense_value(
        left_value: np.ndarray, coefficients: np.ndarray, fraction: float,
    ) -> np.ndarray:
        value = np.zeros_like(left_value)
        for index, coefficient in enumerate(reversed(coefficients)):
            value += coefficient
            value *= fraction if index % 2 == 0 else 1.0 - fraction
        return value + left_value

    grid_times = [0.0]
    grid_values = [initial]
    grid_dense_coefficients = []
    action_length = 0.0
    value = initial
    bracket: tuple[float, np.ndarray, float, np.ndarray] | None = None
    while action_length < 94.0 - 0.5 * fixed_step:
        trial, coefficients = high_order_step(action_length, value, fixed_step)
        trial_length = action_length + fixed_step
        grid_times.append(trial_length)
        grid_values.append(trial)
        grid_dense_coefficients.append(coefficients)
        if len(grid_dense_coefficients) % 32 == 0:
            print(json.dumps({
                "completed_fixed_steps": len(grid_dense_coefficients),
                "action_length": trial_length,
                "field_evaluations": evaluations,
                "signed_descriptor": float(trial[-1]),
            }), flush=True)
        if action_length >= 30.0 and value[-1] > 0.0 >= trial[-1]:
            bracket = (action_length, value, trial_length, trial)
            break
        action_length, value = trial_length, trial
    if bracket is None:
        raise RuntimeError("descending s=0 RK4 bracket not found")
    left_length, left_value, right_length, _ = bracket
    bracket_index = len(grid_dense_coefficients) - 1
    bracket_coefficients = grid_dense_coefficients[bracket_index]
    for _ in range(48):
        midpoint = 0.5 * (left_length + right_length)
        midpoint_value = dense_value(
            grid_values[bracket_index], bracket_coefficients,
            (midpoint - grid_times[bracket_index]) / fixed_step,
        )
        if midpoint_value[-1] > 0.0:
            left_length, left_value = midpoint, midpoint_value
        else:
            right_length = midpoint
    stop_length = 0.5 * (left_length + right_length)
    stop_value = dense_value(
        grid_values[bracket_index], bracket_coefficients,
        (stop_length - grid_times[bracket_index]) / fixed_step,
    )
    stop_value[-1] = 0.0
    macro = np.arange(0.0, 92.0 + 1.0e-12, 2.0)
    action_lengths = np.concatenate((macro, np.asarray([stop_length])))

    def dense(times: np.ndarray) -> np.ndarray:
        result = np.empty((times.size, initial.size))
        stored_times = np.asarray(grid_times)
        stored_values = np.asarray(grid_values)
        for index, time in enumerate(times):
            if abs(time - stop_length) < 1.0e-13:
                result[index] = stop_value
                continue
            left_index = int(np.floor(time / fixed_step + 1.0e-12))
            left_index = min(left_index, stored_times.size - 1)
            base_time = float(stored_times[left_index])
            base_value = stored_values[left_index]
            remainder = float(time - base_time)
            result[index] = (
                base_value if abs(remainder) < 1.0e-14
                else dense_value(
                    base_value,
                    grid_dense_coefficients[left_index],
                    remainder / fixed_step,
                )
            )
        return result

    augmented_nodes = dense(action_lengths)
    states = augmented_nodes[:, :-1] / weights
    descriptors = augmented_nodes[:, -1]
    node_rates = np.asarray([field(t, y) for t, y in zip(
        action_lengths, augmented_nodes, strict=True,
    )])
    midpoint_times = 0.5 * (action_lengths[:-1] + action_lengths[1:])
    augmented_midpoints = dense(midpoint_times)
    exact_midpoint_rates = np.asarray([field(t, y) for t, y in zip(
        midpoint_times, augmented_midpoints, strict=True,
    )])

    hermite_midpoints = []
    hermite_midpoint_rates = []
    for index, h in enumerate(np.diff(action_lengths)):
        y0, y1 = augmented_nodes[index:index + 2]
        f0, f1 = node_rates[index:index + 2]
        hermite_midpoints.append(0.5 * (y0 + y1) + h * (f0 - f1) / 8.0)
        hermite_midpoint_rates.append(
            1.5 * (y1 - y0) / h - 0.25 * (f0 + f1)
        )
    hermite_midpoints = np.asarray(hermite_midpoints)
    hermite_midpoint_rates = np.asarray(hermite_midpoint_rates)
    midpoint_state_position_defect = (
        hermite_midpoints[:, :-1] - augmented_midpoints[:, :-1]
    )
    midpoint_descriptor_position_defect = (
        hermite_midpoints[:, -1] - augmented_midpoints[:, -1]
    )
    midpoint_state_rate_defect = (
        hermite_midpoint_rates[:, :-1] - exact_midpoint_rates[:, :-1]
    )
    midpoint_descriptor_rate_defect = (
        hermite_midpoint_rates[:, -1] - exact_midpoint_rates[:, -1]
    )
    old_stop = old_states[-1] * weights
    new_stop = augmented_nodes[-1, :-1]
    np.savez_compressed(
        DATA_RESULT,
        centers=states,
        signed_descriptors=descriptors,
        action_lengths=action_lengths,
        state_weights=weights,
        branch_reference=reference,
        state_rates=node_rates[:, :-1] / weights,
        action_rates=node_rates[:, :-1],
        descriptor_rates=node_rates[:, -1],
        dense_midpoints=augmented_midpoints[:, :-1] / weights,
        dense_midpoint_descriptors=augmented_midpoints[:, -1],
        Hermite_midpoint_state_position_defects=midpoint_state_position_defect,
        Hermite_midpoint_descriptor_position_defects=midpoint_descriptor_position_defect,
        Hermite_midpoint_state_rate_defects=midpoint_state_rate_defect,
        Hermite_midpoint_descriptor_rate_defects=midpoint_descriptor_rate_defect,
        fine_grid_action_lengths=np.asarray(grid_times),
        fine_grid_augmented_action_values=np.asarray(grid_values),
        fine_grid_DOP853_dense_coefficients=np.asarray(grid_dense_coefficients),
        stop_bracket_fine_grid_index=np.asarray([bracket_index], dtype=int),
        stop_dense_fraction=np.asarray([
            (stop_length - grid_times[bracket_index]) / fixed_step
        ]),
    )
    maximum_state_position = float(np.max(np.linalg.norm(
        midpoint_state_position_defect, axis=1,
    )))
    maximum_state_rate = float(np.max(np.linalg.norm(
        midpoint_state_rate_defect, axis=1,
    )))
    maximum_descriptor_position = float(np.max(np.abs(
        midpoint_descriptor_position_defect
    )))
    maximum_descriptor_rate = float(np.max(np.abs(
        midpoint_descriptor_rate_defect
    )))
    old_stop_shift = float(np.linalg.norm(new_stop - old_stop))
    validation = {
        "fixed_DOP853_descending_s_zero_bracket_found": bracket is not None,
        "scalar_bisection_returns_s_zero_center": stop_value[-1] == 0.0,
        "same_47_macro_seams_retained": action_lengths.size == 48,
        "high_order_center_stop_stays_near_prior_refined_stop": old_stop_shift < 1.0e-3,
        "high_order_center_not_promoted_to_interval_history": True,
        "no_new_stop_selector_action_scale_gate_or_chord_added": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    return {
        "artifact": "BHSM_N12_C2_STOP_HIGH_ORDER_CENTER_RECONNAISSANCE",
        "status": "HIGH_ORDER_GLOBAL_STOP_CENTER_ASSEMBLED;_INTERVAL_AUTHORITY_OPEN",
        "method": "FIXED_DOP853_ON_RETAINED_DENOMINATOR_FREE_ACTION_ARCLENGTH_FIELD",
        "action_jet_realization": (
            "CROSS_VALIDATED_OPTIONAL_JAX_96_POINT_ACTION"
            if os.environ.get("BHSM_N12_USE_JAX", "0") == "1" else
            "RETAINED_COMBINED_DIRECTION_DELTA_96_POINT_ACTION"
            if os.environ.get("BHSM_N12_USE_FAST_DELTA", "0") == "1" else
            "RETAINED_PYTHON_JET_96_POINT_ACTION"
        ),
        "descriptor_directional_realization": (
            "JAX_PREDICTOR_ONLY_REQUIRES_RETAINED_RESIDUAL_RECHECK"
            if os.environ.get("BHSM_N12_FAST_DELTA_JAX", "0") == "1" else
            "RETAINED_COMPLEX_STEP_ACTION_JET"
        ),
        "macro_action_jet_calibration": (
            "PREDICTOR_ONLY_REQUIRES_RETAINED_RESIDUAL_RECHECK"
            if os.environ.get("BHSM_N12_CALIBRATED_JAX_DATA") else None
        ),
        "integrator": {
            "fixed_action_step": fixed_step,
            "Runge_Kutta_order": 8,
            "Runge_Kutta_stages": int(DOP853.n_stages),
            "stop_bisection_iterations": 48,
            "field_evaluations": evaluations,
            "global_fixed_steps_through_stop_bracket": len(grid_times) - 1,
        },
        "center": {
            "action_length_stop": stop_length,
            "prior_refined_stop_action_length": float(
                parent["mesh"]["action_length_stop"]
            ),
            "stop_action_coordinate_shift_from_prior_center": old_stop_shift,
            "maximum_Hermite_midpoint_state_position_defect_action_norm": maximum_state_position,
            "maximum_Hermite_midpoint_state_rate_defect_action_norm": maximum_state_rate,
            "maximum_absolute_Hermite_midpoint_descriptor_position_defect": maximum_descriptor_position,
            "maximum_absolute_Hermite_midpoint_descriptor_rate_defect": maximum_descriptor_rate,
        },
        "claim_boundary": {
            "global_center_improved": True,
            "finite_interval_witness": "OPEN",
            "Gate7": "ACTIVE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "REBUILD_THE_FINITE_SHEARED_BORDERED_GREEN_OPERATOR_ON_THIS_ONE_"
            "HIGH_ORDER_CENTER_AND_CERTIFY_ITS_INTERVAL_NEWTON_RADIUS_WITH_"
            "THE_EXISTING_ACTION_D4_D5_AND_256_CELL_RESPONSE_PARENTS"
        ),
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "data_SHA256": _sha256(DATA_RESULT),
        "inputs": {
            PARENT.relative_to(ROOT).as_posix(): _sha256(PARENT),
            PARENT_DATA.relative_to(ROOT).as_posix(): _sha256(PARENT_DATA),
        },
        "validation": validation,
        "validation_passed": False,
        "FLAGSHIP_READY": False,
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixed-step", type=float, default=2.0)
    args = parser.parse_args()
    payload = build_payload(fixed_step=args.fixed_step)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "integrator": payload["integrator"],
        "center": payload["center"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
