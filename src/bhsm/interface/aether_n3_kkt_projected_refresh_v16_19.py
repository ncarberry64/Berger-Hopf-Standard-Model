"""Fresh common event-KKT curvature at the exactly projected v16.18 state."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_kkt_refreshed_curvature_v16_16 import (
    refreshed_continuation_from,
)


VERSION = "v16.19"
CLASSIFICATION = "BHSM_N3_KKT_PROJECTED_STATE_REFRESH"
FULL_BHSM_COMPLETE = False


def v16_18_projected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_event_multiplier_projection_v16_18.json"
    ).read_text(encoding="utf-8"))
    values = payload["event_multiplier_projection"]["projected_raw_vector_hex"]
    result = np.asarray([float.fromhex(value) for value in values])
    if result.shape != (376,):
        raise ValueError("v16.18 vector has wrong dimension")
    return result


def completion_payload() -> dict[str, Any]:
    result = refreshed_continuation_from(
        v16_18_projected_raw_vector(), iterations=24, trust_radius=5.0e-2
    )
    validation = {
        "projected_event_curvature_inserted": (
            result["event_curvature_KKT_contribution_norm"] > 0.0
        ),
        "eta_domain_preserved": result["final_eta_minimum"] > 1.0e-5,
        "full_precision_state_preserved": len(
            result["final_raw_vector_hex"]
        ) == 376,
    }
    if result["iterations_accepted"] > 0:
        validation["accepted_steps_reduce_complete_residual"] = (
            result["final_residual_norm"] < result["initial_residual_norm"]
        )
    return {
        "artifact": "BHSM_aether_n3_kkt_projected_refresh_v16_19",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "projected_state_refresh": result,
        "dependency_advanced": (
            "FRESH_COMMON_EVENT-KKT_RANGE_TEST_AT_THE_EXACTLY_PROJECTED_STATE"
        ),
        "active_calculation": (
            "CONTINUE_TO_SIMULTANEOUS_STATIONARITY_AND_SOFT-EVENT_CLOSURE_"
            "OR_DECOMPOSE_ANY_REMAINING_REFRESHED_RANGE_DEFECT"
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
        return round(value, 12)
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
    path = target / "BHSM_aether_n3_kkt_projected_refresh_v16_19.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "v16_18_projected_raw_vector", "completion_payload",
    "deterministic_json", "materialize",
]
