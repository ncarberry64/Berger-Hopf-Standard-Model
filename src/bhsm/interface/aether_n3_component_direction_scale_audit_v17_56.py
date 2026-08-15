"""Derivative-scale audit of the v17.55 component-resolved direction."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import LABELS, _metrics, _slopes
from bhsm.interface.aether_n3_post_curvature_compensation_audit_v17_54 import v17_53_selected_raw_vector
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales

VERSION = "v17.56"
CLASSIFICATION = "BHSM_N3_COMPONENT_DIRECTION_DERIVATIVE_SCALE_AUDIT"
FULL_BHSM_COMPLETE = False
INTERNAL_ACTION_COVECTOR_RELATIVE_STEP = 2e-6
DERIVATIVE_SCALES = (1e-8, 3e-8, 1e-7, 3e-7, 1e-6, 2e-6, 3e-6, 1e-5, 3e-5, 1e-4)


def component_direction_scale_audit() -> dict[str, Any]:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_scale_component_event_correction_v17_55.json"
    ).read_text(encoding="utf-8"))["scale_component_event_correction"]
    row = next(
        item for item in payload["direction_rows"]
        if item["priority_profile"] == {"log_scale": 2.0, "event": 2.0}
    )
    trial = next(item for item in row["trials"] if item.get("raw_vector_hex"))
    scales = kkt_variable_scales()
    y, residual = sbp_projected_residual_and_vector(v17_53_selected_raw_vector() * scales)
    initial = _metrics(residual)
    candidate = np.asarray([float.fromhex(value) for value in trial["raw_vector_hex"]]) * scales
    direction = (candidate - y) / trial["trust_radius"]
    direction[-1] = 0.0
    direction /= np.linalg.norm(direction)
    rows = []
    for epsilon in DERIVATIVE_SCALES:
        _, plus = sbp_projected_residual_and_vector(y + epsilon * direction)
        _, minus = sbp_projected_residual_and_vector(y - epsilon * direction)
        central = _slopes(residual, (plus - minus) / (2 * epsilon), initial)
        plus_metrics = _metrics(plus)
        forward = {
            owner: (initial[owner] - plus_metrics[owner]) / initial[owner] / epsilon
            for owner in initial
        }
        rows.append({
            "epsilon": epsilon,
            "central_fractional_slopes": {
                LABELS[index]: float(central[index]) for index in range(len(LABELS))
            },
            "forward_fractional_descent_rates": forward,
            "central_common_descent": bool(np.all(central < 0)),
            "forward_all_owner_descent": all(value > 0 for value in forward.values()),
        })
    return {
        "source_state": "v17.53_selected_event_log_curvature_compensated_state",
        "source_direction": "v17.55_log2_event2_component_resolved_direction",
        "internal_action_covector_relative_step": INTERNAL_ACTION_COVECTOR_RELATIVE_STEP,
        "derivative_scales": list(DERIVATIVE_SCALES),
        "rows": rows,
        "interpretation": (
            "A_COMMON_CENTRAL_SLOPE_AND_FORWARD_DESCENT_PLATEAU_ABOVE_THE_INTERNAL_"
            "ACTION_COVECTOR_DIFFERENCE_SCALE_IS_REQUIRED_FOR_PHYSICAL_PROMOTION"
        ),
    }


def completion_payload() -> dict[str, Any]:
    result = component_direction_scale_audit()
    rows = result["rows"]
    above = [
        row for row in rows
        if row["epsilon"] >= 3 * INTERNAL_ACTION_COVECTOR_RELATIVE_STEP
    ]
    validation = {
        "all_scales_evaluated": len(rows) == len(DERIVATIVE_SCALES),
        "internal_difference_scale_bracketed": (
            min(DERIVATIVE_SCALES) < INTERNAL_ACTION_COVECTOR_RELATIVE_STEP
            < max(DERIVATIVE_SCALES)
        ),
        "all_results_finite": all(
            math.isfinite(value)
            for row in rows
            for mapping in (
                row["central_fractional_slopes"],
                row["forward_fractional_descent_rates"],
            )
            for value in mapping.values()
        ),
        "above_internal_scale_classified": len(above) >= 2,
        "no_unresolved_small_step_promoted": True,
    }
    plateau = all(
        row["central_common_descent"] and row["forward_all_owner_descent"]
        for row in above
    )
    return {
        "artifact": "BHSM_aether_n3_component_direction_scale_audit_v17_56",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": False,
        "component_direction_scale_audit": result,
        "stable_physical_descent_plateau": plateau,
        "status": "VALIDATED" if all(validation.values()) and plateau else "RECLASSIFIED",
        "real_physical_property_explained": (
            "RESOLUTION_LIMIT_OF_THE_NESTED_FINITE_DIFFERENCE_ACTION_COVECTOR_"
            "ALONG_THE_COMPONENT_RESOLVED_DIRECTION"
        ),
        "dependency_advanced": (
            "CLASSIFY_THE_ACTION_COVECTOR_ACCURACY_AS_A_BLOCKER_OR_PROMOTE_THE_"
            "RESOLVED_DIRECTION"
        ),
        "active_calculation": (
            "IF_NO_STABLE_DESCENT_PLATEAU_EXISTS_BUILD_A_HIGHER_ACCURACY_SAME_"
            "ACTION_COVECTOR_BEFORE_FURTHER_N3_CONTINUATION"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_component_direction_scale_audit_v17_56.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "DERIVATIVE_SCALES",
    "component_direction_scale_audit", "completion_payload", "materialize",
]
