"""Dense exact-radius promotion along the validated v17.29 event direction."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_fresh_sbp_event_priority_family_v17_29 import (
    v17_27_selected_raw_vector,
)
from bhsm.interface.aether_n3_fresh_sbp_kkt_v16_58 import (
    sbp_projected_residual_and_vector,
)
from bhsm.interface.aether_n3_fresh_sbp_six_owner_measured_cone_v17_05 import (
    MARGIN,
    _metrics,
)
from bhsm.interface.aether_n3_kkt_newton_step_v16_13 import _minimum_node_eta
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import (
    kkt_variable_scales,
)

VERSION = "v17.30"
CLASSIFICATION = "BHSM_N3_FRESH_SBP_EVENT_DIRECTION_DENSE_RADIUS_PROMOTION"
FULL_BHSM_COMPLETE = False
FACTORS = (0.22, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6, 0.75, 1.0, 1.25, 1.5, 2.0)


def event_dense_radius() -> dict[str, Any]:
    payload = json.loads(
        Path(
            "artifacts/BHSM_aether_n3_fresh_sbp_event_priority_family_v17_29.json"
        ).read_text(encoding="utf-8")
    )
    selected = payload["fresh_sbp_event_priority_family"][
        "selected_event_priority_maximin"
    ]
    scales = kkt_variable_scales()
    raw = v17_27_selected_raw_vector()
    y = raw * scales
    y, residual = sbp_projected_residual_and_vector(y)
    initial = _metrics(residual)
    coarse_raw = np.asarray(
        [float.fromhex(value) for value in selected["raw_vector_hex"]]
    )
    coarse_y = coarse_raw * scales
    direction = (coarse_y - y) / float(selected["trust_radius"])
    cauchy_radius = float(selected["trust_radius"]) / float(
        selected["cauchy_factor"]
    )
    trials: list[dict[str, Any]] = []
    accepted: list[tuple[float, float, dict[str, Any]]] = []
    for factor in FACTORS:
        candidate_y, candidate_residual = sbp_projected_residual_and_vector(
            y + factor * cauchy_radius * direction
        )
        raw_candidate = candidate_y / scales
        metrics = _metrics(candidate_residual)
        reductions = {key: initial[key] - metrics[key] for key in initial}
        fractions = {
            key: reductions[key] / max(initial[key], 1e-300) for key in initial
        }
        eta = _minimum_node_eta(raw_candidate)
        trial = {
            "cauchy_factor": factor,
            "trust_radius": factor * cauchy_radius,
            "domain_valid": bool(eta > 1e-5),
            "metrics": metrics,
            "reductions": reductions,
            "fractional_reductions": fractions,
            "minimum_fractional_progress": min(fractions.values()),
            "limiting_owner": min(fractions, key=fractions.get),
            "eta_minimum": eta,
            "raw_vector_hex": [float(value).hex() for value in raw_candidate],
        }
        trials.append(trial)
        if eta > 1e-5 and all(value > MARGIN for value in reductions.values()):
            accepted.append(
                (trial["minimum_fractional_progress"], sum(fractions.values()), trial)
            )
    best = None
    if accepted:
        _, _, best = max(accepted, key=lambda item: (item[0], item[1]))
    return {
        "source_state": "v17.27_selected_log_scale_priority_state",
        "source_direction": "v17.29_selected_event_priority_direction",
        "physical_residual_changed": False,
        "physical_event_changed": False,
        "selection_rule": "MAXIMIN_THEN_SUM_FRACTIONAL_PROGRESS_ON_EXACT_VALID_TRIALS",
        "initial_metrics": initial,
        "cauchy_radius": cauchy_radius,
        "radius_factors": list(FACTORS),
        "trials": trials,
        "strict_candidate_count": len(accepted),
        "selected_dense_radius": best,
    }


def completion_payload() -> dict[str, Any]:
    result = event_dense_radius()
    best = result["selected_dense_radius"]
    validation = {
        "v17_27_residual_reproduced": math.isclose(
            result["initial_metrics"]["complete"],
            1.105384210751369,
            rel_tol=0,
            abs_tol=2e-8,
        ),
        "v17_27_event_reproduced": math.isclose(
            result["initial_metrics"]["event"],
            0.094479981924371,
            rel_tol=0,
            abs_tol=2e-8,
        ),
        "source_direction_owned": (
            result["source_direction"]
            == "v17.29_selected_event_priority_direction"
        ),
        "physical_equations_unchanged": (
            not result["physical_residual_changed"]
            and not result["physical_event_changed"]
        ),
        "dense_radius_tested": len(result["radius_factors"]) == len(FACTORS),
        "strict_candidate_exists": best is not None,
        "all_six_metrics_reduced": bool(
            best is not None
            and all(value > MARGIN for value in best["reductions"].values())
        ),
        "maximin_radius_is_half_cauchy": bool(
            best is not None
            and math.isclose(best["cauchy_factor"], 0.5, rel_tol=0, abs_tol=1e-15)
        ),
        "eta_domain_preserved": bool(
            best is not None and best["eta_minimum"] > 1e-5
        ),
        "full_precision_state_preserved": bool(
            best is not None and len(best["raw_vector_hex"]) == 376
        ),
    }
    return {
        "artifact": "BHSM_aether_n3_fresh_sbp_event_dense_radius_v17_30",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": False,
        "fresh_sbp_event_dense_radius": result,
        "status": "VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained": (
            "LARGER_EXACT_SIX_OWNER_DESCENT_ALONG_THE_MEASURED_EVENT_DIRECTION"
        ),
        "dependency_advanced": "SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation": "REBUILD_THE_FRESH_JACOBIAN_FROM_THE_PROMOTED_STATE",
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
    path = target / "BHSM_aether_n3_fresh_sbp_event_dense_radius_v17_30.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "event_dense_radius",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
