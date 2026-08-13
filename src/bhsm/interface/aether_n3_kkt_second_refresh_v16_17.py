"""Second refreshed-curvature continuation of the N=3 event KKT."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_kkt_refreshed_curvature_v16_16 import (
    refreshed_continuation_from,
)


VERSION = "v16.17"
CLASSIFICATION = "BHSM_N3_KKT_SECOND_REFRESHED_CURVATURE"
FULL_BHSM_COMPLETE = False


def v16_16_final_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_kkt_refreshed_curvature_v16_16.json"
    ).read_text(encoding="utf-8"))
    values = payload["refreshed_continuation"]["final_raw_vector_hex"]
    result = np.asarray([float.fromhex(value) for value in values])
    if result.shape != (376,):
        raise ValueError("v16.16 vector has wrong dimension")
    return result


def completion_payload() -> dict[str, Any]:
    result = refreshed_continuation_from(
        v16_16_final_raw_vector(), iterations=20, trust_radius=1.0e-1
    )
    validation = {
        "nonzero_event_curvature_inserted": (
            result["event_curvature_KKT_contribution_norm"] > 0.0
        ),
        "refreshed_range_failure_detected": (
            result["iterations_accepted"] == 0
            and result["termination"] == "REFRESHED_SR1_STEP_NOT_FOUND"
        ),
        "failed_step_did_not_mutate_state": math.isclose(
            result["final_residual_norm"], result["initial_residual_norm"],
            rel_tol=0.0, abs_tol=1.0e-12,
        ),
        "eta_domain_preserved": result["final_eta_minimum"] > 1.0e-5,
    }
    return {
        "artifact": "BHSM_aether_n3_kkt_second_refresh_v16_17",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "second_refreshed_continuation": result,
        "dependency_advanced": (
            "SECOND_PHYSICAL_JACOBIAN_REFRESH_LOCALIZES_A_NON-DOMAIN_"
            "RANGE_FAILURE_AFTER_THE_SOFT-EVENT_CROSSING"
        ),
        "active_calculation": (
            "PROJECT_THE_EXPOSED_EVENT-MULTIPLIER_BLOCK_EXACTLY_THEN_REFRESH"
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
    path = target / "BHSM_aether_n3_kkt_second_refresh_v16_17.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE",
    "v16_16_final_raw_vector", "completion_payload",
    "deterministic_json", "materialize",
]
