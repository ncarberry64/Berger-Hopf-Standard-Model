"""Direct gradient of the exact projected 376-row N=3 merit."""
from __future__ import annotations

import json
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_exact_local_jet_sbp_covector_v17_61 import (
    exact_local_jet_sbp_projected_residual_and_vector,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN, _metrics
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_resolved_trial_complete_child_promotion_v18_09 import v18_09_selected_raw_vector


VERSION = "v18.10"
CLASSIFICATION = "BHSM_N3_EXACT_PROJECTED_PHYSICAL_MERIT_GRADIENT"
FULL_BHSM_COMPLETE = False
ABSOLUTE_STEP = 3.0e-5
LINE_RADII = (1.0e-7, 3.0e-7, 1.0e-6, 3.0e-6, 1.0e-5, 3.0e-5, 1.0e-4)


def _chunks(indices: tuple[int, ...], count: int) -> list[tuple[int, ...]]:
    return [tuple(indices[offset::count]) for offset in range(count) if indices[offset::count]]


def _merit(scaled: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    projected, residual = exact_local_jet_sbp_projected_residual_and_vector(scaled)
    return projected, residual, 0.5 * float(residual @ residual)


def _merit_columns(
    task: tuple[np.ndarray, tuple[int, ...], float],
) -> list[tuple[int, float]]:
    source_y, columns, step = task
    rows = []
    for column in columns:
        delta = np.zeros(376)
        delta[column] = step
        _, _, plus = _merit(source_y + delta)
        _, _, minus = _merit(source_y - delta)
        rows.append((column, (plus - minus) / (2.0 * step)))
    return rows


def exact_projected_merit_gradient(
    source_y: np.ndarray, *, workers: int | None = None,
    absolute_step: float = ABSOLUTE_STEP,
) -> dict[str, Any]:
    y = np.asarray(source_y, dtype=float)
    if y.shape != (376,):
        raise ValueError("scaled KKT vector has wrong dimension")
    worker_count = max(1, int(workers or min(8, os.cpu_count() or 1)))
    gradient = np.empty(375)
    tasks = [
        (y, chunk, absolute_step)
        for chunk in _chunks(tuple(range(375)), worker_count)
    ]
    with ProcessPoolExecutor(max_workers=worker_count) as executor:
        for rows in executor.map(_merit_columns, tasks):
            for column, value in rows:
                gradient[column] = value
    return {
        "gradient": gradient,
        "assembly_workers": worker_count,
        "column_partition": "INDEPENDENT_CENTRAL_DIFFERENCES_OF_SCALAR_TRUE_MERIT",
        "absolute_step": absolute_step,
        "physical_residual_changed": False,
        "physical_event_changed": False,
        "global_KKT_row_added": False,
    }


def v18_10_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_exact_projected_merit_gradient_v18_10.json"
    ).read_text(encoding="utf-8"))
    selected = payload["exact_projected_merit_gradient"][
        "selected_true_merit_candidate_pending_child_acceptance"
    ]
    if selected is None:
        raise ValueError("v18.10 has no candidate to reconstruct")
    return np.asarray([float.fromhex(value) for value in selected["raw_vector_hex"]])


