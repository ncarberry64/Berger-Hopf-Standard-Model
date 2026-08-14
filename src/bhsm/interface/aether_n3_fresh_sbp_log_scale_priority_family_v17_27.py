"""Bounded log-scale-priority family after the v17.26 owner audit."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_fresh_sbp_period_priority_family_v17_25 import (
    MARGIN,
    PRIORITIES,
    period_priority_family_from,
)
from bhsm.interface.aether_n3_fresh_sbp_post_period_audit_v17_26 import (
    v17_25_selected_raw_vector,
)

VERSION = "v17.27"
CLASSIFICATION = "BHSM_N3_FRESH_SBP_LOG_SCALE_PRIORITY_MEASURED_TANGENT_FAMILY"
FULL_BHSM_COMPLETE = False


def log_scale_priority_family() -> dict[str, Any]:
    return period_priority_family_from(
        v17_25_selected_raw_vector(),
        source_state="v17.25_selected_period_priority_state",
        priority_owner="log_scale",
        priority_key="log_scale_priority",
        selection_key="selected_log_scale_priority_maximin",
    )


def completion_payload() -> dict[str, Any]:
    result = log_scale_priority_family()
    best = result["selected_log_scale_priority_maximin"]
    validation = {
        "v17_25_residual_reproduced": math.isclose(
            result["initial_metrics"]["complete"],
            1.127995335027502,
            rel_tol=0,
            abs_tol=2e-8,
        ),
        "v17_25_event_reproduced": math.isclose(
            result["initial_metrics"]["event"],
            0.095644921219748,
            rel_tol=0,
            abs_tol=2e-8,
        ),
        "v17_25_scale_reproduced": math.isclose(
            result["initial_metrics"]["log_scale"],
            0.349649642559301,
            rel_tol=0,
            abs_tol=2e-8,
        ),
        "source_state_owned": (
            result["source_state"] == "v17.25_selected_period_priority_state"
        ),
        "physical_equations_unchanged": (
            not result["physical_residual_changed"]
            and not result["physical_event_changed"]
        ),
        "bounded_priorities_tested": result["priority_count"] == len(PRIORITIES),
        "all_families_tested": result["family_count"] == 7,
        "common_direction_exists": result["common_direction_count"] > 0,
        "strict_candidate_exists": best is not None,
        "all_six_metrics_reduced": bool(
            best is not None
            and all(value > MARGIN for value in best["reductions"].values())
        ),
        "positive_maximin_progress": bool(
            best is not None and best["minimum_fractional_progress"] > 0
        ),
        "eta_domain_preserved": bool(
            best is not None and best["eta_minimum"] > 1e-5
        ),
        "full_precision_state_preserved": bool(
            best is not None and len(best["raw_vector_hex"]) == 376
        ),
    }
    return {
        "artifact": "BHSM_aether_n3_fresh_sbp_log_scale_priority_family_v17_27",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": False,
        "fresh_sbp_log_scale_priority_family": result,
        "status": "VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained": (
            "FINITE_NONLINEAR_SIX_OWNER_DESCENT_WITH_BOUNDED_LOG_SCALE_"
            "PRECONDITIONING"
        ),
        "dependency_advanced": "SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation": "PROMOTE_IF_VALIDATED_THEN_REAUDIT_THE_OWNER_SET",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return [_canonical(item) for item in value.tolist()]
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        return round(value, 15)
    if isinstance(value, Mapping):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_fresh_sbp_log_scale_priority_family_v17_27.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "log_scale_priority_family",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
