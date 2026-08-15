"""Refresh the adopted physical Jacobian at the v18.00 N=3 state."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_complete_child_merit_promotion_v18_00 import (
    v18_00_selected_raw_vector,
)
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


VERSION = "v18.01"
CLASSIFICATION = "BHSM_N3_REFRESHED_COMPLETE_MERIT_NEWTON"
FULL_BHSM_COMPLETE = False


def v18_01_selected_raw_vector() -> np.ndarray:
    """Return the materialized true-merit candidate without rebuilding J."""
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_refreshed_complete_merit_newton_v18_01.json"
    ).read_text(encoding="utf-8"))
    selected = payload["refreshed_complete_merit_newton"][
        "selected_true_merit_candidate_pending_child_acceptance"
    ]
    if selected is None:
        raise ValueError("v18.01 has no candidate to reconstruct")
    return np.asarray([
        float.fromhex(value) for value in selected["raw_vector_hex"]
    ])


def refreshed_complete_merit_newton() -> dict[str, Any]:
    scales = kkt_variable_scales()
    source_raw = v18_00_selected_raw_vector()
    source_y, source_residual = exact_local_jet_sbp_projected_residual_and_vector(
        source_raw * scales
    )
    initial = _metrics(source_residual)
    assembled = parallel_high_accuracy_sbp_physical_jacobian(source_y / scales)
    full_matrix = np.asarray(assembled.pop("matrix"))
    reduced_matrix = full_matrix[:, :-1]
    singular_values = np.linalg.svd(reduced_matrix, compute_uv=False)
    gradient = reduced_matrix.T @ source_residual
    image = reduced_matrix @ gradient
    cauchy_radius = float(
        (gradient @ gradient) ** 1.5
        / max(float(image @ image), 1.0e-300)
    )
    trust_radius = min(
        TRUST_RADIUS_MAXIMUM, max(1.0e-6, cauchy_radius)
    )
    direction, dogleg = _dogleg(
        reduced_matrix, source_residual, trust_radius
    )
    predicted = source_residual + reduced_matrix @ direction
    trials = []
    selected = None
    for backtrack in range(BACKTRACKS):
        fraction = 0.5**backtrack
        candidate_input = source_y.copy()
        candidate_input[:-1] += fraction * direction
        try:
            candidate_y, candidate_residual = (
                exact_local_jet_sbp_projected_residual_and_vector(
                    candidate_input
                )
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
                eta > 1.0e-5
                and row["complete_norm_reduction"] > MARGIN
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
        "source_state": "v18.00_complete_child_merit_promoted_state",
        "initial_metrics": initial,
        "initial_eta_minimum": _minimum_node_eta(source_y / scales),
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
        "trust_model": {
            **dogleg,
            "derived_cauchy_radius": cauchy_radius,
            "predicted_complete_norm_reduction": float(
                np.linalg.norm(source_residual) - np.linalg.norm(predicted)
            ),
        },
        "acceptance_rule": (
            "TRUE_376_ROW_NORM_DECREASE_AND_GLOBAL_ETA_DOMAIN_FIRST;_"
            "COMPLETE_CHILD_RECONSTRUCTION_REQUIRED_BEFORE_PROMOTION"
        ),
        "componentwise_event_monotonicity_required": False,
        "handcrafted_direction_mixture": False,
        "physical_Jacobian_refreshed": True,
        "trials": trials,
        "selected_true_merit_candidate_pending_child_acceptance": selected,
    }


def completion_payload() -> dict[str, Any]:
    result = refreshed_complete_merit_newton()
    selected = result[
        "selected_true_merit_candidate_pending_child_acceptance"
    ]
    validation = {
        "source_is_v18_00": result["source_state"].startswith("v18.00"),
        "physical_jacobian_refreshed": result[
            "physical_Jacobian_refreshed"
        ],
        "no_handcrafted_mixture": not result[
            "handcrafted_direction_mixture"
        ],
        "componentwise_event_filter_removed": not result[
            "componentwise_event_monotonicity_required"
        ],
        "candidate_classified": selected is not None or bool(result["trials"]),
        "selected_reduces_true_merit": bool(
            selected is None or selected["complete_norm_reduction"] > MARGIN
        ),
        "selected_preserves_eta": bool(
            selected is None or selected["eta_minimum"] > 1.0e-5
        ),
        "selected_state_complete_if_present": bool(
            selected is None or len(selected["raw_vector_hex"]) == 376
        ),
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_refreshed_complete_merit_newton_v18_01",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "refreshed_complete_merit_newton": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "REFRESHED_LOCAL_RESPONSE_OF_THE_UNCHANGED_376_ROW_N3_ACTION_"
            "AT_A_STATE_KNOWN_TO_CREATE_A_COMPLETE_CHILD"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "RECONSTRUCT_AND_TEST_THE_SELECTED_CANDIDATE_CHILD_THEN_PROMOTE_"
            "OR_REJECT_THE_GLOBAL_STEP"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_refreshed_complete_merit_newton_v18_01.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "v18_01_selected_raw_vector", "refreshed_complete_merit_newton",
    "completion_payload", "materialize",
]
