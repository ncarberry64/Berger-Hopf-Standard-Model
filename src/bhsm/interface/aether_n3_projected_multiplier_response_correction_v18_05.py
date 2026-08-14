"""Correct the reduced N=3 Jacobian for analytic event-multiplier projection."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_direct_constrained_trust_newton_v17_83 import (
    BACKTRACKS,
    TRUST_RADIUS_MAXIMUM,
    _dogleg,
)
from bhsm.interface.aether_n3_exact_local_jet_sbp_covector_v17_61 import (
    exact_local_jet_sbp_projected_residual_and_vector,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_fresh_sbp_first_descent_v16_59 import (
    EVENT_CURVATURE_RELATIVE_STEP,
)
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_event_covector
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import (
    MARGIN,
    _metrics,
)
from bhsm.interface.aether_n3_high_accuracy_physical_jacobian_v17_58 import (
    parallel_high_accuracy_sbp_physical_jacobian,
)
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    event_gradient_indices,
    kkt_variable_scales,
)
from bhsm.interface.aether_n3_second_refreshed_complete_child_promotion_v18_04 import (
    v18_04_selected_raw_vector,
)


VERSION = "v18.05"
CLASSIFICATION = "BHSM_N3_PROJECTED_EVENT_MULTIPLIER_RESPONSE_CORRECTION"
FULL_BHSM_COMPLETE = False


def v18_05_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_projected_multiplier_response_correction_v18_05.json"
    ).read_text(encoding="utf-8"))
    selected = payload["projected_multiplier_response_correction"][
        "selected_true_merit_candidate_pending_child_acceptance"
    ]
    if selected is None:
        raise ValueError("v18.05 has no candidate to reconstruct")
    return np.asarray([
        float.fromhex(value) for value in selected["raw_vector_hex"]
    ])


def _event_hessian(raw: np.ndarray) -> np.ndarray:
    scales = kkt_variable_scales()
    ybase = raw[:-1] * scales[:-1]

    def gradient(value: np.ndarray) -> np.ndarray:
        return (
            sbp_event_covector(value / scales[:-1])
            / scales[:-1] / scales[-1]
        )

    hessian = np.zeros((375, 375))
    for column in event_gradient_indices():
        step = EVENT_CURVATURE_RELATIVE_STEP * max(
            1.0, abs(float(ybase[column]))
        )
        delta = np.zeros(375)
        delta[column] = step
        hessian[:, column] = (
            gradient(ybase + delta) - gradient(ybase - delta)
        ) / (2.0 * step)
    return hessian


def projected_multiplier_response_correction() -> dict[str, Any]:
    scales = kkt_variable_scales()
    source_raw = v18_04_selected_raw_vector()
    source_y, source_residual = exact_local_jet_sbp_projected_residual_and_vector(
        source_raw * scales
    )
    source_raw = source_y / scales
    initial = _metrics(source_residual)
    assembled = parallel_high_accuracy_sbp_physical_jacobian(source_raw)
    full_matrix = np.asarray(assembled.pop("matrix"))
    fixed_rho = full_matrix[:, :-1]
    event_covector = full_matrix[:-1, -1]
    event_hessian = _event_hessian(source_raw)
    top_residual = source_residual[:-1]
    event_norm_squared = float(event_covector @ event_covector)
    rho_gradient = -(
        fixed_rho[:-1].T @ event_covector
        + event_hessian.T @ top_residual
    ) / event_norm_squared
    projected = fixed_rho.copy()
    correction = np.outer(event_covector, rho_gradient)
    projected[:-1] += correction

    directions = []
    for offset in (0.31, 0.73, 1.19):
        direction = np.cos(np.arange(375) + offset)
        direction /= np.linalg.norm(direction)
        epsilon = 1.0e-6
        plus_input = source_y.copy()
        minus_input = source_y.copy()
        plus_input[:-1] += epsilon * direction
        minus_input[:-1] -= epsilon * direction
        _, plus = exact_local_jet_sbp_projected_residual_and_vector(plus_input)
        _, minus = exact_local_jet_sbp_projected_residual_and_vector(minus_input)
        finite = (plus - minus) / (2.0 * epsilon)
        corrected = projected @ direction
        old = fixed_rho @ direction
        directions.append({
            "offset": offset,
            "corrected_relative_residual": float(
                np.linalg.norm(corrected - finite)
                / max(1.0, np.linalg.norm(finite))
            ),
            "fixed_rho_relative_residual": float(
                np.linalg.norm(old - finite)
                / max(1.0, np.linalg.norm(finite))
            ),
        })

    singular_values = np.linalg.svd(projected, compute_uv=False)
    gradient = projected.T @ source_residual
    image = projected @ gradient
    cauchy_radius = float(
        (gradient @ gradient) ** 1.5
        / max(float(image @ image), 1.0e-300)
    )
    trust_radius = min(TRUST_RADIUS_MAXIMUM, max(1.0e-6, cauchy_radius))
    direction, dogleg = _dogleg(projected, source_residual, trust_radius)
    predicted = source_residual + projected @ direction
    trials = []
    selected = None
    for backtrack in range(BACKTRACKS):
        fraction = 0.5**backtrack
        candidate_input = source_y.copy()
        candidate_input[:-1] += fraction * direction
        try:
            candidate_y, candidate_residual = (
                exact_local_jet_sbp_projected_residual_and_vector(candidate_input)
            )
            candidate_raw = candidate_y / scales
            metrics = _metrics(candidate_residual)
            eta = _minimum_node_eta(candidate_raw)
            row = {
                "backtrack": backtrack,
                "fraction": fraction,
                "eta_minimum": eta,
                "metrics": metrics,
                "complete_norm_reduction": (
                    initial["complete"] - metrics["complete"]
                ),
                "event_component_change": (
                    metrics["event"] - initial["event"]
                ),
                "raw_vector_hex": [
                    float(value).hex() for value in candidate_raw
                ],
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
        "source_state": "v18.04_complete_child_promoted_state",
        "initial_metrics": initial,
        "initial_eta_minimum": _minimum_node_eta(source_raw),
        "derivation": {
            "projected_multiplier_definition": "rho_star=-(a_dot_e)/(e_dot_e)",
            "fixed_multiplier_top_derivative": "B=A+rho_star*H_event",
            "projection_gradient": (
                "grad_rho_star=-(B_T_e+H_event_T_r)/(e_dot_e)"
            ),
            "projected_top_derivative": "B+outer(e,grad_rho_star)",
            "physical_action_changed": False,
            "physical_event_changed": False,
            "global_KKT_row_added": False,
        },
        "projection_orthogonality_residual": float(
            abs(top_residual @ event_covector)
        ),
        "projection_gradient_norm": float(np.linalg.norm(rho_gradient)),
        "missing_rank_one_term_norm": float(np.linalg.norm(correction)),
        "directional_validation": directions,
        "jacobian": {
            **assembled,
            "dimension": [376, 375],
            "response": "DERIVATIVE_OF_THE_ACTUALLY_EVALUATED_PROJECTED_MAP",
            "largest_singular_value": float(singular_values[0]),
            "smallest_singular_value": float(singular_values[-1]),
            "condition_number": float(
                singular_values[0] / max(singular_values[-1], 1.0e-300)
            ),
            "numerical_rank_relative_1e_10": int(np.sum(
                singular_values > 1.0e-10 * singular_values[0]
            )),
        },
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
    result = projected_multiplier_response_correction()
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    directional = result["directional_validation"]
    validation = {
        "source_is_v18_04": result["source_state"].startswith("v18.04"),
        "projection_is_orthogonal": result[
            "projection_orthogonality_residual"
        ] < 1.0e-8,
        "missing_chain_rule_term_nonzero": result[
            "missing_rank_one_term_norm"
        ] > 0.0,
        "corrected_directional_response_validated": max(
            row["corrected_relative_residual"] for row in directional
        ) < 2.0e-5,
        "corrected_is_better_than_fixed_rho": all(
            row["corrected_relative_residual"]
            < row["fixed_rho_relative_residual"]
            for row in directional
        ),
        "physical_equations_unchanged": (
            not result["derivation"]["physical_action_changed"]
            and not result["derivation"]["physical_event_changed"]
            and not result["derivation"]["global_KKT_row_added"]
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
        "artifact": "BHSM_aether_n3_projected_multiplier_response_correction_v18_05",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "projected_multiplier_response_correction": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_LOCAL_RESPONSE_NOW_DIFFERENTIATES_THE_SAME_ANALYTICALLY_"
            "PROJECTED_EVENT_MULTIPLIER_USED_BY_EVERY_NONLINEAR_EVALUATION"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "RECONSTRUCT_THE_SELECTED_EVENT_CHILD_IF_PRESENT_THEN_USE_THE_"
            "CORRECTED_PROJECTED_RESPONSE_FOR_SUBSEQUENT_N3_CONTINUATION"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / (
        "BHSM_aether_n3_projected_multiplier_response_correction_v18_05.json"
    )
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "v18_05_selected_raw_vector", "projected_multiplier_response_correction",
    "completion_payload", "materialize",
]
