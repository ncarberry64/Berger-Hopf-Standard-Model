"""Run one continuation after the predictive v20.94 refreshed proposal."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_dual_metric_range_space_proposal_v20_91 import (
    dual_metric_range_space_proposal,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_refreshed_dual_metric_proposal_v20_94 import (
    v20_94_selected_raw_vector,
)


VERSION = "v20.95"
CLASSIFICATION = "BHSM_N3_REFRESHED_DUAL_METRIC_CONTINUATION"
FULL_BHSM_COMPLETE = False


def v20_95_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_REFRESHED_DUAL_METRIC_CONTINUATION_V20_95.json"
    ).read_text(encoding="utf-8"))["refreshed_dual_metric_continuation"]
    if not payload["promotion"]["promoted"]:
        raise ValueError("v20.95 has no physically promoted state")
    return np.asarray([
        float.fromhex(value) for value in payload["exact_search"]["best"]["raw_vector_hex"]
    ])


def completion_payload() -> dict[str, Any]:
    result = dual_metric_range_space_proposal(
        v20_94_selected_raw_vector(),
        source_label="v20.94",
        curvature_artifact=(
            "artifacts/BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_REFRESH_V20_93.json"
        ),
        curvature_key="curvature_singular_subspace_refresh",
    )
    best = result["exact_search"]["best"]
    validation = {
        "source_v20_94_reproduced": abs(
            result["source"]["exact_rayleigh_f376_l2"] - 0.783613548218730
        ) < 5.0e-12,
        "refreshed_curvature_used": result["dual_metric_model"][
            "curvature_artifact"
        ].endswith("V20_93.json"),
        "exact_rows_decide": result["exact_search"][
            "original_unweighted_376_rows_authoritative"
        ],
        "candidate_reduces_merit": best is None or best["exact_reduction"] > 0.0,
        "promotion_requires_child": not result["promotion"]["promoted"] or result[
            "promotion"
        ]["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"]
        and not result["event_definition_changed"]
        and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_REFRESHED_DUAL_METRIC_CONTINUATION_V20_95",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "refreshed_dual_metric_continuation": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_REFRESHED_DUAL_METRIC_CONTINUATION_V20_95.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "v20_95_selected_raw_vector",
    "completion_payload",
    "materialize",
]
