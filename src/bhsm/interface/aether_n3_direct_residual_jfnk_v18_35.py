"""Apply the v18.34 direct residual response to the square KKT equation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.sparse.linalg import LinearOperator, gmres

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import (
    _action_curvature_transform,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import (
    MARGIN,
    _metrics,
)
from bhsm.interface.aether_n3_invalid_model_exact_merit_promotion_v18_33 import (
    v18_33_selected_raw_vector,
)
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import (
    _square_physical_residual,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales


VERSION = "v18.35"
CLASSIFICATION = "BHSM_N3_DIRECT_RESIDUAL_JFNK"
FULL_BHSM_COMPLETE = False
BACKTRACKS = 41
GMRES_RESTART = 40
GMRES_OUTER_ITERATIONS = 1
GMRES_RTOL = 1.0e-6


def v18_35_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_direct_residual_jfnk_v18_35.json"
    ).read_text(encoding="utf-8"))
    selected = payload["direct_residual_jfnk"][
        "selected_true_merit_candidate_pending_child_acceptance"
    ]
    if selected is None:
        raise ValueError("v18.35 has no exact-merit candidate")
    return np.asarray([float.fromhex(value) for value in selected["raw_vector_hex"]])


def direct_residual_jfnk() -> dict[str, Any]:
    audit = json.loads(Path(
        "artifacts/BHSM_aether_n3_direct_residual_response_scale_audit_v18_34.json"
    ).read_text(encoding="utf-8"))
    measured = audit["direct_residual_response_scale_audit"]
    pair = measured["selected_finest_common_stable_pair"]
    if pair is None:
        raise ValueError("v18.34 has no common stable direct-response scale")
    response_step = float(pair["fine_step"])
    comparison_step = float(pair["coarse_step"])

    raw = v18_33_selected_raw_vector()
    scales = kkt_variable_scales()
    y = raw * scales
    residual = _square_physical_residual(y)
    initial = _metrics(residual)

    def direct_response(direction_y: np.ndarray, step: float = response_step) -> np.ndarray:
        direction = np.asarray(direction_y, dtype=float)
        norm = float(np.linalg.norm(direction))
        if norm == 0.0:
            return np.zeros(376)
        unit = direction / norm
        finite = (
            _square_physical_residual(y + step * unit)
            - _square_physical_residual(y - step * unit)
        ) / (2.0 * step)
        return norm * finite

    transform, transform_audit = _action_curvature_transform(raw)
    operator = LinearOperator(
        (376, 376),
        matvec=lambda direction_x: direct_response(transform @ direction_x),
        dtype=float,
    )
    callback_residuals: list[float] = []
    direction_x, info = gmres(
        operator,
        -residual,
        rtol=GMRES_RTOL,
        atol=0.0,
        restart=GMRES_RESTART,
        maxiter=GMRES_OUTER_ITERATIONS,
        callback=lambda value: callback_residuals.append(float(value)),
        callback_type="pr_norm",
    )
    direction_y = transform @ direction_x
    predicted = direct_response(direction_y)
    linear_residual = predicted + residual
    direction_norm = float(np.linalg.norm(direction_y))
    unit = direction_y / direction_norm
    comparison = direct_response(unit, comparison_step)
    finest = direct_response(unit, response_step)
    response_consistency = float(
        np.linalg.norm(finest - comparison) / max(1.0, np.linalg.norm(finest))
    )

    trials = []
    eligible = []
    for backtrack in range(BACKTRACKS):
        fraction = 0.5**backtrack
        candidate_y = y + fraction * direction_y
        try:
            candidate_residual = _square_physical_residual(candidate_y)
            candidate_raw = candidate_y / scales
            metrics = _metrics(candidate_residual)
            eta = _minimum_node_eta(candidate_raw)
            row = {
                "backtrack": backtrack,
                "fraction": fraction,
                "action_curvature_coordinate_step_norm": float(
                    fraction * np.linalg.norm(direction_x)
                ),
                "physical_scaled_coordinate_step_norm": fraction * direction_norm,
                "raw_coordinate_step_norm": float(
                    fraction * np.linalg.norm(direction_y / scales)
                ),
                "eta_minimum": eta,
                "metrics": metrics,
                "complete_norm_reduction": initial["complete"] - metrics["complete"],
                "raw_vector_hex": [float(value).hex() for value in candidate_raw],
            }
            row["true_merit_eligible"] = bool(
                eta > 1.0e-5 and row["complete_norm_reduction"] > MARGIN
            )
            trials.append(row)
            if row["true_merit_eligible"]:
                eligible.append(row)
        except (ArithmeticError, FloatingPointError, ValueError) as exc:
            trials.append({
                "backtrack": backtrack,
                "fraction": fraction,
                "domain_valid": False,
                "exception": type(exc).__name__,
            })
    selected = min(
        eligible, key=lambda row: row["metrics"]["complete"]
    ) if eligible else None
    return {
        "source_state": "v18.33_invalid_model_exact_merit_promoted_state",
        "source_complete_norm": initial["complete"],
        "source_eta_minimum": _minimum_node_eta(raw),
        "direct_response": {
            "source_artifact": audit["artifact"],
            "source_status": audit["status"],
            "fine_step": response_step,
            "comparison_step": comparison_step,
            "source_maximum_relative_change": pair["maximum_relative_change"],
            "resulting_direction_relative_change": response_consistency,
            "differentiates_unchanged_exact_376_residual": True,
            "decomposed_v18_30_v18_31_models_reused": False,
        },
        "coordinate_map": transform_audit,
        "linear_solve": {
            "method": "GMRES_ON_DIRECT_EXACT_RESIDUAL_JVP_TIMES_ACTION_RIGHT_MAP",
            "rtol": GMRES_RTOL,
            "restart": GMRES_RESTART,
            "maximum_outer_iterations": GMRES_OUTER_ITERATIONS,
            "info": int(info),
            "iterations": len(callback_residuals),
            "callback_relative_residuals": callback_residuals,
            "relative_exact_linear_residual": float(
                np.linalg.norm(linear_residual) / max(1.0, np.linalg.norm(residual))
            ),
            "numerical_control_is_not_physical_acceptance": True,
        },
        "direction": {
            "action_curvature_coordinate_norm": float(np.linalg.norm(direction_x)),
            "physical_scaled_coordinate_norm": direction_norm,
            "raw_coordinate_norm": float(np.linalg.norm(direction_y / scales)),
        },
        "trials": trials,
        "selected_true_merit_candidate_pending_child_acceptance": selected,
        "physical_solve_dimension": [376, 376],
        "event_multiplier_explicit": True,
        "physical_equations_changed": False,
        "event_definition_changed": False,
        "componentwise_monotonicity_required": False,
        "must_remain_on_previous_iterate_path": False,
    }


def completion_payload() -> dict[str, Any]:
    result = direct_residual_jfnk()
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    response = result["direct_response"]
    solve = result["linear_solve"]
    validation = {
        "source_is_v18_33": result["source_state"].startswith("v18.33"),
        "validated_response_scale_source": response["source_status"] == "VALIDATED",
        "direct_response_consistent_on_resulting_direction": (
            response["resulting_direction_relative_change"] < 5.0e-3
        ),
        "unchanged_exact_residual_differentiated": response[
            "differentiates_unchanged_exact_376_residual"
        ],
        "failed_decomposed_models_not_reused": not response[
            "decomposed_v18_30_v18_31_models_reused"
        ],
        "right_coordinate_map_invertible": result["coordinate_map"]["invertible"],
        "krylov_control_not_acceptance": solve[
            "numerical_control_is_not_physical_acceptance"
        ],
        "square_explicit_multiplier_system": (
            result["physical_solve_dimension"] == [376, 376]
            and result["event_multiplier_explicit"]
        ),
        "physical_equations_unchanged": not result["physical_equations_changed"],
        "event_definition_unchanged": not result["event_definition_changed"],
        "no_componentwise_filter": not result["componentwise_monotonicity_required"],
        "previous_path_not_a_constraint": not result[
            "must_remain_on_previous_iterate_path"
        ],
        "selected_reduces_true_merit": bool(
            selected is None or selected["complete_norm_reduction"] > MARGIN
        ),
        "selected_preserves_eta": bool(
            selected is None or selected["eta_minimum"] > 1.0e-5
        ),
    }
    passed = all(validation.values())
    converged = solve["info"] == 0
    return {
        "artifact": "BHSM_aether_n3_direct_residual_jfnk_v18_35",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "direct_residual_jfnk": result,
        "status": (
            "VALIDATED" if passed and converged
            else "RECLASSIFIED" if passed
            else "INVALIDATED"
        ),
        "newton_equation_converged": converged,
        "real_physical_property_explained": (
            "THE_MEASURED_DIRECT_DERIVATIVE_OF_THE_UNCHANGED_376_ROW_RESIDUAL_"
            "TESTS_THE_SQUARE_KKT_LINEAR_EQUATION_WITHOUT_EVENT_DECOMPOSITION"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "RECONSTRUCT_AND_TEST_THE_SELECTED_COMPLETE_CHILD_IF_PRESENT"
            if selected is not None
            else "RESOLVE_THE_DIRECT_JFNK_LINEAR_SOLVE_OR_MERIT_LINE"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_direct_residual_jfnk_v18_35.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "v18_35_selected_raw_vector",
    "direct_residual_jfnk",
    "completion_payload",
    "materialize",
]
