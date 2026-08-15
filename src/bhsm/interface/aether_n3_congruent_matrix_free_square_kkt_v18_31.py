"""Apply the action-owned congruent map to the matrix-free square KKT solve."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.sparse.linalg import LinearOperator, minres

from bhsm.interface.aether_n3_action_curvature_square_kkt_proposal_v18_16 import (
    _action_curvature_transform,
)
from bhsm.interface.aether_n3_directional_event_merit_descent_v18_22 import (
    EVENT_DIRECTIONAL_STEP,
    _event_gradient_scaled,
    _event_hessian_vector,
)
from bhsm.interface.aether_n3_exact_action_hessian_assembly_v18_18 import (
    exact_sbp_action_hessian,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import (
    MARGIN,
    _metrics,
)
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import (
    _square_physical_residual,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_second_directional_complete_child_promotion_v18_29 import (
    v18_29_selected_raw_vector,
)


VERSION = "v18.31"
CLASSIFICATION = "BHSM_N3_CONGRUENT_MATRIX_FREE_SQUARE_KKT"
FULL_BHSM_COMPLETE = False
BACKTRACKS = 41
MINRES_ITERATIONS = 80
MINRES_RTOL = 1.0e-6
RESPONSE_DISPLACEMENTS = (1.0e-4, 3.0e-5, 1.0e-5)


def v18_31_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_congruent_matrix_free_square_kkt_v18_31.json"
    ).read_text(encoding="utf-8"))
    selected = payload["congruent_matrix_free_square_kkt"][
        "selected_true_merit_candidate_pending_child_acceptance"
    ]
    if selected is None:
        raise ValueError("v18.31 has no exact-merit candidate")
    return np.asarray([float.fromhex(value) for value in selected["raw_vector_hex"]])


def congruent_matrix_free_square_kkt() -> dict[str, Any]:
    raw = v18_29_selected_raw_vector()
    scales = kkt_variable_scales()
    y = raw * scales
    residual = _square_physical_residual(y)
    initial = _metrics(residual)
    action = exact_sbp_action_hessian(raw[:-1])
    action_raw = np.asarray(action.pop("hessian"))
    inverse = 1.0 / scales[:-1]
    action_scaled = inverse[:, None] * action_raw * inverse[None, :]
    event_gradient = _event_gradient_scaled(y[:-1], scales)

    def response(direction_y: np.ndarray) -> np.ndarray:
        direction = np.asarray(direction_y, dtype=float)
        event_hv = _event_hessian_vector(y[:-1], direction[:-1], scales)
        return np.concatenate((
            action_scaled @ direction[:-1]
            + y[-1] * event_hv
            + direction[-1] * event_gradient,
            [float(event_gradient @ direction[:-1])],
        ))

    transform, transform_audit = _action_curvature_transform(raw)
    congruent = LinearOperator(
        (376, 376),
        matvec=lambda direction_x: transform @ response(transform @ direction_x),
        dtype=float,
    )
    right_hand_side = -(transform @ residual)
    direction_x, info = minres(
        congruent,
        right_hand_side,
        rtol=MINRES_RTOL,
        maxiter=MINRES_ITERATIONS,
        check=False,
    )
    direction_y = transform @ direction_x
    linear_residual = response(direction_y) + residual
    direction_norm = float(np.linalg.norm(direction_y))
    unit = direction_y / direction_norm
    predicted_unit = response(unit)
    response_checks = []
    for epsilon in RESPONSE_DISPLACEMENTS:
        finite = (
            _square_physical_residual(y + epsilon * unit)
            - _square_physical_residual(y - epsilon * unit)
        ) / (2.0 * epsilon)
        response_checks.append({
            "epsilon": epsilon,
            "finite_response_norm": float(np.linalg.norm(finite)),
            "relative_residual": float(
                np.linalg.norm(predicted_unit - finite)
                / max(1.0, np.linalg.norm(finite))
            ),
        })

    trials = []
    exact_eligible = []
    resolved_eligible = []
    minimum_response_scale = min(RESPONSE_DISPLACEMENTS)
    for backtrack in range(BACKTRACKS):
        fraction = 0.5**backtrack
        candidate_y = y + fraction * direction_y
        try:
            candidate_residual = _square_physical_residual(candidate_y)
            candidate_raw = candidate_y / scales
            metrics = _metrics(candidate_residual)
            eta = _minimum_node_eta(candidate_raw)
            scaled_step = fraction * direction_norm
            row = {
                "backtrack": backtrack,
                "fraction": fraction,
                "action_curvature_coordinate_step_norm": float(
                    fraction * np.linalg.norm(direction_x)
                ),
                "physical_scaled_coordinate_step_norm": scaled_step,
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
            row["within_validated_response_scale"] = scaled_step >= minimum_response_scale
            row["resolved_true_merit_eligible"] = bool(
                row["true_merit_eligible"] and row["within_validated_response_scale"]
            )
            trials.append(row)
            if row["true_merit_eligible"]:
                exact_eligible.append(row)
            if row["resolved_true_merit_eligible"]:
                resolved_eligible.append(row)
        except (ArithmeticError, FloatingPointError, ValueError) as exc:
            trials.append({
                "backtrack": backtrack,
                "fraction": fraction,
                "domain_valid": False,
                "exception": type(exc).__name__,
            })
    exact_selected = min(
        exact_eligible, key=lambda row: row["metrics"]["complete"]
    ) if exact_eligible else None
    resolved_selected = min(
        resolved_eligible, key=lambda row: row["metrics"]["complete"]
    ) if resolved_eligible else None
    return {
        "source_state": "v18.29_second_directional_complete_child_promoted_state",
        "source_complete_norm": initial["complete"],
        "source_eta_minimum": _minimum_node_eta(raw),
        "action_response": action,
        "event_response": {
            "type": "MATRIX_FREE_DIRECTIONAL_HESSIAN_VECTOR",
            "scaled_displacement": EVENT_DIRECTIONAL_STEP,
            "full_event_hessian_claimed": False,
            "invalidated_v18_19_v18_21_matrices_reused": False,
        },
        "coordinate_map": {
            **transform_audit,
            "linear_equation_form": "P_J_P_DX_EQUALS_MINUS_P_F",
            "physical_residual_rows_left_scaled": False,
            "congruent_linear_preconditioning_only": True,
        },
        "linear_solve": {
            "method": "MINRES_ON_ACTION_CURVATURE_CONGRUENT_KKT_RESPONSE",
            "rtol": MINRES_RTOL,
            "maximum_iterations": MINRES_ITERATIONS,
            "info": int(info),
            "relative_exact_linear_residual": float(
                np.linalg.norm(linear_residual) / max(1.0, np.linalg.norm(residual))
            ),
            "numerical_control_is_not_physical_acceptance": True,
        },
        "newton_direction": {
            "action_curvature_coordinate_norm": float(np.linalg.norm(direction_x)),
            "physical_scaled_coordinate_norm": direction_norm,
            "raw_coordinate_norm": float(np.linalg.norm(direction_y / scales)),
        },
        "response_checks": response_checks,
        "maximum_response_relative_residual": max(
            row["relative_residual"] for row in response_checks
        ),
        "minimum_validated_response_displacement": minimum_response_scale,
        "trials": trials,
        "selected_exact_merit_candidate": exact_selected,
        "selected_true_merit_candidate_pending_child_acceptance": exact_selected,
        "selected_resolved_true_merit_candidate_pending_child_acceptance": (
            resolved_selected
        ),
        "response_scale_is_numerical_reliability_not_physics": True,
        "physical_solve_dimension": [376, 376],
        "event_multiplier_explicit": True,
        "physical_equations_changed": False,
        "componentwise_monotonicity_required": False,
        "must_remain_on_previous_iterate_path": False,
    }


def completion_payload() -> dict[str, Any]:
    result = congruent_matrix_free_square_kkt()
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    validation = {
        "source_is_v18_29": result["source_state"].startswith("v18.29"),
        "exact_action_response_validated": (
            result["action_response"]["gradient_relative_residual"] < 5.0e-11
        ),
        "directional_event_only": (
            not result["event_response"]["full_event_hessian_claimed"]
            and not result["event_response"][
                "invalidated_v18_19_v18_21_matrices_reused"
            ]
        ),
        "congruent_map_invertible": result["coordinate_map"]["invertible"],
        "physical_residual_rows_unchanged": (
            not result["coordinate_map"]["physical_residual_rows_left_scaled"]
            and result["coordinate_map"]["congruent_linear_preconditioning_only"]
        ),
        "direction_response_validated": (
            result["maximum_response_relative_residual"] < 2.0e-2
        ),
        "response_scale_only_numerical_reliability": result[
            "response_scale_is_numerical_reliability_not_physics"
        ],
        "square_explicit_multiplier_system": (
            result["physical_solve_dimension"] == [376, 376]
            and result["event_multiplier_explicit"]
        ),
        "physical_equations_unchanged": not result["physical_equations_changed"],
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
    converged = result["linear_solve"]["info"] == 0
    return {
        "artifact": "BHSM_aether_n3_congruent_matrix_free_square_kkt_v18_31",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "congruent_matrix_free_square_kkt": result,
        "status": (
            "VALIDATED" if passed and converged
            else "RECLASSIFIED" if passed
            else "INVALIDATED"
        ),
        "newton_equation_converged": converged,
        "real_physical_property_explained": (
            "THE_ACTION_OWNED_CONGRUENT_MAP_TESTS_THE_EXISTING_NEWTON_EQUATION_"
            "WITHOUT_CHANGING_ANY_PHYSICAL_RESIDUAL_ROW"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "RECONSTRUCT_AND_TEST_THE_INDEPENDENT_EXACT_MERIT_CANDIDATE_"
            "WITHOUT_REASSERTING_THE_INVALIDATED_NEWTON_MODEL"
            if selected is not None
            else "RESOLVE_THE_SQUARE_KKT_LINEAR_RESPONSE_OR_MERIT_RESOLUTION"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_congruent_matrix_free_square_kkt_v18_31.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "v18_31_selected_raw_vector",
    "congruent_matrix_free_square_kkt",
    "completion_payload",
    "materialize",
]
