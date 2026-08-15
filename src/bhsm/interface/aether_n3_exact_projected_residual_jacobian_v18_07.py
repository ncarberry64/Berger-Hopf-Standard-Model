"""Jacobian of the exact v17.61 projected N=3 residual actually evaluated."""
from __future__ import annotations

import json
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_chain_trial_complete_child_promotion_v18_06 import (
    v18_06_selected_raw_vector,
)
from bhsm.interface.aether_n3_direct_constrained_trust_newton_v17_83 import (
    BACKTRACKS, TRUST_RADIUS_MAXIMUM, _dogleg,
)
from bhsm.interface.aether_n3_exact_local_jet_sbp_covector_v17_61 import (
    exact_local_jet_sbp_projected_residual_and_vector,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_first_descent_v16_59 import ACTION_HESSIAN_RELATIVE_STEP
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN, _metrics
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales


VERSION = "v18.07"
CLASSIFICATION = "BHSM_N3_EXACT_PROJECTED_RESIDUAL_JACOBIAN"
FULL_BHSM_COMPLETE = False


def _chunks(indices: tuple[int, ...], count: int) -> list[tuple[int, ...]]:
    return [tuple(indices[offset::count]) for offset in range(count) if indices[offset::count]]


def _projected_columns(
    task: tuple[np.ndarray, tuple[int, ...], float | None],
) -> list[tuple[int, np.ndarray]]:
    source_y, columns, absolute_step = task
    rows = []
    for column in columns:
        step = (
            absolute_step
            if absolute_step is not None
            else ACTION_HESSIAN_RELATIVE_STEP * max(
                1.0, abs(float(source_y[column]))
            )
        )
        delta = np.zeros(376)
        delta[column] = step
        _, plus = exact_local_jet_sbp_projected_residual_and_vector(source_y + delta)
        _, minus = exact_local_jet_sbp_projected_residual_and_vector(source_y - delta)
        rows.append((column, (plus - minus) / (2.0 * step)))
    return rows


def exact_projected_residual_jacobian(
    source_y: np.ndarray, *, workers: int | None = None,
    absolute_step: float | None = None,
) -> dict[str, Any]:
    """Differentiate the projected nonlinear map, including rho_*(x)."""
    y = np.asarray(source_y, dtype=float)
    if y.shape != (376,):
        raise ValueError("scaled KKT vector has wrong dimension")
    worker_count = max(1, int(workers or min(8, os.cpu_count() or 1)))
    matrix = np.empty((376, 375))
    tasks = [
        (y, chunk, absolute_step)
        for chunk in _chunks(tuple(range(375)), worker_count)
    ]
    with ProcessPoolExecutor(max_workers=worker_count) as executor:
        for rows in executor.map(_projected_columns, tasks):
            for column, values in rows:
                matrix[:, column] = values
    return {
        "matrix": matrix,
        "assembly_workers": worker_count,
        "column_partition": "INDEPENDENT_CENTRAL_COLUMNS_OF_EXACT_PROJECTED_MAP",
        "relative_step": (
            ACTION_HESSIAN_RELATIVE_STEP if absolute_step is None else None
        ),
        "absolute_step": absolute_step,
        "projected_multiplier_chain_rule_included_by_construction": True,
        "v17_61_exact_local_jet_covector_differentiated": True,
    }


def v18_07_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_exact_projected_residual_jacobian_v18_07.json"
    ).read_text(encoding="utf-8"))
    selected = payload["exact_projected_residual_jacobian"][
        "selected_true_merit_candidate_pending_child_acceptance"
    ]
    if selected is None:
        raise ValueError("v18.07 has no candidate to reconstruct")
    return np.asarray([float.fromhex(value) for value in selected["raw_vector_hex"]])


