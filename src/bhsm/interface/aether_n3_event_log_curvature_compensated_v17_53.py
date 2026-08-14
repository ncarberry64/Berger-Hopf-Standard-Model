"""Two-direction event/log curvature compensation from the v17.49 state."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import sbp_projected_residual_and_vector
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import MARGIN, _metrics
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import kkt_variable_scales
from bhsm.interface.aether_n3_soft_event_constrained_v17_51 import v17_49_selected_raw_vector

VERSION = "v17.53"
CLASSIFICATION = "BHSM_N3_SOFT_EVENT_LOG_CURVATURE_COMPENSATED_CONTINUATION"
FULL_BHSM_COMPLETE = False
EVENT_FAMILY = "single_filter_1e-04"
EVENT_TARGET = 0.15
COMPENSATOR_FAMILY = "single_filter_1e-03"
COMPENSATOR_TARGET = 0.05
EVENT_ROOT_FRACTIONS = (0.0002, 0.00025, 0.0003, 0.00035, 0.0004, 0.0005, 0.0006)
COMPENSATOR_RADII = (0.0, 1e-6, 2e-6, 3e-6, 4e-6, 5e-6, 6e-6, 7e-6, 8e-6, 9e-6, 1e-5)


def _payload() -> dict[str, Any]:
    return json.loads(Path(
        "artifacts/BHSM_aether_n3_soft_event_constrained_v17_51.json"
    ).read_text(encoding="utf-8"))["soft_event_constrained"]


def _direction(
    payload: dict[str, Any], y: np.ndarray, scales: np.ndarray,
    family: str, target: float,
) -> tuple[np.ndarray, dict[str, Any]]:
    row = next(
        item for item in payload["direction_rows"]
        if item["family"] == family
        and math.isclose(item["event_target_fraction"], target, rel_tol=0, abs_tol=1e-15)
    )
    trial = next(
        item for item in row["trials"]
        if item.get("raw_vector_hex") and item.get("trust_radius", 0.0) > 0.0
    )
    candidate = np.asarray([float.fromhex(value) for value in trial["raw_vector_hex"]]) * scales
    direction = (candidate - y) / trial["trust_radius"]
    direction[-1] = 0.0
    direction /= np.linalg.norm(direction)
    return direction, row


def event_log_curvature_compensated() -> dict[str, Any]:
    payload = _payload()
    scales = kkt_variable_scales()
    raw = v17_49_selected_raw_vector()
    y, residual = sbp_projected_residual_and_vector(raw * scales)
    initial = _metrics(residual)
    event_direction, event_row = _direction(payload, y, scales, EVENT_FAMILY, EVENT_TARGET)
    compensator, compensator_row = _direction(
        payload, y, scales, COMPENSATOR_FAMILY, COMPENSATOR_TARGET
    )
    event_root_radius = 1.0 / -float(event_row["verified_fractional_slopes"]["event"])
    trials: list[dict[str, Any]] = []
    accepted: list[tuple[float, float, dict[str, Any]]] = []
    for event_fraction in EVENT_ROOT_FRACTIONS:
        event_radius = event_fraction * event_root_radius
        for compensator_radius in COMPENSATOR_RADII:
            try:
                candidate_y, candidate_residual = sbp_projected_residual_and_vector(
                    y + event_radius * event_direction + compensator_radius * compensator
                )
                raw_candidate = candidate_y / scales
                eta = _minimum_node_eta(raw_candidate)
                metrics = _metrics(candidate_residual)
                reductions = {key: initial[key] - metrics[key] for key in initial}
                fractions = {
                    key: reductions[key] / max(initial[key], 1e-300) for key in initial
                }
                trial = {
                    "event_root_fraction": event_fraction,
                    "event_radius": event_radius,
                    "compensator_radius": compensator_radius,
                    "domain_valid": bool(eta > 1e-5),
                    "eta_minimum": eta,
                    "metrics": metrics,
                    "reductions": reductions,
                    "fractional_reductions": fractions,
                    "minimum_fractional_progress": min(fractions.values()),
                    "limiting_owner": min(fractions, key=fractions.get),
                    "raw_vector_hex": [float(value).hex() for value in raw_candidate],
                }
                trials.append(trial)
                if eta > 1e-5 and all(value > MARGIN for value in reductions.values()):
                    accepted.append((min(fractions.values()), sum(fractions.values()), trial))
            except (FloatingPointError, ValueError, np.linalg.LinAlgError) as exc:
                trials.append({
                    "event_root_fraction": event_fraction,
                    "compensator_radius": compensator_radius,
                    "domain_valid": False,
                    "exception": type(exc).__name__,
                })
    best = max(accepted, key=lambda item: (item[0], item[1]))[2] if accepted else None
    return {
        "source_state": "v17.49_selected_refined_four_owner_state",
        "physical_residual_changed": False,
        "physical_event_changed": False,
        "event_direction": {"family": EVENT_FAMILY, "target_fraction": EVENT_TARGET},
        "compensator_direction": {
            "family": COMPENSATOR_FAMILY, "target_fraction": COMPENSATOR_TARGET,
        },
        "event_root_radius": event_root_radius,
        "initial_metrics": initial,
        "trial_count": len(trials),
        "strict_candidate_count": len(accepted),
        "trials": trials,
        "selected_event_log_curvature_compensated": best,
    }


def completion_payload() -> dict[str, Any]:
    result = event_log_curvature_compensated()
    best = result["selected_event_log_curvature_compensated"]
    validation = {
        "v17_49_residual_reproduced": math.isclose(
            result["initial_metrics"]["complete"], 0.855054105118296,
            rel_tol=0, abs_tol=2e-8,
        ),
        "v17_49_event_reproduced": math.isclose(
            result["initial_metrics"]["event"], 0.084012053757297,
            rel_tol=0, abs_tol=2e-8,
        ),
        "bounded_two_direction_grid_tested": result["trial_count"] == 77,
        "physical_equations_unchanged": (
            not result["physical_residual_changed"] and not result["physical_event_changed"]
        ),
        "strict_candidate_exists": best is not None,
        "all_six_metrics_reduced": bool(
            best is not None and all(value > MARGIN for value in best["reductions"].values())
        ),
        "v17_51_minimum_progress_exceeded": bool(
            best is not None and best["minimum_fractional_progress"] > 0.000102509241248
        ),
        "eta_domain_preserved": bool(best is not None and best["eta_minimum"] > 1e-5),
        "full_precision_state_preserved": bool(
            best is not None and len(best["raw_vector_hex"]) == 376
        ),
    }
    return {
        "artifact": "BHSM_aether_n3_event_log_curvature_compensated_v17_53",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": False,
        "event_log_curvature_compensated": result,
        "status": "VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained": (
            "SAME_ACTION_TWO_DIRECTION_SOFT_EVENT_LOG_CURVATURE_COMPENSATION"
        ),
        "dependency_advanced": "SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "PROMOTE_IF_VALIDATED_THEN_REAUDIT_THE_SOFT_BRANCH_AND_CONTRACTION"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_event_log_curvature_compensated_v17_53.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "EVENT_ROOT_FRACTIONS",
    "COMPENSATOR_RADII", "event_log_curvature_compensated", "completion_payload",
    "materialize",
]
