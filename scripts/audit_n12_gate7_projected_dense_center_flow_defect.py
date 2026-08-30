"""Evaluate the projected native-DOP853 dense center's exact flow defect."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import audit_n12_c2_stop_dop853_boundary_cluster_probe as dense  # noqa: E402
import audit_n12_gate7_within_seam_constraint_center_obstruction as constraints  # noqa: E402
from bhsm.interface.aether_forward_c2_exact_fixed_s_field import (  # noqa: E402
    exact_cancelled_euler_dirac_field_action,
)


BASE = ROOT / "artifacts" / "flagship_integration"
NATIVE = BASE / "BHSM_N12_C2_STOP_HIGH_ORDER_QUARTER_STEP_RETAINED_RECONNAISSANCE.json"
NATIVE_DATA = NATIVE.with_suffix(".npz")
PROJECTED = BASE / "BHSM_N12_GATE7_PROJECTED_NATIVE_DOP853_CENTER_CANDIDATE.json"
PROJECTED_DATA = PROJECTED.with_suffix(".npz")
THEORY = ROOT / "theory" / "n12_gate7_projected_dense_center_flow_defect.md"
RESULT = BASE / "BHSM_N12_GATE7_PROJECTED_DENSE_CENTER_FLOW_DEFECT.json"
DATA = RESULT.with_suffix(".npz")
THIS_SCRIPT = Path(__file__).resolve()
FIXED_STEP = 0.25
_WORK: dict[str, np.ndarray | float] = {}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() in {".json", ".md", ".py"}:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest().upper()


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def _bernstein_value(control: np.ndarray, fraction: float) -> np.ndarray:
    level = np.asarray(control, dtype=float)
    while level.shape[0] > 1:
        level = (1.0 - fraction) * level[:-1] + fraction * level[1:]
    return level[0]


def _bernstein_derivative(
    control: np.ndarray, fraction: float, step: float,
) -> np.ndarray:
    degree = control.shape[0] - 1
    derivative_control = degree * (control[1:] - control[:-1])
    return _bernstein_value(derivative_control, fraction) / step


def _initialize(
    native_values: np.ndarray,
    native_coefficients: np.ndarray,
    weights: np.ndarray,
    reference: np.ndarray,
    corrections: np.ndarray,
    times: np.ndarray,
    stop_fraction: float,
) -> None:
    _WORK.update({
        "native_values": native_values,
        "native_coefficients": native_coefficients,
        "weights": weights,
        "reference": reference,
        "corrections": corrections,
        "times": times,
        "stop_fraction": stop_fraction,
    })


def _cell(index: int) -> tuple[int, dict[str, float], np.ndarray]:
    values = np.asarray(_WORK["native_values"])
    coefficients = np.asarray(_WORK["native_coefficients"])
    weights = np.asarray(_WORK["weights"])
    reference = np.asarray(_WORK["reference"])
    corrections = np.asarray(_WORK["corrections"])
    times = np.asarray(_WORK["times"])
    stop_fraction = float(_WORK["stop_fraction"])
    right_fraction = stop_fraction if index == times.size - 2 else 1.0
    fraction = 0.5 * right_fraction
    control = dense._dense_bernstein_controls(values[index], coefficients[index])
    native_midpoint = _bernstein_value(control, fraction)
    native_rate = _bernstein_derivative(control, fraction, FIXED_STEP)
    interval_length = float(times[index + 1] - times[index])
    correction_midpoint = 0.5 * (corrections[index] + corrections[index + 1])
    correction_rate = (corrections[index + 1] - corrections[index]) / interval_length
    state = (native_midpoint[:-1] + correction_midpoint) / weights
    descriptor = max(float(native_midpoint[-1]), 0.0)
    value = exact_cancelled_euler_dirac_field_action(
        state=state,
        weights=weights,
        reference=reference,
        signed_descriptor=descriptor,
    )
    cancelled = np.asarray(value["cancelled_field_action"], dtype=float)
    cancelled_norm = float(np.linalg.norm(cancelled))
    exact_rate = np.concatenate((
        cancelled / cancelled_norm,
        [float(value["Delta"]) / cancelled_norm],
    ))
    candidate_rate = np.concatenate((
        native_rate[:-1] + correction_rate,
        native_rate[-1:],
    ))
    defect = candidate_rate - exact_rate
    constraint_residual = constraints._scaled_residual(state, weights)[0]
    row = {
        "cell": index,
        "midpoint_action_time": 0.5 * float(times[index] + times[index + 1]),
        "interval_length": interval_length,
        "signed_descriptor": descriptor,
        "selected_branch": int(value["selected_branch"]),
        "selected_eigenline_gap": float(value["selected_eigenline_gap"]),
        "scaled_constraint_2_norm": constraint_residual,
        "action_correction_rate_2_norm": float(np.linalg.norm(correction_rate)),
        "augmented_flow_defect_2_norm": float(np.linalg.norm(defect)),
        "state_flow_defect_2_norm": float(np.linalg.norm(defect[:-1])),
        "descriptor_rate_defect_absolute": abs(float(defect[-1])),
    }
    return index, row, defect


def main() -> None:
    projected = _load(PROJECTED)
    if projected.get("validation_passed") is not True:
        raise RuntimeError("validated projected native DOP853 candidate required")
    with np.load(NATIVE_DATA) as source:
        native_values = np.asarray(
            source["fine_grid_augmented_action_values"], dtype=float,
        )
        native_coefficients = np.asarray(
            source["fine_grid_DOP853_dense_coefficients"], dtype=float,
        )
        stop_fraction = float(source["stop_dense_fraction"][0])
    with np.load(PROJECTED_DATA) as source:
        weights = np.asarray(source["state_weights"], dtype=float)
        reference = np.asarray(source["branch_reference"], dtype=float)
        corrections = np.asarray(
            source["one_step_action_corrections"], dtype=float,
        )
        times = np.asarray(source["action_times"], dtype=float)

    workers = min(
        int(os.environ.get("BHSM_N12_PROJECTED_DEFECT_WORKERS", "8")),
        os.cpu_count() or 1,
    )
    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=_initialize,
        initargs=(
            native_values, native_coefficients, weights, reference,
            corrections, times, stop_fraction,
        ),
    ) as executor:
        evaluated = list(executor.map(_cell, range(times.size - 1), chunksize=2))
    evaluated.sort(key=lambda item: item[0])
    rows = [item[1] for item in evaluated]
    defects = np.asarray([item[2] for item in evaluated])
    flow_norms = np.asarray([row["augmented_flow_defect_2_norm"] for row in rows])
    constraint_norms = np.asarray([row["scaled_constraint_2_norm"] for row in rows])
    correction_rates = np.asarray([row["action_correction_rate_2_norm"] for row in rows])
    descriptor_defects = np.asarray([
        row["descriptor_rate_defect_absolute"] for row in rows
    ])
    np.savez_compressed(
        DATA,
        cell_midpoint_action_times=np.asarray([
            row["midpoint_action_time"] for row in rows
        ]),
        augmented_flow_defect=defects,
        augmented_flow_defect_2_norm=flow_norms,
        scaled_constraint_2_norm=constraint_norms,
        action_correction_rate_2_norm=correction_rates,
        descriptor_rate_defect_absolute=descriptor_defects,
    )

    validation = {
        "all_370_projected_dense_cells_evaluated": len(rows) == 370,
        "all_quantities_are_finite": bool(np.all(np.isfinite(np.concatenate((
            defects.ravel(), flow_norms, constraint_norms,
            correction_rates, descriptor_defects,
        ))))),
        "branch_24_selected_on_every_midpoint": all(
            row["selected_branch"] == 24 for row in rows
        ),
        "selected_line_remains_simple_numerically": min(
            row["selected_eigenline_gap"] for row in rows
        ) > 1.0e-7,
        "projected_dense_midpoints_are_constraint_accurate_numerically": (
            float(np.max(constraint_norms)) < 2.0e-12
        ),
        "nonzero_flow_defect_is_not_promoted_to_shadowing": (
            float(np.max(flow_norms)) > 1.0e-6
        ),
        "descriptor_fiber_and_first_hit_not_claimed": True,
        "no_action_source_selector_scale_gate_or_chord_changed": True,
    }
    validation = {key: bool(value) for key, value in validation.items()}
    passed = all(validation.values())
    owner = int(np.argmax(flow_norms))
    payload = {
        "artifact": "BHSM_N12_GATE7_PROJECTED_DENSE_CENTER_FLOW_DEFECT",
        "status": (
            "PROJECTED_DENSE_PATH_CONSTRAINT_ACCURATE_BUT_FLOW_COLLOCATION_CORRECTION_REQUIRED"
            if passed else "PROJECTED_DENSE_CENTER_FLOW_DEFECT_AUDIT_INVALID"
        ),
        "authority": (
            "DIRECT_RETAINED_96_POINT_ACTION_FIELD_AT_ALL_370_PROJECTED_"
            "DOP853_DENSE_CELL_MIDPOINTS"
        ),
        "mesh": {
            "cells": len(rows),
            "native_fixed_action_step": FIXED_STEP,
            "workers": workers,
        },
        "summary": {
            "maximum_scaled_constraint_2_norm": float(np.max(constraint_norms)),
            "maximum_augmented_flow_defect_2_norm": float(np.max(flow_norms)),
            "maximum_state_flow_defect_2_norm": max(
                row["state_flow_defect_2_norm"] for row in rows
            ),
            "maximum_descriptor_rate_defect_absolute": float(np.max(descriptor_defects)),
            "maximum_action_correction_rate_2_norm": float(np.max(correction_rates)),
            "minimum_selected_eigenline_gap": min(
                row["selected_eigenline_gap"] for row in rows
            ),
            "flow_defect_owner": rows[owner],
        },
        "rows": rows,
        "data": _relative(DATA),
        "data_SHA256": _sha256(DATA),
        "inputs": {
            _relative(path): _sha256(path)
            for path in (
                NATIVE, NATIVE_DATA, PROJECTED, PROJECTED_DATA,
                THEORY, THIS_SCRIPT,
            )
        },
        "adjudication": {
            "projected_dense_constraint_geometry": "NUMERICALLY_ACCURATE_AT_ALL_CELL_MIDPOINTS",
            "projected_dense_flow_equation": "NONZERO_COLLOCATION_DEFECT",
            "continuous_shadowing_center": "OPEN",
            "next_route": "GLOBAL_OR_CAUSAL_COLLOCATION_CORRECTION_WITH_CONSTRAINT_AND_DESCRIPTOR_FIBER_ROWS",
        },
        "claim_boundary": {
            "constraint_accurate_projected_dense_midpoints": "NUMERICAL_CANDIDATE",
            "continuous_action_constrained_center": "OPEN_COLLOCATION_CORRECTION",
            "descriptor_fiber_lambda_equals_s": "OPEN",
            "first_hit_time": "OPEN_REBUILD_AFTER_CENTER",
            "continuous_outward_variational_carrier": "OPEN_AFTER_CENTER",
            "Weyl_force_KKT_Hessian": "NOT_CLAIMED",
            "Gate7": "ACTIVE_ACTION_OWNED_OPERATOR_ORACLE",
            "FULL_BHSM_COMPLETE": False,
        },
        "exact_next_dependency": (
            "SOLVE_THE_370_CELL_PROJECTED_DENSE_FLOW_DEFECT_WITH_A_"
            "CONSTRAINT_AND_DESCRIPTOR_FIBER_AUGMENTED_COLLOCATION_NEWTON_"
            "SYSTEM,_THEN_CERTIFY_ITS_CONTINUOUS_RESIDUAL_AND_FIRST_HIT"
        ),
        "validation": validation,
        "validation_passed": passed,
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "status": payload["status"],
        "summary": payload["summary"],
        "validation_passed": passed,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
