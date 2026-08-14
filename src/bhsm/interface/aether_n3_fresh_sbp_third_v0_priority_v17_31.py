"""Fresh v0-priority continuation from the v17.30 dense-radius state."""
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

VERSION = "v17.31"
CLASSIFICATION = "BHSM_N3_FRESH_SBP_THIRD_V0_PRIORITY_MEASURED_TANGENT_FAMILY"
FULL_BHSM_COMPLETE = False
RADII = (0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.75, 1.0, 1.25)


def v17_30_selected_raw_vector() -> np.ndarray:
    payload = json.loads(
        Path(
            "artifacts/BHSM_aether_n3_fresh_sbp_event_dense_radius_v17_30.json"
        ).read_text(encoding="utf-8")
    )
    values = payload["fresh_sbp_event_dense_radius"]["selected_dense_radius"][
        "raw_vector_hex"
    ]
    raw = np.asarray([float.fromhex(value) for value in values])
    if raw.shape != (376,):
        raise ValueError("v17.30 selected vector has wrong dimension")
    return raw


def third_v0_priority() -> dict[str, Any]:
    return period_priority_family_from(
        v17_30_selected_raw_vector(),
        source_state="v17.30_selected_event_dense_radius_state",
        priority_owner="v0",
        priority_key="v0_priority",
        selection_key="selected_v0_priority_maximin",
        priorities=PRIORITIES,
        cauchy_factors=RADII,
    )


def completion_payload() -> dict[str, Any]:
    result = third_v0_priority()
    best = result["selected_v0_priority_maximin"]
    validation = {
        "v17_30_residual_reproduced": math.isclose(
            result["initial_metrics"]["complete"],
            1.054776763781015,
            rel_tol=0,
            abs_tol=2e-8,
        ),
        "v17_30_event_reproduced": math.isclose(
            result["initial_metrics"]["event"],
            0.09119557544008,
            rel_tol=0,
            abs_tol=2e-8,
        ),
        "source_state_owned": (
            result["source_state"] == "v17.30_selected_event_dense_radius_state"
        ),
        "physical_equations_unchanged": (
            not result["physical_residual_changed"]
            and not result["physical_event_changed"]
        ),
        "bounded_priorities_tested": result["priority_count"] == len(PRIORITIES),
        "all_families_tested": result["family_count"] == 7,
        "expanded_radius_grid_tested": len(RADII) == 12,
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
        "artifact": "BHSM_aether_n3_fresh_sbp_third_v0_priority_v17_31",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": False,
        "fresh_sbp_third_v0_priority": result,
        "status": "VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained": (
            "FRESH_SIX_OWNER_DESCENT_WITH_V0_PRECONDITIONING_AFTER_DENSE_EVENT_"
            "RADIUS_PROMOTION"
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
    path = target / "BHSM_aether_n3_fresh_sbp_third_v0_priority_v17_31.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "v17_30_selected_raw_vector",
    "third_v0_priority",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
