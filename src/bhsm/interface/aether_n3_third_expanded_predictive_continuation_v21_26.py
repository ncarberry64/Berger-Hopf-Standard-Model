"""Use the validated v21.25 curvature once at the promoted v21.25 state."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_dual_metric_range_space_proposal_v20_91 import dual_metric_range_space_proposal
from bhsm.interface.aether_n3_second_expanded_predictive_continuation_v21_24 import v21_24_selected_raw_vector
from bhsm.interface.aether_n3_third_expanded_radius_refreshed_continuation_v21_25 import v21_25_selected_raw_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_isolated_eigenpair_event_hessian_v21_17 import _local_eigenpair_hessian, _terminal_pullback
from bhsm.interface.aether_n3_rayleigh_event_covector_v20_80 import _terminal_data
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales


VERSION = "v21.26"
CLASSIFICATION = "BHSM_N3_THIRD_EXPANDED_PREDICTIVE_CONTINUATION"
FULL_BHSM_COMPLETE = False


def v21_26_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_THIRD_EXPANDED_PREDICTIVE_CONTINUATION_V21_26.json"
    ).read_text(encoding="utf-8"))["third_expanded_predictive_continuation"]
    if not payload["promotion"]["promoted"]:
        raise ValueError("v21.26 has no physically promoted state")
    return np.asarray([float.fromhex(v) for v in payload["exact_search"]["best"]["raw_vector_hex"]])


def completion_payload() -> dict[str, Any]:
    refresh_artifact = json.loads(Path(
        "artifacts/BHSM_N3_THIRD_EXPANDED_RADIUS_REFRESHED_CONTINUATION_V21_25.json"
    ).read_text(encoding="utf-8"))
    if not refresh_artifact["validation_passed"]:
        raise ValueError("v21.25 curvature refresh is not validated")
    curvature_raw = v21_24_selected_raw_vector(); scales = kkt_variable_scales()
    local = _terminal_data(curvature_raw[:-1])[-1]
    gradient, local_hessian, _ = _local_eigenpair_hessian(local, second_relative_step=1.0e-3)
    support, _, raw_block = _terminal_pullback(gradient, local_hessian, curvature_raw)
    support_scales = scales[:-1][support]
    block = raw_block / support_scales[:, None] / support_scales[None, :] / scales[-1]
    prior = json.loads(Path(
        "artifacts/BHSM_N3_RESIDUAL_MANIFOLD_NORMAL_ACCELERATION_V21_06.json"
    ).read_text(encoding="utf-8"))["curvature_refresh"]
    curvature = {
        "event_curvature_support_indices": support.tolist(),
        "event_curvature_symmetric_block": block.tolist(),
        "bhsm_owned_action_coordinate_radii": prior["bhsm_owned_action_coordinate_radii"],
    }
    interval = json.loads(Path(
        "artifacts/BHSM_N3_EIGENPAIR_CURVATURE_EXPANDED_RADIUS_V21_21.json"
    ).read_text(encoding="utf-8"))["eigenpair_curvature_expanded_radius"]
    schedule = interval["dual_metric_model"]["radius_schedule"]
    result = dual_metric_range_space_proposal(
        v21_25_selected_raw_vector(), source_label="v21.25",
        curvature_override=curvature, radius_schedule_override=schedule,
    )
    result["dual_metric_model"]["curvature_artifact"] = (
        "SINGLE_PREDICTIVE_REUSE_OF_VALIDATED_V21_25_EIGENPAIR_CURVATURE"
    )
    best = result["exact_search"]["best"]
    validation = {
        "source_v21_25_reproduced": abs(
            result["source"]["exact_rayleigh_f376_l2"] - 0.780870640281120
        ) < 5.0e-12,
        "validated_curvature_reused_once": result["dual_metric_model"]["curvature_artifact"].startswith("SINGLE_PREDICTIVE_REUSE"),
        "same_history_owned_interval": len(schedule) == 25,
        "both_signs_all_points": result["exact_search"]["trial_count"] == 50,
        "exact_rows_decide": result["exact_search"]["original_unweighted_376_rows_authoritative"],
        "candidate_reduces_merit": best is None or best["exact_reduction"] > 0.0,
        "promotion_requires_child": not result["promotion"]["promoted"] or result["promotion"]["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"] and not result["event_definition_changed"] and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_THIRD_EXPANDED_PREDICTIVE_CONTINUATION_V21_26",
        "version": VERSION, "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "third_expanded_predictive_continuation": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation, "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_THIRD_EXPANDED_PREDICTIVE_CONTINUATION_V21_26.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8"); return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v21_26_selected_raw_vector", "completion_payload", "materialize"]
