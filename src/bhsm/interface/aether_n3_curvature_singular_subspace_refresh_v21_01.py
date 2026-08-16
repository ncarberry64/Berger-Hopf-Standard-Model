"""Direct Rayleigh curvature refresh at v20.99 for transport validation."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from bhsm.interface.aether_n3_curvature_singular_subspace_audit_v20_89 import curvature_singular_subspace_audit
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_refreshed_dual_metric_continuation_v20_99 import v20_99_selected_raw_vector


VERSION = "v21.01"
CLASSIFICATION = "BHSM_N3_DIRECT_CURVATURE_REFRESH_FOR_TRANSPORT_VALIDATION"
FULL_BHSM_COMPLETE = False


def completion_payload() -> dict[str, Any]:
    result = curvature_singular_subspace_audit(
        v20_99_selected_raw_vector(), source_label="v20.99"
    )
    response = result["response"]
    validation = {
        "source_v20_99_reproduced": abs(
            result["source"]["exact_rayleigh_f376_l2"] - 0.782780987846174
        ) < 5.0e-12,
        "rank_boundary_resolved": response["weakest_retained_singular_value"]
        > response["tolerance"]
        >= response["strongest_discarded_singular_value"],
        "residual_in_retained_range": response[
            "source_residual_outside_retained_range_l2"
        ] < 2.0e-5,
        "child_chart_surjective": result["child_compatible_tangent"]["rank_DcG"] == 14,
        "same_physics": not result["physical_equations_changed"]
        and not result["event_definition_changed"]
        and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_REFRESH_V21_01",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "curvature_singular_subspace_refresh": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_CURVATURE_SINGULAR_SUBSPACE_REFRESH_V21_01.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "completion_payload", "materialize"]
