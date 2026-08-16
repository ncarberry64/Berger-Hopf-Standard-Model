"""Refresh the Rayleigh curvature/singular audit at the accepted v20.92 frontier."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from bhsm.interface.aether_n3_curvature_singular_subspace_audit_v20_89 import curvature_singular_subspace_audit
from bhsm.interface.aether_n3_dual_metric_range_space_continuation_v20_92 import v20_92_selected_raw_vector
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json


VERSION = "v20.93"
CLASSIFICATION = "BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_REFRESH"
FULL_BHSM_COMPLETE = False


def completion_payload() -> dict[str, Any]:
    result = curvature_singular_subspace_audit(v20_92_selected_raw_vector(), source_label="v20.92")
    response = result["response"]
    validation = {
        "source_v20_92_reproduced": abs(result["source"]["exact_rayleigh_f376_l2"] - 0.785778751174718) < 5.0e-12,
        "rank_boundary_resolved": response["weakest_retained_singular_value"] > response["tolerance"] >= response["strongest_discarded_singular_value"],
        "residual_in_retained_range": response["source_residual_outside_retained_range_l2"] < 2.0e-5,
        "child_chart_surjective": result["child_compatible_tangent"]["rank_DcG"] == 14,
        "same_physics": not result["physical_equations_changed"] and not result["event_definition_changed"] and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_REFRESH_V20_93", "version": VERSION,
        "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "curvature_singular_subspace_refresh": result, "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation, "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_REFRESH_V20_93.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "completion_payload", "materialize"]
