"""Event-priority continuation from the audited v17.42 state."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_fresh_sbp_period_priority_family_v17_25 import (
    MARGIN,
    PRIORITIES,
    period_priority_family_from,
)
from bhsm.interface.aether_n3_fresh_sbp_third_v0_priority_v17_31 import RADII
from bhsm.interface.aether_n3_parallel_physical_jacobian_v17_32 import (
    parallel_sbp_physical_jacobian,
)

VERSION = "v17.43"
CLASSIFICATION = "BHSM_N3_FRESH_SBP_SECOND_EVENT_PRIORITY_MEASURED_TANGENT_FAMILY"
FULL_BHSM_COMPLETE = False


def v17_42_selected_raw_vector() -> np.ndarray:
    payload = json.loads(
        Path(
            "artifacts/BHSM_aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42.json"
        ).read_text(encoding="utf-8")
    )
    values = payload["fresh_sbp_asymmetric_period_v0_priority"][
        "selected_asymmetric_period_v0_priority_maximin"
    ]["raw_vector_hex"]
    raw = np.asarray([float.fromhex(value) for value in values])
    if raw.shape != (376,):
        raise ValueError("v17.42 selected vector has wrong dimension")
    return raw


def second_event_priority() -> dict[str, Any]:
    return period_priority_family_from(
        v17_42_selected_raw_vector(),
        source_state="v17.42_selected_asymmetric_period_v0_priority_state",
        priority_owner="event",
        priority_key="event_priority",
        selection_key="selected_event_priority_maximin",
        priorities=PRIORITIES,
        cauchy_factors=RADII,
        jacobian_builder=parallel_sbp_physical_jacobian,
    )


def completion_payload() -> dict[str, Any]:
    result = second_event_priority()
    best = result["selected_event_priority_maximin"]
    validation = {
        "v17_42_residual_reproduced": math.isclose(
            result["initial_metrics"]["complete"], 0.933415266557169,
            rel_tol=0, abs_tol=2e-8,
        ),
        "v17_42_event_reproduced": math.isclose(
            result["initial_metrics"]["event"], 0.085030910850866,
            rel_tol=0, abs_tol=2e-8,
        ),
        "source_state_owned": result["source_state"]
        == "v17.42_selected_asymmetric_period_v0_priority_state",
        "parallel_jacobian_adopted": result.get("assembly_workers") == 8,
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
        "artifact": "BHSM_aether_n3_fresh_sbp_second_event_priority_v17_43",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": False,
        "fresh_sbp_second_event_priority": result,
        "status": "VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained": (
            "SAME_ACTION_SIX_OWNER_DESCENT_WITH_EVENT_PRECONDITIONING_AFTER_"
            "THE_V17_42_EVENT_LIMITER_TRANSITION"
        ),
        "dependency_advanced": "SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation": "PROMOTE_IF_VALIDATED_THEN_REAUDIT_THE_OWNER_SET",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_fresh_sbp_second_event_priority_v17_43.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "v17_42_selected_raw_vector", "second_event_priority",
    "completion_payload", "materialize",
]
