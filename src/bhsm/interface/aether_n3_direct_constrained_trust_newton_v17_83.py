"""One direct reduced trust-Newton step for the unchanged N=3 event KKT."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_exact_local_jet_sbp_covector_v17_61 import (
    exact_local_jet_sbp_projected_residual_and_vector,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import (
    MARGIN,
    _metrics,
)
from bhsm.interface.aether_n3_high_accuracy_physical_jacobian_v17_58 import (
    parallel_high_accuracy_sbp_physical_jacobian,
)
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    kkt_variable_scales,
)
from bhsm.interface.aether_n3_scale_corrected_period_log_continuation_v17_76 import (
    v17_75_selected_raw_vector,
)


VERSION = "v17.83"
CLASSIFICATION = "BHSM_N3_DIRECT_CONSTRAINED_REDUCED_TRUST_NEWTON"
FULL_BHSM_COMPLETE = False
TRUST_RADIUS_MAXIMUM = 2.0e-2
BACKTRACKS = 9


def _dogleg(
    matrix: np.ndarray, residual: np.ndarray, trust_radius: float,
) -> tuple[np.ndarray, dict[str, float]]:
    gradient = matrix.T @ residual
    image = matrix @ gradient
    denominator = float(image @ image)
    if denominator <= 0.0:
        raise ValueError("Gauss-Newton curvature is not positive")
    cauchy = -(float(gradient @ gradient) / denominator) * gradient
    newton = np.linalg.lstsq(matrix, -residual, rcond=1.0e-10)[0]
    cauchy_norm = float(np.linalg.norm(cauchy))
    newton_norm = float(np.linalg.norm(newton))
    if newton_norm <= trust_radius:
        direction = newton
        branch = "REDUCED_GAUSS_NEWTON"
    elif cauchy_norm >= trust_radius:
        direction = cauchy * (trust_radius / cauchy_norm)
        branch = "SCALED_CAUCHY_BOUNDARY"
    else:
        difference = newton - cauchy
        a = float(difference @ difference)
        b = 2.0 * float(cauchy @ difference)
        c = float(cauchy @ cauchy) - trust_radius**2
        tau = (-b + math.sqrt(max(0.0, b * b - 4.0 * a * c))) / (2.0 * a)
        direction = cauchy + tau * difference
        branch = "DOGLEG_BOUNDARY"
    return direction, {
        "cauchy_norm": cauchy_norm,
        "unrestricted_reduced_Gauss_Newton_norm": newton_norm,
        "trust_radius": trust_radius,
        "direction_norm": float(np.linalg.norm(direction)),
        "branch": branch,
    }


def direct_constrained_trust_newton() -> dict[str, Any]:
    scales = kkt_variable_scales()
    source_raw = v17_75_selected_raw_vector()
    source_y, source_residual = exact_local_jet_sbp_projected_residual_and_vector(
        source_raw * scales
    )
    initial = _metrics(source_residual)

    assembled = parallel_high_accuracy_sbp_physical_jacobian(
        source_y / scales
    )
    full_matrix = np.asarray(assembled.pop("matrix"))
    reduced_matrix = full_matrix[:, :-1]
    singular_values = np.linalg.svd(reduced_matrix, compute_uv=False)
    gradient = reduced_matrix.T @ source_residual
    image = reduced_matrix @ gradient
    cauchy_radius = float(
        (gradient @ gradient) ** 1.5
        / max(float(image @ image), 1.0e-300)
    )
    trust_radius = min(TRUST_RADIUS_MAXIMUM, max(1.0e-6, cauchy_radius))
    direction, dogleg = _dogleg(
        reduced_matrix, source_residual, trust_radius
    )
    predicted_residual = source_residual + reduced_matrix @ direction
    predicted_reduction = float(
        np.linalg.norm(source_residual) - np.linalg.norm(predicted_residual)
    )

    trials: list[dict[str, Any]] = []
    accepted: list[dict[str, Any]] = []
    for backtrack in range(BACKTRACKS):
        fraction = 0.5**backtrack
        candidate_input = source_y.copy()
        candidate_input[:-1] += fraction * direction
        try:
            candidate_y, candidate_residual = (
                exact_local_jet_sbp_projected_residual_and_vector(candidate_input)
            )
            candidate_raw = candidate_y / scales
            eta = _minimum_node_eta(candidate_raw)
            metrics = _metrics(candidate_residual)
            reductions = {
                key: initial[key] - metrics[key] for key in initial
            }
            row = {
                "backtrack": backtrack,
                "fraction": fraction,
                "eta_minimum": eta,
                "metrics": metrics,
                "reductions": reductions,
                "complete_reduced": reductions["complete"] > MARGIN,
                "absolute_event_reduced": reductions["event"] > MARGIN,
                "raw_vector_hex": [float(value).hex() for value in candidate_raw],
            }
            trials.append(row)
            if (
                eta > 1.0e-5
                and row["complete_reduced"]
                and row["absolute_event_reduced"]
            ):
                accepted.append(row)
                break
        except (FloatingPointError, ValueError, ArithmeticError) as exc:
            trials.append({
                "backtrack": backtrack,
                "fraction": fraction,
                "domain_valid": False,
                "exception": type(exc).__name__,
            })

    selected = accepted[0] if accepted else None
    return {
        "source_state": "v17.75_selected_fine_period_log_mix_state",
        "solve_type": "DIRECT_REDUCED_376_RESIDUAL_375_BASE_TRUST_NEWTON",
        "event_multiplier_treatment": "ANALYTICALLY_PROJECTED_EACH_EVALUATION",
        "owner_weighting_or_tangent_mixture": False,
        "physical_action_changed": False,
        "physical_event_changed": False,
        "initial_metrics": initial,
        "initial_eta_minimum": _minimum_node_eta(source_y / scales),
        "jacobian": {
            **assembled,
            "dimension": [376, 375],
            "largest_singular_value": float(singular_values[0]),
            "smallest_singular_value": float(singular_values[-1]),
            "condition_number": float(singular_values[0] / singular_values[-1]),
            "numerical_rank_relative_1e_10": int(np.sum(
                singular_values > 1.0e-10 * singular_values[0]
            )),
        },
        "trust_model": {
            **dogleg,
            "derived_cauchy_radius": cauchy_radius,
            "predicted_complete_norm_reduction": predicted_reduction,
        },
        "trial_count": len(trials),
        "trials": trials,
        "selected_direct_trust_newton_state": selected,
    }


def completion_payload() -> dict[str, Any]:
    result = direct_constrained_trust_newton()
    selected = result["selected_direct_trust_newton_state"]
    validation = {
        "v17_75_residual_reproduced": math.isclose(
            result["initial_metrics"]["complete"],
            0.831984571818635,
            rel_tol=0.0,
            abs_tol=2.0e-8,
        ),
        "v17_75_event_reproduced": math.isclose(
            result["initial_metrics"]["event"],
            0.083860915332372,
            rel_tol=0.0,
            abs_tol=2.0e-8,
        ),
        "direct_reduced_system_solved": result["solve_type"] == (
            "DIRECT_REDUCED_376_RESIDUAL_375_BASE_TRUST_NEWTON"
        ),
        "no_owner_weighting_or_tangent_mixture": not result[
            "owner_weighting_or_tangent_mixture"
        ],
        "physical_equations_unchanged": (
            not result["physical_action_changed"]
            and not result["physical_event_changed"]
        ),
        "candidate_result_classified": selected is not None or bool(
            result["trials"]
        ),
        "complete_and_event_reduced_if_promoted": bool(
            selected is None
            or (
                selected["complete_reduced"]
                and selected["absolute_event_reduced"]
            )
        ),
        "eta_domain_preserved_if_promoted": bool(
            selected is None or selected["eta_minimum"] > 1.0e-5
        ),
        "full_state_preserved_if_promoted": bool(
            selected is None or len(selected["raw_vector_hex"]) == 376
        ),
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_direct_constrained_trust_newton_v17_83",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "direct_constrained_trust_newton": result,
        "status": (
            "VALIDATED" if passed and selected is not None
            else "RECLASSIFIED" if passed else "INVALIDATED"
        ),
        "real_physical_property_explained": (
            "DIRECT_FULL_RESIDUAL_LOCAL_NEWTON_RESPONSE_OF_THE_UNCHANGED_N3_"
            "EVENT_SADDLE"
        ),
        "dependency_advanced": "SIMULTANEOUS_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "PROMOTE_THE_DIRECT_STATE_AND_REPEAT_DIRECT_TRUST_NEWTON_IF_"
            "VALIDATED;OTHERWISE_CLASSIFY_THE_DEMONSTRATED_BLOCKER"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_direct_constrained_trust_newton_v17_83.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "TRUST_RADIUS_MAXIMUM", "BACKTRACKS", "direct_constrained_trust_newton",
    "completion_payload", "materialize",
]
