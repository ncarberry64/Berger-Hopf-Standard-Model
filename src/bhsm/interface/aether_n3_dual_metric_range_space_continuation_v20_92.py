"""Continue the curvature-aware dual-metric range-space solve from v20.91."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_dual_metric_range_space_proposal_v20_91 import (
    dual_metric_range_space_proposal, v20_91_selected_raw_vector,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json


VERSION = "v20.92"
CLASSIFICATION = "BHSM_N3_DUAL_METRIC_RANGE_SPACE_CONTINUATION"
FULL_BHSM_COMPLETE = False


def v20_92_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_DUAL_METRIC_RANGE_SPACE_CONTINUATION_V20_92.json"
    ).read_text(encoding="utf-8"))["dual_metric_range_space_continuation"]
    if not payload["promotion"]["promoted"]:
        raise ValueError("v20.92 has no physically promoted state")
    return np.asarray([float.fromhex(value) for value in payload["exact_search"]["best"]["raw_vector_hex"]])


def completion_payload() -> dict[str, Any]:
    result = dual_metric_range_space_proposal(v20_91_selected_raw_vector(), source_label="v20.91")
    best = result["exact_search"]["best"]
    validation = {
        "source_v20_91_reproduced": abs(result["source"]["exact_rayleigh_f376_l2"] - 0.785805767011881) < 5.0e-12,
        "both_bhsm_metrics_used": result["dual_metric_model"]["physical_metric"].startswith("EXISTING_BHSM") and result["dual_metric_model"]["action_metric"].startswith("VALIDATED_V18_15"),
        "exact_rows_decide": result["exact_search"]["original_unweighted_376_rows_authoritative"],
        "candidate_reduces_merit": best is None or best["exact_reduction"] > 0.0,
        "promotion_requires_child": not result["promotion"]["promoted"] or result["promotion"]["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"] and not result["event_definition_changed"] and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_DUAL_METRIC_RANGE_SPACE_CONTINUATION_V20_92", "version": VERSION,
        "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "dual_metric_range_space_continuation": result, "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation, "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_DUAL_METRIC_RANGE_SPACE_CONTINUATION_V20_92.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v20_92_selected_raw_vector", "completion_payload", "materialize"]
