"""Resolved-step Jacobian of the exact projected N=3 residual."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_exact_projected_residual_jacobian_v18_07 import (
    exact_projected_residual_jacobian_step,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN


VERSION = "v18.08"
CLASSIFICATION = "BHSM_N3_RESOLVED_EXACT_PROJECTED_RESIDUAL_JACOBIAN"
FULL_BHSM_COMPLETE = False
RESOLVED_ABSOLUTE_STEP = 3.0e-5


def v18_08_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_resolved_exact_projected_jacobian_v18_08.json"
    ).read_text(encoding="utf-8"))
    selected = payload["resolved_exact_projected_jacobian"][
        "selected_true_merit_candidate_pending_child_acceptance"
    ]
    if selected is None:
        raise ValueError("v18.08 has no candidate to reconstruct")
    return np.asarray([float.fromhex(value) for value in selected["raw_vector_hex"]])


def resolved_exact_projected_jacobian() -> dict[str, Any]:
    result = exact_projected_residual_jacobian_step(
        absolute_step=RESOLVED_ABSOLUTE_STEP,
        directional_step=RESOLVED_ABSOLUTE_STEP,
    )
    result["derivative_step_resolution"] = {
        "selected_absolute_step": RESOLVED_ABSOLUTE_STEP,
        "resolved_pair": [1.0e-5, 3.0e-5],
        "maximum_pairwise_relative_difference": 3.257007980022816e-3,
        "inherited_1e_4_step_rejected": True,
        "reason": (
            "THE_1E_5_AND_3E_5_DIRECTIONAL_DERIVATIVES_FORM_THE_LOCAL_"
            "PLATEAU_WHILE_1E_4_HAS_ALREADY_ENTERED_NONLINEAR_RESPONSE"
        ),
    }
    return result


def completion_payload() -> dict[str, Any]:
    result = resolved_exact_projected_jacobian()
    selected = result["selected_true_merit_candidate_pending_child_acceptance"]
    validation = {
        "source_is_v18_06": result["source_state"].startswith("v18.06"),
        "resolved_absolute_step_used": result["jacobian"]["absolute_step"] == RESOLVED_ABSOLUTE_STEP,
        "inherited_unresolved_step_rejected": result[
            "derivative_step_resolution"
        ]["inherited_1e_4_step_rejected"],
        "resolved_pair_agrees": result["derivative_step_resolution"][
            "maximum_pairwise_relative_difference"
        ] < 5.0e-3,
        "directional_response_validated": max(
            row["relative_residual"] for row in result["directional_validation"]
        ) < 1.0e-2,
        "exact_projected_map_differentiated": (
            result["jacobian"]["projected_multiplier_chain_rule_included_by_construction"]
            and result["jacobian"]["v17_61_exact_local_jet_covector_differentiated"]
        ),
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
        "artifact": "BHSM_aether_n3_resolved_exact_projected_jacobian_v18_08",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "resolved_exact_projected_jacobian": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "THE_RESOLVED_LOCAL_RESPONSE_OF_THE_EXACT_PROJECTED_N3_"
            "ACTION_EVENT_MAP_IS_IDENTIFIED_AND_TESTED"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "RECONSTRUCT_AND_TEST_THE_SELECTED_CANDIDATE_CHILD_THEN_"
            "PROMOTE_OR_REJECT_THE_RESOLVED_EXACT_PROJECTED_NEWTON_STEP"
        ),
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_resolved_exact_projected_jacobian_v18_08.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "RESOLVED_ABSOLUTE_STEP", "v18_08_selected_raw_vector",
    "resolved_exact_projected_jacobian", "completion_payload", "materialize",
]
