"""Run one continuation after the promoted v20.98 refreshed proposal."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from bhsm.interface.aether_n3_dual_metric_range_space_proposal_v20_91 import dual_metric_range_space_proposal
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_refreshed_dual_metric_proposal_v20_98 import v20_98_selected_raw_vector


VERSION = "v20.99"
CLASSIFICATION = "BHSM_N3_REFRESHED_DUAL_METRIC_CONTINUATION"
FULL_BHSM_COMPLETE = False


def completion_payload() -> dict[str, Any]:
    result = dual_metric_range_space_proposal(
        v20_98_selected_raw_vector(),
        source_label="v20.98",
        curvature_artifact="artifacts/BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_REFRESH_V20_97.json",
        curvature_key="curvature_singular_subspace_refresh",
    )
    best = result["exact_search"]["best"]
    validation = {
        "source_v20_98_reproduced": abs(
            result["source"]["exact_rayleigh_f376_l2"] - 0.782783159793278
        ) < 5.0e-12,
        "v20_97_curvature_used": result["dual_metric_model"]["curvature_artifact"].endswith("V20_97.json"),
        "exact_rows_decide": result["exact_search"]["original_unweighted_376_rows_authoritative"],
        "candidate_reduces_merit": best is None or best["exact_reduction"] > 0.0,
        "promotion_requires_child": not result["promotion"]["promoted"] or result["promotion"]["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"]
        and not result["event_definition_changed"]
        and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_REFRESHED_DUAL_METRIC_CONTINUATION_V20_99",
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
    path = target / "BHSM_N3_REFRESHED_DUAL_METRIC_CONTINUATION_V20_99.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "completion_payload", "materialize"]