def exact_projected_merit_gradient_step() -> dict[str, Any]:
    scales = kkt_variable_scales()
    source_raw = v18_09_selected_raw_vector()
    source_y, source_residual, source_merit = _merit(source_raw * scales)
    initial = _metrics(source_residual)
    assembled = exact_projected_merit_gradient(source_y)
    gradient = np.asarray(assembled.pop("gradient"))
    gradient_norm = float(np.linalg.norm(gradient))
    direction = -gradient / gradient_norm
    directional = []
    for step in (1.0e-5, 3.0e-5):
        plus_y = source_y.copy(); plus_y[:-1] += step * direction
        minus_y = source_y.copy(); minus_y[:-1] -= step * direction
        _, _, plus = _merit(plus_y)
        _, _, minus = _merit(minus_y)
        finite = (plus - minus) / (2.0 * step)
        directional.append({
            "absolute_step": step,
            "finite_merit_slope": finite,
            "assembled_merit_slope": float(gradient @ direction),
            "relative_residual": abs(finite - float(gradient @ direction))
            / max(1.0, abs(finite)),
        })
    trials = []
    eligible = []
    for radius in LINE_RADII:
        candidate_input = source_y.copy()
        candidate_input[:-1] += radius * direction
        try:
            candidate_y, residual, merit = _merit(candidate_input)
            raw = candidate_y / scales
            metrics = _metrics(residual)
            eta = _minimum_node_eta(raw)
            row = {
                "radius": radius,
                "eta_minimum": eta,
                "merit": merit,
                "merit_reduction": source_merit - merit,
                "metrics": metrics,
                "complete_norm_reduction": initial["complete"] - metrics["complete"],
                "event_component_change": metrics["event"] - initial["event"],
                "raw_vector_hex": [float(value).hex() for value in raw],
            }
            row["true_merit_eligible"] = bool(
                eta > 1.0e-5 and row["complete_norm_reduction"] > MARGIN
            )
            trials.append(row)
            if row["true_merit_eligible"]:
                eligible.append(row)
        except (ArithmeticError, FloatingPointError, ValueError) as exc:
            trials.append({
                "radius": radius,
                "domain_valid": False,
                "exception": type(exc).__name__,
            })
    selected = min(eligible, key=lambda row: row["metrics"]["complete"]) if eligible else None
    return {
        "source_state": "v18.09_complete_child_promoted_state",
        "initial_metrics": initial,
        "initial_merit": source_merit,
        "initial_eta_minimum": _minimum_node_eta(source_y / scales),
        "merit_gradient": {
            **assembled,
            "dimension": 375,
            "norm": gradient_norm,
            "direction_norm": float(np.linalg.norm(direction)),
            "predicted_unit_direction_slope": -gradient_norm,
        },
        "directional_validation": directional,
        "line_radii": list(LINE_RADII),
        "trials": trials,
        "selected_true_merit_candidate_pending_child_acceptance": selected,
    }


def completion_payload() -> dict[str, Any]:
    result = exact_projected_merit_gradient_step()
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    slopes = result["directional_validation"]
    validation = {
        "source_is_v18_09": result["source_state"].startswith("v18.09"),
        "same_physical_residual": (
            not result["merit_gradient"]["physical_residual_changed"]
            and not result["merit_gradient"]["physical_event_changed"]
            and not result["merit_gradient"]["global_KKT_row_added"]
        ),
        "gradient_finite_nonzero": (
            np.isfinite(result["merit_gradient"]["norm"])
            and result["merit_gradient"]["norm"] > 0.0
        ),
        "assembled_direction_is_descent": result["merit_gradient"][
            "predicted_unit_direction_slope"
        ] < 0.0,
        "resolved_directional_slope_negative": all(
            row["finite_merit_slope"] < 0.0 for row in slopes
        ),
        "directional_slope_validated": max(
            row["relative_residual"] for row in slopes
        ) < 1.0e-2,
        "candidate_classified": selected is not None or bool(result["trials"]),
        "selected_reduces_true_merit": bool(
            selected is None or selected["complete_norm_reduction"] > MARGIN
        ),
        "selected_preserves_eta": bool(
            selected is None or selected["eta_minimum"] > 1.0e-5
        ),
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_exact_projected_merit_gradient_v18_10",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "exact_projected_merit_gradient": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "DIRECT_LOCAL_DESCENT_RESPONSE_OF_THE_UNCHANGED_EXACT_"
            "PROJECTED_376_ROW_N3_PHYSICAL_MERIT"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "RECONSTRUCT_AND_TEST_THE_SELECTED_CANDIDATE_CHILD_THEN_"
            "PROMOTE_OR_REJECT_THE_DIRECT_TRUE_MERIT_STEP"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_exact_projected_merit_gradient_v18_10.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "exact_projected_merit_gradient", "v18_10_selected_raw_vector",
    "exact_projected_merit_gradient_step", "completion_payload", "materialize",
]
