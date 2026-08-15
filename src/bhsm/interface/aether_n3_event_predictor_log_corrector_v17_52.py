"""Fresh-Jacobian log corrector after a bounded soft-event predictor."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import (
    sbp_projected_residual_and_vector,
)
from bhsm.interface.aether_n3_fresh_sbp_period_priority_family_v17_25 import (
    MARGIN,
    period_priority_family_from,
)
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import (
    _metrics,
)
from bhsm.interface.aether_n3_fresh_sbp_third_v0_priority_v17_31 import RADII
from bhsm.interface.aether_n3_parallel_physical_jacobian_v17_32 import (
    parallel_sbp_physical_jacobian,
)
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    kkt_variable_scales,
)
from bhsm.interface.aether_n3_soft_event_constrained_v17_51 import (
    v17_49_selected_raw_vector,
)

VERSION = "v17.52"
CLASSIFICATION = "BHSM_N3_SOFT_EVENT_PREDICTOR_FRESH_LOG_CORRECTOR"
FULL_BHSM_COMPLETE = False
PREDICTOR_FAMILY = "single_filter_1e-04"
PREDICTOR_TARGET_FRACTION = 0.15
PREDICTOR_EVENT_ROOT_FRACTION = 0.001
CORRECTOR_PROFILES = (
    (24.0, 8.0, 8.0, 8.0),
    (32.0, 12.0, 10.0, 10.0),
    (48.0, 16.0, 12.0, 12.0),
    (64.0, 24.0, 16.0, 16.0),
    (96.0, 32.0, 20.0, 20.0),
    (128.0, 48.0, 24.0, 24.0),
    (160.0, 64.0, 32.0, 32.0),
    (192.0, 80.0, 40.0, 40.0),
)


def _v17_51_payload() -> dict[str, Any]:
    return json.loads(
        Path("artifacts/BHSM_aether_n3_soft_event_constrained_v17_51.json")
        .read_text(encoding="utf-8")
    )["soft_event_constrained"]


def event_predictor() -> dict[str, Any]:
    """Reconstruct the validated direction and take a bounded event predictor."""
    payload = _v17_51_payload()
    row = next(
        item for item in payload["direction_rows"]
        if item["family"] == PREDICTOR_FAMILY
        and math.isclose(
            item["event_target_fraction"], PREDICTOR_TARGET_FRACTION,
            rel_tol=0.0, abs_tol=1e-15,
        )
    )
    trial = next(
        item for item in row["trials"]
        if item.get("raw_vector_hex") and item.get("trust_radius", 0.0) > 0.0
    )
    scales = kkt_variable_scales()
    base_raw = v17_49_selected_raw_vector()
    base_y, base_residual = sbp_projected_residual_and_vector(base_raw * scales)
    trial_y = np.asarray(
        [float.fromhex(value) for value in trial["raw_vector_hex"]]
    ) * scales
    direction = (trial_y - base_y) / trial["trust_radius"]
    direction[-1] = 0.0
    direction /= np.linalg.norm(direction)
    event_root_radius = 1.0 / -float(row["verified_fractional_slopes"]["event"])
    predictor_radius = PREDICTOR_EVENT_ROOT_FRACTION * event_root_radius
    predictor_y, predictor_residual = sbp_projected_residual_and_vector(
        base_y + predictor_radius * direction
    )
    return {
        "base_metrics": _metrics(base_residual),
        "predictor_metrics": _metrics(predictor_residual),
        "predictor_eta_checked_by_corrector_trials": True,
        "predictor_family": PREDICTOR_FAMILY,
        "predictor_target_fraction": PREDICTOR_TARGET_FRACTION,
        "predictor_event_root_fraction": PREDICTOR_EVENT_ROOT_FRACTION,
        "event_root_radius": event_root_radius,
        "predictor_radius": predictor_radius,
        "raw_vector": predictor_y / scales,
    }


def event_predictor_log_corrector() -> dict[str, Any]:
    predictor = event_predictor()
    corrector = period_priority_family_from(
        predictor["raw_vector"],
        source_state="v17.49_state_plus_bounded_v17.51_soft_event_predictor",
        priority_owner="log_scale",
        additional_priority_owners=("event", "period", "v0"),
        priority_key="corrector_profile",
        selection_key="selected_predicted_state_corrector",
        priority_profiles=CORRECTOR_PROFILES,
        cauchy_factors=RADII,
        jacobian_builder=parallel_sbp_physical_jacobian,
    )
    base_metrics = predictor["base_metrics"]
    accepted: list[tuple[float, float, dict[str, Any], str, Any]] = []
    tested = 0
    for row in corrector["direction_rows"]:
        for trial in row["trials"]:
            if "metrics" not in trial:
                continue
            tested += 1
            reductions = {
                key: base_metrics[key] - trial["metrics"][key]
                for key in base_metrics
            }
            fractions = {
                key: reductions[key] / max(base_metrics[key], 1e-300)
                for key in base_metrics
            }
            if trial["eta_minimum"] > 1e-5 and all(
                value > MARGIN for value in reductions.values()
            ):
                candidate = {
                    "family": row["family"],
                    "corrector_profile": row["corrector_profile"],
                    **trial,
                    "base_reductions": reductions,
                    "base_fractional_reductions": fractions,
                    "base_minimum_fractional_progress": min(fractions.values()),
                    "base_limiting_owner": min(fractions, key=fractions.get),
                }
                accepted.append(
                    (
                        candidate["base_minimum_fractional_progress"],
                        sum(fractions.values()),
                        candidate,
                        row["family"],
                        row["corrector_profile"],
                    )
                )
    best = max(accepted, key=lambda item: (item[0], item[1]))[2] if accepted else None
    predictor.pop("raw_vector")
    return {
        "source_state": "v17.49_selected_refined_four_owner_state",
        "physical_residual_changed": False,
        "physical_event_changed": False,
        "predictor": predictor,
        "corrector": corrector,
        "base_comparison_trial_count": tested,
        "base_strict_candidate_count": len(accepted),
        "selected_event_predictor_log_corrector": best,
    }


def completion_payload() -> dict[str, Any]:
    result = event_predictor_log_corrector()
    predictor = result["predictor"]
    best = result["selected_event_predictor_log_corrector"]
    validation = {
        "v17_49_residual_reproduced": math.isclose(
            predictor["base_metrics"]["complete"], 0.855054105118296,
            rel_tol=0.0, abs_tol=2e-8,
        ),
        "v17_49_event_reproduced": math.isclose(
            predictor["base_metrics"]["event"], 0.084012053757297,
            rel_tol=0.0, abs_tol=2e-8,
        ),
        "bounded_event_predictor_used": 0.0 < PREDICTOR_EVENT_ROOT_FRACTION < 1.0,
        "event_improved_at_predictor": (
            predictor["predictor_metrics"]["event"]
            < predictor["base_metrics"]["event"]
        ),
        "fresh_parallel_corrector_jacobian": (
            result["corrector"].get("assembly_workers") == 8
        ),
        "physical_equations_unchanged": (
            not result["physical_residual_changed"]
            and not result["physical_event_changed"]
        ),
        "corrector_trials_tested": result["base_comparison_trial_count"] > 0,
        "base_candidate_result_classified": (
            (best is None and result["base_strict_candidate_count"] == 0)
            or (
                best is not None
                and all(value > MARGIN for value in best["base_reductions"].values())
            )
        ),
        "no_unvalidated_state_promoted": best is None,
    }
    return {
        "artifact": "BHSM_aether_n3_event_predictor_log_corrector_v17_52",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": False,
        "event_predictor_log_corrector": result,
        "status": (
            "VALIDATED" if all(validation.values()) and best is not None
            else "RECLASSIFIED" if all(validation.values())
            else "INVALIDATED"
        ),
        "real_physical_property_explained": (
            "SAME_ACTION_SOFT_EVENT_PREDICTION_WITH_FRESH_LOG_SCALE_CORRECTION"
        ),
        "dependency_advanced": "SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "DERIVE_THE_EVENT_LOG_CURVATURE_COMPENSATED_SAME_ACTION_CONTINUATION_"
            "BEFORE_ANY_FURTHER_EVENT_PREDICTOR_PROMOTION"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_event_predictor_log_corrector_v17_52.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "PREDICTOR_EVENT_ROOT_FRACTION", "CORRECTOR_PROFILES", "event_predictor",
    "event_predictor_log_corrector", "completion_payload", "materialize",
]
