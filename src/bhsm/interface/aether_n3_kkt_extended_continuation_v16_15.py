"""Extended physical continuation of the N=3 replacement event KKT."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_kkt_sr1_continuation_v16_14 import (
    sr1_continuation,
)


VERSION = "v16.15"
CLASSIFICATION = "BHSM_N3_REPLACEMENT_KKT_EXTENDED_CONTINUATION"
FULL_BHSM_COMPLETE = False


def completion_payload() -> dict[str, Any]:
    result = sr1_continuation(iterations=60, trust_radius=1.0e-1)
    validation = {
        "continuation_materially_extended": result["iterations_accepted"] > 12,
        "complete_residual_reduced": (
            result["final_residual_norm"] < result["initial_residual_norm"]
        ),
        "soft_event_approached": abs(result["final_event_residual"]) < 0.1361,
        "eta_domain_preserved": result["final_eta_minimum"] > 1.0e-5,
        "state_preserved_at_full_float_precision": len(
            result["final_raw_vector_hex"]
        ) == 376,
    }
    return {
        "artifact": "BHSM_aether_n3_kkt_extended_continuation_v16_15",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "continuation": result,
        "dependency_advanced": (
            "EXTENDED_NONLINEAR_APPROACH_TO_THE_STATIONARY_N3_COMMON_"
            "REPLACEMENT_SOFT_EVENT"
        ),
        "active_calculation": (
            "REFRESH_THE_JACOBIAN_AT_THE_EXTENDED_STATE_OR_PROMOTE_THE_"
            "CONVERGED_EVENT_IF_THE_COMPLETE_RESIDUAL_CLOSES"
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
    path = target / "BHSM_aether_n3_kkt_extended_continuation_v16_15.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "completion_payload", "deterministic_json", "materialize",
]
