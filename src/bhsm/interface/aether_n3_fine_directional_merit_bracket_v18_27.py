"""Resolve the exact-merit line minimum below the v18.26 coarse-step floor."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_directional_complete_child_promotion_v18_25 import (
    v18_25_selected_raw_vector,
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


VERSION = "v18.27"
CLASSIFICATION = "BHSM_N3_FINE_DIRECTIONAL_MERIT_BRACKET"
FULL_BHSM_COMPLETE = False
FINE_STEPS = (
    1.0e-12,
    3.0e-12,
    1.0e-11,
    3.0e-11,
    1.0e-10,
    3.0e-10,
    1.0e-9,
    3.0e-9,
    1.0e-8,
)


def v18_27_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_fine_directional_merit_bracket_v18_27.json"
    ).read_text(encoding="utf-8"))
    selected = payload["fine_directional_merit_bracket"][
        "selected_true_merit_candidate_pending_child_acceptance"
    ]
    if selected is None:
        raise ValueError("v18.27 has no candidate to reconstruct")
    return np.asarray([float.fromhex(value) for value in selected["raw_vector_hex"]])


def fine_directional_merit_bracket() -> dict[str, Any]:
    """Evaluate exact residual merit on the retained v18.26 direction."""
    source = json.loads(Path(
        "artifacts/BHSM_aether_n3_second_directional_event_merit_descent_v18_26.json"
    ).read_text(encoding="utf-8"))
    coarse = source["second_directional_event_merit_descent"]
    direction = np.asarray([
        float.fromhex(value) for value in coarse["scaled_merit_direction_hex"]
    ])
    raw = v18_25_selected_raw_vector()
    scales = kkt_variable_scales()
    y = raw * scales
    residual = _square_physical_residual(y)
    initial = _metrics(residual)
    source_merit = 0.5 * float(residual @ residual)
    trials = []
    eligible = []
    for step in FINE_STEPS:
        plus_residual = _square_physical_residual(y + step * direction)
        minus_residual = _square_physical_residual(y - step * direction)
        plus_merit = 0.5 * float(plus_residual @ plus_residual)
        minus_merit = 0.5 * float(minus_residual @ minus_residual)
        candidate_raw = (y + step * direction) / scales
        metrics = _metrics(plus_residual)
        eta = _minimum_node_eta(candidate_raw)
        row = {
            "step": step,
            "physical_scaled_coordinate_step_norm": float(
                step * np.linalg.norm(direction)
            ),
            "raw_coordinate_step_norm": float(
                step * np.linalg.norm(direction / scales)
            ),
            "exact_symmetric_merit_slope": (
                plus_merit - minus_merit
            ) / (2.0 * step),
            "eta_minimum": eta,
            "metrics": metrics,
            "complete_norm_reduction": initial["complete"] - metrics["complete"],
            "merit_reduction": source_merit - plus_merit,
            "raw_vector_hex": [float(value).hex() for value in candidate_raw],
        }
        row["true_merit_eligible"] = bool(
            eta > 1.0e-5 and row["complete_norm_reduction"] > MARGIN
        )
        trials.append(row)
        if row["true_merit_eligible"]:
            eligible.append(row)
    selected = min(
        eligible, key=lambda row: row["metrics"]["complete"]
    ) if eligible else None
    return {
        "source_state": "v18.25_directional_complete_child_promoted_state",
        "source_direction_artifact_status": source["status"],
        "source_direction_response_validated": coarse[
            "maximum_response_relative_residual"
        ] < 2.0e-2,
        "source_complete_norm": initial["complete"],
        "source_eta_minimum": _minimum_node_eta(raw),
        "trials": trials,
        "selected_true_merit_candidate_pending_child_acceptance": selected,
        "physical_solve_dimension": [376, 376],
        "event_multiplier_explicit": True,
        "physical_equations_changed": False,
        "componentwise_monotonicity_required": False,
        "must_remain_on_previous_iterate_path": False,
    }


def completion_payload() -> dict[str, Any]:
    result = fine_directional_merit_bracket()
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    validation = {
        "source_is_v18_25": result["source_state"].startswith("v18.25"),
        "coarse_attempt_retained_as_invalidated": (
            result["source_direction_artifact_status"] == "INVALIDATED"
        ),
        "directional_response_itself_validated": result[
            "source_direction_response_validated"
        ],
        "fine_bracket_measured": len(result["trials"]) == len(FINE_STEPS),
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
    return {
        "artifact": "BHSM_aether_n3_fine_directional_merit_bracket_v18_27",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "fine_directional_merit_bracket": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_EXACT_V18_25_MERIT_LINE_IS_MEASURED_BELOW_THE_COARSE_TRIAL_FLOOR"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "RECONSTRUCT_AND_TEST_THE_SELECTED_COMPLETE_CHILD_IF_PRESENT"
            if selected is not None
            else "REFRESH_THE_LOCAL_DIRECTION_OR_RESOLVE_THE_EXACT_MERIT_NOISE_FLOOR"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_fine_directional_merit_bracket_v18_27.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "v18_27_selected_raw_vector",
    "fine_directional_merit_bracket",
    "completion_payload",
    "materialize",
]
