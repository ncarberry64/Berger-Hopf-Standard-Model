"""Sixth fresh physical KKT audit after the accepted v16.34 step."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_post_basin_refresh_v16_25 import refreshed_system_at
from bhsm.interface.aether_n3_third_physical_refresh_v16_29 import (
    spectral_and_block_audit_from_system,
)


VERSION = "v16.35"
CLASSIFICATION = "BHSM_N3_SIXTH_FRESH_PHYSICAL_KKT"
FULL_BHSM_COMPLETE = False


def v16_34_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_fifth_multirank_step_v16_34.json"
    ).read_text(encoding="utf-8"))
    values = payload["fifth_multirank_step"]["best_accepted"]["raw_vector_hex"]
    result = np.asarray([float.fromhex(value) for value in values])
    if result.shape != (376,):
        raise ValueError("v16.34 vector has wrong dimension")
    return result


def refreshed_sixth_system() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return refreshed_system_at(v16_34_raw_vector())


def completion_payload() -> dict[str, Any]:
    result = spectral_and_block_audit_from_system(*refreshed_sixth_system())
    validation = {
        "accepted_v16_34_residual_reproduced": math.isclose(
            result["residual_norm"], 8.492887411566,
            rel_tol=0.0, abs_tol=2.0e-9,
        ),
        "soft_event_remains_near_zero": abs(result["event_residual"]) < 0.1,
        "fresh_physical_jacobian_is_symmetric": (
            result["symmetric_relative_residual"] < 1.0e-14
        ),
    }
    return {
        "artifact": "BHSM_aether_n3_sixth_physical_refresh_v16_35",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "sixth_refresh": result,
        "status": "ACTIVE",
        "dependency_advanced": (
            "REFRESHES_AND_BLOCK_DECOMPOSES_THE_V16_34_STATE_AFTER_THE_"
            "OBSERVED_SHRINKING_LOCAL_TRUST_SCALE"
        ),
        "active_calculation": (
            "CLASSIFY_THE_NEW_LOCAL_RANGE_AND_CONTINUE_OR_REDIRECT_TO_ITS_"
            "DOMINANT_UPSTREAM_BLOCK"
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
    path = target / "BHSM_aether_n3_sixth_physical_refresh_v16_35.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v16_34_raw_vector",
    "refreshed_sixth_system", "completion_payload", "deterministic_json", "materialize",
]
