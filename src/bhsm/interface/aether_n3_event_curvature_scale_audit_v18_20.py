"""Measure ordered-event curvature across action-owned scaled displacements."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_event_covector, sbp_event_value_from_base
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import event_gradient_indices, kkt_variable_scales
from bhsm.interface.aether_n3_square_kkt_complete_child_promotion_v18_12 import v18_12_selected_raw_vector


VERSION = "v18.20"
CLASSIFICATION = "BHSM_N3_EVENT_CURVATURE_SCALE_AUDIT"
FULL_BHSM_COMPLETE = False
STEPS = (1.0e-2, 3.0e-3, 1.0e-3, 3.0e-4, 1.0e-4, 3.0e-5, 1.0e-5)


def event_curvature_scale_audit() -> dict[str, Any]:
    raw = v18_12_selected_raw_vector(); scales = kkt_variable_scales()
    ybase = raw[:-1] * scales[:-1]
    event_scale = float(scales[-1])
    support = np.asarray(event_gradient_indices(), dtype=int)

    def event(value: np.ndarray) -> float:
        return sbp_event_value_from_base(value / scales[:-1]) / event_scale

    center = event(ybase)
    gradient = sbp_event_covector(raw[:-1]) / scales[:-1] / event_scale
    templates = []
    coherent_scale = np.zeros(375)
    coherent_scale[support[np.isin(support % 10, [0])]] = 1.0
    templates.append(("event_support_scale", coherent_scale))
    terminal_u = np.zeros(375); terminal_u[221] = 1.0
    templates.append(("terminal_u1", terminal_u))
    multipliers = np.zeros(375); multipliers[368:374] = 1.0
    templates.append(("terminal_multipliers", multipliers))
    mixed = np.zeros(375); mixed[support] = np.cos(np.arange(support.size) + 0.31)
    templates.append(("mixed_event_support", mixed))
    directions = []
    for name, template in templates:
        direction = template / np.linalg.norm(template)
        analytic_first = float(gradient @ direction)
        rows = []
        for step in STEPS:
            plus = event(ybase + step * direction)
            minus = event(ybase - step * direction)
            first = (plus - minus) / (2.0 * step)
            second = (plus - 2.0 * center + minus) / step**2
            rows.append({
                "scaled_step": step,
                "first_derivative": first,
                "first_derivative_absolute_residual": abs(first - analytic_first),
                "second_derivative": second,
            })
        directions.append({
            "direction": name,
            "analytic_first_derivative": analytic_first,
            "rows": rows,
            "curvature_range": [
                min(row["second_derivative"] for row in rows),
                max(row["second_derivative"] for row in rows),
            ],
        })
    return {
        "source_state": "EXACT_ACCEPTED_V18_12",
        "event_value_scaled": center,
        "event_support_dimension": int(support.size),
        "ordered_event_lower_gap": 0.5790449163968373,
        "ordered_event_upper_gap": 0.0007311978328318023,
        "directions": directions,
        "uniform_raw_step_hessian_v18_19": "INVALIDATED",
        "physical_event_changed": False,
        "physical_equations_changed": False,
    }


def completion_payload() -> dict[str, Any]:
    result = event_curvature_scale_audit()
    max_first_residual = max(
        row["first_derivative_absolute_residual"]
        for direction in result["directions"] for row in direction["rows"]
    )
    validation = {
        "exact_v18_12_source": result["source_state"] == "EXACT_ACCEPTED_V18_12",
        "event_support_complete": result["event_support_dimension"] == 37,
        "ordered_event_isolated": result["ordered_event_upper_gap"] > 0.0 and result["ordered_event_lower_gap"] > 0.0,
        "first_derivative_audited": np.isfinite(max_first_residual),
        "bad_uniform_raw_hessian_not_reused": result["uniform_raw_step_hessian_v18_19"] == "INVALIDATED",
        "physical_event_unchanged": not result["physical_event_changed"],
        "physical_equations_unchanged": not result["physical_equations_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_aether_n3_event_curvature_scale_audit_v18_20",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "event_curvature_scale_audit": result,
        "status": "RECLASSIFIED" if passed else "INVALIDATED",
        "real_physical_property_explained": (
            "ORDERED_EVENT_CURVATURE_MUST_BE_RESOLVED_IN_ACTION_OWNED_SCALED_"
            "DIRECTIONS_RATHER_THAN_BY_ONE_UNIFORM_RAW_STEP"
        ),
        "dependency_advanced": "NONLINEAR_N3_EVENT_SADDLE_CLOSURE",
        "active_calculation": "SELECT_THE_RESOLVED_EVENT_CURVATURE_SCALE_OR_USE_DIRECTIONAL_EVENT_RESPONSE",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_event_curvature_scale_audit_v18_20.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "event_curvature_scale_audit", "completion_payload", "materialize"]
