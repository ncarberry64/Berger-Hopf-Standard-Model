"""Asymmetric period/v0 continuation from the validated v17.41 state."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_fresh_sbp_period_priority_family_v17_25 import (
    MARGIN,
    period_priority_family_from,
)
from bhsm.interface.aether_n3_fresh_sbp_third_v0_priority_v17_31 import RADII
from bhsm.interface.aether_n3_parallel_physical_jacobian_v17_32 import (
    parallel_sbp_physical_jacobian,
)

VERSION = "v17.42"
CLASSIFICATION = "BHSM_N3_FRESH_SBP_ASYMMETRIC_PERIOD_V0_PRIORITY_MEASURED_TANGENT_FAMILY"
FULL_BHSM_COMPLETE = False
PRIORITY_PROFILES = (
    (1.0, 1.0),
    (1.25, 1.5),
    (1.5, 2.0),
    (2.0, 3.0),
    (2.0, 4.0),
    (3.0, 6.0),
    (3.0, 8.0),
    (4.0, 8.0),
)


def v17_41_selected_raw_vector() -> np.ndarray:
    payload = json.loads(
        Path(
            "artifacts/BHSM_aether_n3_fresh_sbp_coupled_period_v0_priority_v17_41.json"
        ).read_text(encoding="utf-8")
    )
    values = payload["fresh_sbp_coupled_period_v0_priority"][
        "selected_coupled_period_v0_priority_maximin"
    ]["raw_vector_hex"]
    raw = np.asarray([float.fromhex(value) for value in values])
    if raw.shape != (376,):
        raise ValueError("v17.41 selected vector has wrong dimension")
    return raw


def asymmetric_period_v0_priority() -> dict[str, Any]:
    return period_priority_family_from(
        v17_41_selected_raw_vector(),
        source_state="v17.41_selected_coupled_period_v0_priority_state",
        priority_owner="period",
        additional_priority_owners=("v0",),
        priority_key="period_v0_profile",
        selection_key="selected_asymmetric_period_v0_priority_maximin",
        priority_profiles=PRIORITY_PROFILES,
        cauchy_factors=RADII,
        jacobian_builder=parallel_sbp_physical_jacobian,
    )


def completion_payload() -> dict[str, Any]:
    result = asymmetric_period_v0_priority()
    best = result["selected_asymmetric_period_v0_priority_maximin"]
    selected_profile = best.get("period_v0_profile", {}) if best else {}
    validation = {
        "v17_41_residual_reproduced": math.isclose(
            result["initial_metrics"]["complete"],
            0.944407418152609,
            rel_tol=0,
            abs_tol=2e-8,
        ),
        "v17_41_event_reproduced": math.isclose(
            result["initial_metrics"]["event"],
            0.085357856454871,
            rel_tol=0,
            abs_tol=2e-8,
        ),
        "v17_41_period_reproduced": math.isclose(
            result["initial_metrics"]["period"],
            0.492136298394001,
            rel_tol=0,
            abs_tol=2e-8,
        ),
        "v17_41_v0_reproduced": math.isclose(
            result["initial_metrics"]["v0"],
            0.475151972815575,
            rel_tol=0,
            abs_tol=2e-8,
        ),
        "source_state_owned": (
            result["source_state"]
            == "v17.41_selected_coupled_period_v0_priority_state"
        ),
        "asymmetric_priority_owned": result.get("priority_owners")
        == ["period", "v0"],
        "bounded_profiles_tested": (
            result.get("priority_profiles_tested") == len(PRIORITY_PROFILES)
        ),
        "selected_profile_is_asymmetric_or_baseline": (
            set(selected_profile) == {"period", "v0"}
        ),
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
        "artifact": "BHSM_aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": False,
        "fresh_sbp_asymmetric_period_v0_priority": result,
        "status": "VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained": (
            "SAME_ACTION_SIX_OWNER_DESCENT_WITH_BOUNDED_ASYMMETRIC_PERIOD_V0_"
            "NUMERICAL_PRECONDITIONING"
        ),
        "dependency_advanced": "SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "PROMOTE_ONLY_IF_THE_ASYMMETRIC_CORRECTION_IMPROVES_THE_V0_"
            "BOTTLENECK_WITH_ORIGINAL_ACCEPTANCE"
        ),
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
    path = target / "BHSM_aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "PRIORITY_PROFILES",
    "v17_41_selected_raw_vector",
    "asymmetric_period_v0_priority",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
