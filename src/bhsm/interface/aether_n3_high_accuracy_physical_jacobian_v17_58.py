"""Process-parallel physical Jacobian from the validated v17.57 covector."""
from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_fresh_sbp_first_descent_v16_59 import (
    ACTION_HESSIAN_RELATIVE_STEP, EVENT_CURVATURE_RELATIVE_STEP,
)
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_event_covector
from bhsm.interface.aether_n3_high_accuracy_action_covector_v17_57 import (
    high_accuracy_sbp_action_covector,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    event_gradient_indices, kkt_variable_scales,
)

VERSION = "v17.58"
CLASSIFICATION = "BHSM_N3_HIGH_ACCURACY_PROCESS_PARALLEL_PHYSICAL_JACOBIAN"
FULL_BHSM_COMPLETE = False


def _chunks(indices: tuple[int, ...], count: int) -> list[tuple[int, ...]]:
    return [tuple(indices[offset::count]) for offset in range(count) if indices[offset::count]]


def _action_columns(task: tuple[np.ndarray, tuple[int, ...]]) -> list[tuple[int, np.ndarray]]:
    raw, columns = task
    scales = kkt_variable_scales()
    ybase = raw[:-1] * scales[:-1]

    def gradient(value: np.ndarray) -> np.ndarray:
        return (
            np.asarray(high_accuracy_sbp_action_covector(value / scales[:-1])["covector"])
            / scales[:-1]
        )

    result = []
    for column in columns:
        step = ACTION_HESSIAN_RELATIVE_STEP * max(1.0, abs(float(ybase[column])))
        delta = np.zeros(375)
        delta[column] = step
        result.append((column, (gradient(ybase + delta) - gradient(ybase - delta)) / (2 * step)))
    return result


def _event_columns(task: tuple[np.ndarray, tuple[int, ...]]) -> list[tuple[int, np.ndarray]]:
    raw, columns = task
    scales = kkt_variable_scales()
    ybase = raw[:-1] * scales[:-1]

    def gradient(value: np.ndarray) -> np.ndarray:
        return sbp_event_covector(value / scales[:-1]) / scales[:-1] / scales[-1]

    result = []
    for column in columns:
        step = EVENT_CURVATURE_RELATIVE_STEP * max(1.0, abs(float(ybase[column])))
        delta = np.zeros(375)
        delta[column] = step
        result.append((column, (gradient(ybase + delta) - gradient(ybase - delta)) / (2 * step)))
    return result


def parallel_high_accuracy_sbp_physical_jacobian(
    raw: np.ndarray, *, workers: int | None = None,
) -> dict[str, Any]:
    raw = np.asarray(raw, dtype=float)
    if raw.shape != (376,):
        raise ValueError("raw KKT vector has wrong dimension")
    worker_count = max(1, int(workers or min(8, os.cpu_count() or 1)))
    scales = kkt_variable_scales()
    y = raw * scales
    action_hessian = np.empty((375, 375))
    tasks = [(raw, chunk) for chunk in _chunks(tuple(range(375)), worker_count)]
    with ProcessPoolExecutor(max_workers=worker_count) as executor:
        for values in executor.map(_action_columns, tasks):
            for column, vector in values:
                action_hessian[:, column] = vector
    action_asymmetry = float(
        np.linalg.norm(action_hessian - action_hessian.T)
        / max(1.0, np.linalg.norm(action_hessian))
    )
    action_hessian = 0.5 * (action_hessian + action_hessian.T)
    event_gradient = sbp_event_covector(raw[:-1]) / scales[:-1] / scales[-1]
    event_hessian = np.zeros((375, 375))
    tasks = [
        (raw, chunk) for chunk in _chunks(
            tuple(int(index) for index in event_gradient_indices()), worker_count
        )
    ]
    with ProcessPoolExecutor(max_workers=worker_count) as executor:
        for values in executor.map(_event_columns, tasks):
            for column, vector in values:
                event_hessian[:, column] = vector
    event_asymmetry = float(
        np.linalg.norm(event_hessian - event_hessian.T)
        / max(1.0, np.linalg.norm(event_hessian))
    )
    matrix = np.zeros((376, 376))
    matrix[:-1, :-1] = action_hessian + y[-1] * event_hessian
    matrix[:-1, -1] = event_gradient
    matrix[-1, :-1] = event_gradient
    return {
        "matrix": matrix,
        "assembly_workers": worker_count,
        "column_partition": "INDEPENDENT_CENTRAL_FINITE_DIFFERENCE_COLUMNS",
        "action_covector": "V17_57_HIGH_ACCURACY_SAME_ACTION",
        "action_hessian_norm": float(np.linalg.norm(action_hessian)),
        "action_hessian_raw_asymmetry": action_asymmetry,
        "event_hessian_norm": float(np.linalg.norm(event_hessian)),
        "event_hessian_raw_asymmetry": event_asymmetry,
        "event_curvature_contribution_norm": float(abs(y[-1]) * np.linalg.norm(event_hessian)),
    }


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "parallel_high_accuracy_sbp_physical_jacobian",
]