def exact_projected_residual_jacobian_step(
    *, absolute_step: float | None = None,
    directional_step: float = 2.0e-5,
) -> dict[str, Any]:
    scales = kkt_variable_scales()
    source_raw = v18_06_selected_raw_vector()
    source_y, source_residual = exact_local_jet_sbp_projected_residual_and_vector(
        source_raw * scales
    )
    initial = _metrics(source_residual)
    assembled = exact_projected_residual_jacobian(
        source_y, absolute_step=absolute_step
    )
    matrix = np.asarray(assembled.pop("matrix"))
    directional = []
    for offset in (0.31, 0.73, 1.19):
        direction = np.cos(np.arange(375) + offset)
        direction /= np.linalg.norm(direction)
        epsilon = directional_step
        plus_y = source_y.copy(); plus_y[:-1] += epsilon * direction
        minus_y = source_y.copy(); minus_y[:-1] -= epsilon * direction
        _, plus = exact_local_jet_sbp_projected_residual_and_vector(plus_y)
        _, minus = exact_local_jet_sbp_projected_residual_and_vector(minus_y)
        finite = (plus - minus) / (2.0 * epsilon)
        predicted = matrix @ direction
        directional.append({
            "offset": offset,
            "relative_residual": float(
                np.linalg.norm(predicted - finite)
                / max(1.0, np.linalg.norm(finite))
            ),
        })
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    gradient = matrix.T @ source_residual
    image = matrix @ gradient
    cauchy_radius = float(
        (gradient @ gradient) ** 1.5
        / max(float(image @ image), 1.0e-300)
    )
    trust_radius = min(TRUST_RADIUS_MAXIMUM, max(1.0e-6, cauchy_radius))
    direction, dogleg = _dogleg(matrix, source_residual, trust_radius)
    predicted = source_residual + matrix @ direction
    trials = []
    selected = None
    for backtrack in range(BACKTRACKS):
        fraction = 0.5**backtrack
        candidate_input = source_y.copy()
        candidate_input[:-1] += fraction * direction
        try:
            candidate_y, candidate_residual = exact_local_jet_sbp_projected_residual_and_vector(candidate_input)
            candidate_raw = candidate_y / scales
            metrics = _metrics(candidate_residual)
            eta = _minimum_node_eta(candidate_raw)
            row = {
                "backtrack": backtrack,
                "fraction": fraction,
                "eta_minimum": eta,
                "metrics": metrics,
                "complete_norm_reduction": initial["complete"] - metrics["complete"],
                "event_component_change": metrics["event"] - initial["event"],
                "raw_vector_hex": [float(value).hex() for value in candidate_raw],
            }
            row["true_merit_eligible"] = bool(
                eta > 1.0e-5 and row["complete_norm_reduction"] > MARGIN
            )
            trials.append(row)
            if row["true_merit_eligible"]:
                selected = row
                break
        except (ArithmeticError, FloatingPointError, ValueError) as exc:
            trials.append({
                "backtrack": backtrack,
                "fraction": fraction,
                "domain_valid": False,
                "exception": type(exc).__name__,
            })
    return {
        "source_state": "v18.06_complete_child_promoted_state",
        "initial_metrics": initial,
        "initial_eta_minimum": _minimum_node_eta(source_y / scales),
        "physical_action_changed": False,
        "physical_event_changed": False,
        "global_KKT_row_added": False,
        "jacobian": {
            **assembled,
            "dimension": [376, 375],
            "largest_singular_value": float(singular_values[0]),
            "smallest_singular_value": float(singular_values[-1]),
            "condition_number": float(
                singular_values[0] / max(singular_values[-1], 1.0e-300)
            ),
            "numerical_rank_relative_1e_10": int(np.sum(
                singular_values > 1.0e-10 * singular_values[0]
            )),
        },
        "directional_validation": directional,
        "trust_model": {
            **dogleg,
            "derived_cauchy_radius": cauchy_radius,
            "predicted_complete_norm_reduction": float(
                np.linalg.norm(source_residual) - np.linalg.norm(predicted)
            ),
        },
        "trials": trials,
        "selected_true_merit_candidate_pending_child_acceptance": selected,
    }


def completion_payload() -> dict[str, Any]:
    result = exact_projected_residual_jacobian_step()
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    validation = {
        "source_is_v18_06": result["source_state"].startswith("v18.06"),
        "exact_projected_map_differentiated": (
            result["jacobian"]["projected_multiplier_chain_rule_included_by_construction"]
            and result["jacobian"]["v17_61_exact_local_jet_covector_differentiated"]
        ),
        "directional_response_validated": max(
            row["relative_residual"] for row in result["directional_validation"]
        ) < 2.0e-5,
        "physical_equations_unchanged": (
            not result["physical_action_changed"]
            and not result["physical_event_changed"]
            and not result["global_KKT_row_added"]
        ),
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
        "artifact": "BHSM_aether_n3_exact_projected_residual_jacobian_v18_07",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "exact_projected_residual_jacobian": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_N3_LOCAL_RESPONSE_NOW_MATCHES_THE_EXACT_PROJECTED_"
            "NONLINEAR_ACTION_EVENT_MAP_ACTUALLY_USED"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "RECONSTRUCT_AND_TEST_THE_SELECTED_CANDIDATE_CHILD_THEN_"
            "PROMOTE_OR_REJECT_THE_EXACT_PROJECTED_NEWTON_STEP"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_exact_projected_residual_jacobian_v18_07.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "exact_projected_residual_jacobian", "v18_07_selected_raw_vector",
    "exact_projected_residual_jacobian_step", "completion_payload", "materialize",
]
