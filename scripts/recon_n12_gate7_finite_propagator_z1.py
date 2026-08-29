"""Reconnoiter the finite common-frame Gate-7 propagator defect.

This calculation composes midpoint exponential propagators on the selected
quarter-step history.  It compares 4, 8, 16, and 32 substeps on every
retained macro seam, both locally and after causal accumulation.  The result
is numerical convergence evidence only; interval remainder authority is a
separate certification step.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.linalg import expm


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "flagship_integration"
CENTER = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.npz"
JACOBIAN = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_GRAPH_JACOBIAN_RECONNAISSANCE.npz"
TANGENT = BASE / "BHSM_N12_C2_STOP_QUARTER_STEP_PHYSICAL_TANGENT_TRANSFER_RECONNAISSANCE.npz"
RESULT = BASE / "BHSM_N12_GATE7_FINITE_PROPAGATOR_Z1_RECONNAISSANCE.json"
DATA_RESULT = RESULT.with_suffix(".npz")
RESOLUTIONS = (4, 8, 16, 32)


def _linear_interpolant(
    time: float, times: np.ndarray, values: np.ndarray,
) -> np.ndarray:
    index = min(
        max(int(np.searchsorted(times, time, side="right") - 1), 0),
        times.size - 2,
    )
    left = float(times[index])
    right = float(times[index + 1])
    fraction = min(max((time - left) / (right - left), 0.0), 1.0)
    return (1.0 - fraction) * values[index] + fraction * values[index + 1]


def _midpoint_step(
    value: np.ndarray,
    left: float,
    step: float,
    times: np.ndarray,
    jacobians: np.ndarray,
) -> np.ndarray:
    midpoint = left + 0.5 * step
    generator = _linear_interpolant(midpoint, times, jacobians)
    return expm(step * generator) @ value


def _step_maps(
    resolution: int,
    macro_times: np.ndarray,
    jacobian_times: np.ndarray,
    jacobians: np.ndarray,
    tangents: np.ndarray,
) -> np.ndarray:
    maps = []
    for seam, (left, right) in enumerate(zip(macro_times[:-1], macro_times[1:])):
        duration = float(right - left)
        step = duration / resolution
        value = tangents[seam]
        for substep in range(resolution):
            value = _midpoint_step(
                value, float(left + substep * step), step,
                jacobian_times, jacobians,
            )
        maps.append(tangents[seam + 1].T @ value)
    return np.asarray(maps)


def _fundamental_profile(step_maps: np.ndarray) -> np.ndarray:
    dimension = step_maps.shape[1]
    values = [np.eye(dimension)]
    current = values[0]
    for step_map in step_maps:
        current = step_map @ current
        values.append(current)
    return np.asarray(values)


def _difference_rows(
    coarse: np.ndarray, fine: np.ndarray, label: str,
) -> list[dict[str, float | int | str]]:
    rows = []
    for index, (left, right) in enumerate(zip(coarse, fine)):
        absolute = float(np.linalg.norm(right - left, 2))
        scale = max(float(np.linalg.norm(right, 2)), np.finfo(float).tiny)
        rows.append({
            "index": index,
            "comparison": label,
            "absolute_defect_2_norm": absolute,
            "relative_defect_2_norm": absolute / scale,
        })
    return rows


def main() -> None:
    with np.load(CENTER) as source:
        macro_times = np.asarray(source["action_lengths"], dtype=float)
    with np.load(JACOBIAN) as source:
        jacobians = np.asarray(source["graph_Jacobian_action"], dtype=float)
        if "action_lengths" in source.files:
            jacobian_times = np.asarray(source["action_lengths"], dtype=float)
        else:
            jacobian_times = macro_times
    with np.load(TANGENT) as source:
        tangents = np.asarray(source["physical_tangent_action"], dtype=float)

    maps = {
        resolution: _step_maps(
            resolution, macro_times, jacobian_times, jacobians, tangents,
        )
        for resolution in RESOLUTIONS
    }
    fundamentals = {
        resolution: _fundamental_profile(maps[resolution])
        for resolution in RESOLUTIONS
    }
    local_4_8 = _difference_rows(maps[4], maps[8], "4_TO_8")
    local_8_16 = _difference_rows(maps[8], maps[16], "8_TO_16")
    local_16_32 = _difference_rows(maps[16], maps[32], "16_TO_32")
    accumulated_4_8 = _difference_rows(
        fundamentals[4], fundamentals[8], "4_TO_8",
    )
    accumulated_8_16 = _difference_rows(
        fundamentals[8], fundamentals[16], "8_TO_16",
    )
    accumulated_16_32 = _difference_rows(
        fundamentals[16], fundamentals[32], "16_TO_32",
    )

    def maximum(rows: list[dict[str, float | int | str]]) -> dict[str, object]:
        return max(rows, key=lambda row: float(row["relative_defect_2_norm"]))

    local_coarse = maximum(local_4_8)
    local_fine = maximum(local_8_16)
    accumulated_coarse = maximum(accumulated_4_8)
    accumulated_fine = maximum(accumulated_8_16)
    local_finest = maximum(local_16_32)
    accumulated_finest = maximum(accumulated_16_32)
    local_relative_sum_4_8 = sum(
        float(row["relative_defect_2_norm"]) for row in local_4_8
    )
    local_relative_sum_8_16 = sum(
        float(row["relative_defect_2_norm"]) for row in local_8_16
    )
    local_relative_sum_16_32 = sum(
        float(row["relative_defect_2_norm"]) for row in local_16_32
    )
    local_order = np.log2(
        float(local_coarse["relative_defect_2_norm"])
        / float(local_fine["relative_defect_2_norm"]),
    )
    accumulated_order = np.log2(
        float(accumulated_coarse["relative_defect_2_norm"])
        / float(accumulated_fine["relative_defect_2_norm"]),
    )
    summed_local_order = np.log2(
        local_relative_sum_4_8 / local_relative_sum_8_16
    )
    finest_summed_local_order = np.log2(
        local_relative_sum_8_16 / local_relative_sum_16_32
    )
    # A factor-four refinement makes the unresolved second-order geometric
    # tail one third of the last difference.  This remains a convergence
    # estimate until a finite interval remainder proves the same ratio.
    handoff_factor_four_tail_estimate = (
        (4.0 / 3.0) * local_relative_sum_8_16
    )
    factor_four_geometric_tail_estimate = (
        (4.0 / 3.0) * local_relative_sum_16_32
    )
    np.savez_compressed(
        DATA_RESULT,
        macro_action_lengths=macro_times,
        step_maps_4=maps[4],
        step_maps_8=maps[8],
        step_maps_16=maps[16],
        step_maps_32=maps[32],
        fundamental_4=fundamentals[4],
        fundamental_8=fundamentals[8],
        fundamental_16=fundamentals[16],
        fundamental_32=fundamentals[32],
    )
    payload = {
        "artifact": "BHSM_N12_GATE7_FINITE_PROPAGATOR_Z1_RECONNAISSANCE",
        "authority": "NUMERICAL_COMMON_FRAME_CONVERGENCE_NOT_INTERVAL_AUTHORITY",
        "identity": {
            "propagator": "MIDPOINT_EXPONENTIAL_PRODUCT",
            "generator": "PIECEWISE_LINEAR_SELECTED_QUARTER_GRAPH_JACOBIAN",
            "common_frame": "73_DIMENSIONAL_RETAINED_CONSTRAINT_TANGENT",
            "Z1": "NORM_I_MINUS_A_L_IN_THE_SAME_COMMON_FRAME",
        },
        "summary": {
            "resolutions": list(RESOLUTIONS),
            "maximum_local_relative_defect_4_to_8": local_coarse,
            "maximum_local_relative_defect_8_to_16": local_fine,
            "observed_local_order": local_order,
            "maximum_accumulated_relative_defect_4_to_8": accumulated_coarse,
            "maximum_accumulated_relative_defect_8_to_16": accumulated_fine,
            "maximum_local_relative_defect_16_to_32": local_finest,
            "maximum_accumulated_relative_defect_16_to_32": accumulated_finest,
            "observed_accumulated_order": accumulated_order,
            "summed_local_relative_defect_4_to_8": local_relative_sum_4_8,
            "summed_local_relative_defect_8_to_16": local_relative_sum_8_16,
            "summed_local_relative_defect_16_to_32": local_relative_sum_16_32,
            "observed_summed_local_order": summed_local_order,
            "observed_finest_summed_local_order": finest_summed_local_order,
            "handoff_factor_four_geometric_tail_estimate_from_8_to_16": (
                handoff_factor_four_tail_estimate
            ),
            "factor_four_geometric_tail_estimate": (
                factor_four_geometric_tail_estimate
            ),
        },
        "data": DATA_RESULT.relative_to(ROOT).as_posix(),
        "status": "FINITE_PROPAGATOR_CONVERGENCE_MEASURED;_INTERVAL_Z1_OPEN",
        "validation": {
            "same_48_node_selected_quarter_history": macro_times.shape == (48,),
            "same_73_dimensional_common_frames": tangents.shape == (48, 98, 73),
            "successive_local_defect_decreases": (
                float(local_fine["relative_defect_2_norm"])
                < float(local_coarse["relative_defect_2_norm"])
                and float(local_finest["relative_defect_2_norm"])
                < float(local_fine["relative_defect_2_norm"])
            ),
            "successive_accumulated_defect_decreases": (
                float(accumulated_fine["relative_defect_2_norm"])
                < float(accumulated_coarse["relative_defect_2_norm"])
                and float(accumulated_finest["relative_defect_2_norm"])
                < float(accumulated_fine["relative_defect_2_norm"])
            ),
            "not_promoted_to_interval_authority": True,
            "no_action_equation_source_selector_scale_gate_or_chord_changed": True,
        },
        "validation_passed": False,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
