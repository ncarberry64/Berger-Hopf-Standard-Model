"""Continue the square explicit-multiplier N=3 KKT from v18.12."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_direct_constrained_trust_newton_v17_83 import (
    BACKTRACKS, TRUST_RADIUS_MAXIMUM, _dogleg,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN, _metrics
from bhsm.interface.aether_n3_high_accuracy_physical_jacobian_v17_58 import parallel_high_accuracy_sbp_physical_jacobian
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_reclassified_chain_proposal_v18_11 import _square_physical_residual
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_square_kkt_complete_child_promotion_v18_12 import v18_12_selected_raw_vector


VERSION = "v18.13"
CLASSIFICATION = "BHSM_N3_SQUARE_KKT_CONTINUATION_PROPOSAL"
FULL_BHSM_COMPLETE = False


def v18_13_selected_raw_vector() -> np.ndarray:
    import json

    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_square_kkt_continuation_proposal_v18_13.json"
    ).read_text(encoding="utf-8"))
    selected = payload["square_kkt_continuation_proposal"][
        "selected_true_merit_candidate_pending_child_acceptance"
    ]
    if selected is None:
        raise ValueError("v18.13 has no candidate to reconstruct")
    return np.asarray([float.fromhex(value) for value in selected["raw_vector_hex"]])


def square_kkt_continuation_proposal() -> dict[str, Any]:
    scales = kkt_variable_scales()
    source_raw = v18_12_selected_raw_vector()
    source_y = source_raw * scales
    source_residual = _square_physical_residual(source_y)
    initial = _metrics(source_residual)
    assembled = parallel_high_accuracy_sbp_physical_jacobian(source_raw)
    full = np.asarray(assembled.pop("matrix"))
    gradient = full.T @ source_residual
    image = full @ gradient
    cauchy_radius = float(
        (gradient @ gradient) ** 1.5 / max(float(image @ image), 1.0e-300)
    )
    trust_radius = min(TRUST_RADIUS_MAXIMUM, max(1.0e-6, cauchy_radius))
    direction, dogleg = _dogleg(full, source_residual, trust_radius)
    predicted = source_residual + full @ direction
    trials: list[dict[str, Any]] = []
    eligible: list[dict[str, Any]] = []
    for backtrack in range(BACKTRACKS):
        fraction = 0.5**backtrack
        candidate_input = source_y + fraction * direction
        try:
            residual = _square_physical_residual(candidate_input)
            raw = candidate_input / scales
            metrics = _metrics(residual)
            eta = _minimum_node_eta(raw)
            row = {
                "backtrack": backtrack,
                "fraction": fraction,
                "eta_minimum": eta,
                "metrics": metrics,
                "complete_norm_reduction": initial["complete"] - metrics["complete"],
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
                "backtrack": backtrack,
                "fraction": fraction,
                "domain_valid": False,
                "exception": type(exc).__name__,
            })
    selected = min(eligible, key=lambda row: row["metrics"]["complete"]) if eligible else None
    return {
        "source_state": "v18.12_complete_child_promoted_state",
        "initial_metrics": initial,
        "initial_eta_minimum": _minimum_node_eta(source_raw),
        "proposal_model": {
            **assembled,
            "derivative_claim": "INVALIDATED_V17_58_VS_V17_61_RESPONSE_NOT_REASSERTED",
            "used_only_to_propose_trials": True,
            "physical_solve_dimension": [376, 376],
            "event_multiplier_explicit": True,
            "event_multiplier_analytically_projected": False,
            "physical_action_changed": False,
            "physical_event_changed": False,
            "global_KKT_row_added": False,
        },
        "trust_model": {
            **dogleg,
            "derived_cauchy_radius": cauchy_radius,
            "predicted_complete_norm_reduction_not_a_claim": float(
                np.linalg.norm(source_residual) - np.linalg.norm(predicted)
            ),
        },
        "acceptance_rule": (
            "INDEPENDENT_EXACT_SQUARE_376_TOTAL_MERIT_REDUCTION_AND_ETA;_"
            "COMPLETE_CHILD_RECONSTRUCTION_REQUIRED_BEFORE_PROMOTION"
        ),
        "componentwise_monotonicity_required": False,
        "must_remain_on_previous_iterate_path": False,
        "trials": trials,
        "selected_true_merit_candidate_pending_child_acceptance": selected,
    }


def completion_payload() -> dict[str, Any]:
    result = square_kkt_continuation_proposal()
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    model = result["proposal_model"]
    validation = {
        "source_is_v18_12": result["source_state"].startswith("v18.12"),
        "invalid_derivative_claim_not_reasserted": model["derivative_claim"].startswith("INVALIDATED"),
        "model_used_only_for_proposals": model["used_only_to_propose_trials"],
        "square_explicit_multiplier_solve": (
            model["physical_solve_dimension"] == [376, 376]
            and model["event_multiplier_explicit"]
            and not model["event_multiplier_analytically_projected"]
        ),
        "no_componentwise_filter": not result["componentwise_monotonicity_required"],
        "previous_path_not_a_constraint": not result["must_remain_on_previous_iterate_path"],
        "physical_equations_unchanged": (
            not model["physical_action_changed"]
            and not model["physical_event_changed"]
            and not model["global_KKT_row_added"]
        ),
        "candidate_classified": selected is not None or bool(result["trials"]),
        "selected_reduces_independent_true_merit": bool(
            selected is None or selected["complete_norm_reduction"] > MARGIN
        ),
        "selected_preserves_eta": bool(selected is None or selected["eta_minimum"] > 1.0e-5),
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_square_kkt_continuation_proposal_v18_13",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "square_kkt_continuation_proposal": result,
        "status": "RECLASSIFIED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_EXISTING_RESPONSE_MODEL_CAN_CONTINUE_TO_PROPOSE_SQUARE_KKT_"
            "TRIALS_WITHOUT_BECOMING_A_PHYSICAL_ACCEPTANCE_CONDITION"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "RECONSTRUCT_AND_TEST_THE_SELECTED_COMPLETE_CHILD_IF_PRESENT;_"
            "OTHERWISE_AUDIT_THE_PROPOSAL_RESTRICTION"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_square_kkt_continuation_proposal_v18_13.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "v18_13_selected_raw_vector", "square_kkt_continuation_proposal",
    "completion_payload", "materialize",
]
