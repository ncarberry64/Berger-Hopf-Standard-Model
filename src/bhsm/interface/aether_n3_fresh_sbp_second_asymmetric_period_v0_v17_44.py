"""Second asymmetric period/v0 continuation from validated v17.43."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    PRIORITY_PROFILES,
    deterministic_json,
)
from bhsm.interface.aether_n3_fresh_sbp_period_priority_family_v17_25 import (
    MARGIN,
    period_priority_family_from,
)
from bhsm.interface.aether_n3_fresh_sbp_third_v0_priority_v17_31 import RADII
from bhsm.interface.aether_n3_parallel_physical_jacobian_v17_32 import (
    parallel_sbp_physical_jacobian,
)

VERSION = "v17.44"
CLASSIFICATION = "BHSM_N3_FRESH_SBP_SECOND_ASYMMETRIC_PERIOD_V0_MEASURED_TANGENT_FAMILY"
FULL_BHSM_COMPLETE = False


def v17_43_selected_raw_vector() -> np.ndarray:
    payload = json.loads(
        Path(
            "artifacts/BHSM_aether_n3_fresh_sbp_second_event_priority_v17_43.json"
        ).read_text(encoding="utf-8")
    )
    values = payload["fresh_sbp_second_event_priority"][
        "selected_event_priority_maximin"
    ]["raw_vector_hex"]
    raw = np.asarray([float.fromhex(value) for value in values])
    if raw.shape != (376,):
        raise ValueError("v17.43 selected vector has wrong dimension")
    return raw


def second_asymmetric_period_v0() -> dict[str, Any]:
    return period_priority_family_from(
        v17_43_selected_raw_vector(),
        source_state="v17.43_selected_second_event_priority_state",
        priority_owner="period",
        additional_priority_owners=("v0",),
        priority_key="period_v0_profile",
        selection_key="selected_second_asymmetric_period_v0_maximin",
        priority_profiles=PRIORITY_PROFILES,
        cauchy_factors=RADII,
        jacobian_builder=parallel_sbp_physical_jacobian,
    )


def completion_payload() -> dict[str, Any]:
    result = second_asymmetric_period_v0()
    best = result["selected_second_asymmetric_period_v0_maximin"]
    profile = best.get("period_v0_profile", {}) if best else {}
    validation = {
        "v17_43_residual_reproduced": math.isclose(
            result["initial_metrics"]["complete"], 0.932849421101113,
            rel_tol=0, abs_tol=2e-8,
        ),
        "v17_43_event_reproduced": math.isclose(
            result["initial_metrics"]["event"], 0.08500803032792,
            rel_tol=0, abs_tol=2e-8,
        ),
        "v17_43_period_reproduced": math.isclose(
            result["initial_metrics"]["period"], 0.488083886305492,
            rel_tol=0, abs_tol=2e-8,
        ),
        "v17_43_v0_reproduced": math.isclose(
            result["initial_metrics"]["v0"], 0.471851037698269,
            rel_tol=0, abs_tol=2e-8,
        ),
        "source_state_owned": result["source_state"]
        == "v17.43_selected_second_event_priority_state",
        "asymmetric_priority_owned": result.get("priority_owners")
        == ["period", "v0"],
        "bounded_profiles_tested": result.get("priority_profiles_tested")
        == len(PRIORITY_PROFILES),
        "selected_profile_owned": set(profile) == {"period", "v0"},
        "parallel_jacobian_adopted": result.get("assembly_workers") == 8,
        "physical_equations_unchanged": (
            not result["physical_residual_changed"]
            and not result["physical_event_changed"]
        ),
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
        "artifact": "BHSM_aether_n3_fresh_sbp_second_asymmetric_period_v0_v17_44",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": False,
        "fresh_sbp_second_asymmetric_period_v0": result,
        "status": "VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained": (
            "SAME_ACTION_SIX_OWNER_DESCENT_WITH_REPEATED_BOUNDED_ASYMMETRIC_"
            "PERIOD_V0_PRECONDITIONING"
        ),
        "dependency_advanced": "SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation": "PROMOTE_IF_VALIDATED_THEN_REAUDIT_THE_OWNER_SET",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_fresh_sbp_second_asymmetric_period_v0_v17_44.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "v17_43_selected_raw_vector", "second_asymmetric_period_v0",
    "completion_payload", "materialize",
]
