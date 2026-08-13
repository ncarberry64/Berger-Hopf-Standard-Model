"""One fresh-Hessian plus multirank nonlinear continuation from v16.37."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_post_basin_multirank_step_v16_26 import (
    multirank_trial_bank_from_system,
)
from bhsm.interface.aether_n3_post_basin_refresh_v16_25 import refreshed_system_at
from bhsm.interface.aether_n3_third_physical_refresh_v16_29 import (
    spectral_and_block_audit_from_system,
)


VERSION = "v16.38"
CLASSIFICATION = "BHSM_N3_COMBINED_FRESH_PHYSICAL_MULTIRANK_CONTINUATION"
FULL_BHSM_COMPLETE = False


def v16_37_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_sixth_multirank_step_v16_37.json"
    ).read_text(encoding="utf-8"))
    values = payload["sixth_multirank_step"]["best_accepted"]["raw_vector_hex"]
    result = np.asarray([float.fromhex(value) for value in values])
    if result.shape != (376,):
        raise ValueError("v16.37 vector has wrong dimension")
    return result


def fresh_continuation_from(raw_vector: np.ndarray) -> dict[str, Any]:
    matrix, residual, raw = refreshed_system_at(raw_vector)
    audit = spectral_and_block_audit_from_system(matrix, residual, raw)
    step = multirank_trial_bank_from_system(matrix, residual, raw)
    return {"fresh_physical_audit": audit, "multirank_step": step}


def combined_fresh_continuation() -> dict[str, Any]:
    return fresh_continuation_from(v16_37_raw_vector())


def completion_payload() -> dict[str, Any]:
    result = combined_fresh_continuation()
    audit = result["fresh_physical_audit"]
    step = result["multirank_step"]
    best = step["best_accepted"]
    validation = {
        "accepted_v16_37_residual_reproduced": math.isclose(
            audit["residual_norm"], 7.542317783457,
            rel_tol=0.0, abs_tol=2.0e-9,
        ),
        "fresh_physical_jacobian_symmetric": audit["symmetric_relative_residual"] < 1.0e-14,
        "all_rank_fractions_probed": step["trial_count"] == 20,
        "at_least_one_joint_step_accepted": best is not None,
        "complete_residual_reduced": bool(
            best is not None and best["residual_norm"] < audit["residual_norm"]
        ),
        "eta_domain_preserved": bool(best is not None and best["eta_minimum"] > 1.0e-5),
        "full_precision_state_preserved": bool(
            best is not None and len(best["raw_vector_hex"]) == 376
        ),
    }
    return {
        "artifact": "BHSM_aether_n3_combined_fresh_continuation_v16_38",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "combined_fresh_continuation": result,
        "status": "VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained": (
            "THE_SHARED_EVENT_BACKGROUND_REQUIRED_BEFORE_A_PERSISTENT_"
            "ELECTRON-LIKE_LR_MASS_AND_THE_BROKEN_GAUGE_KERNEL"
        ),
        "dependency_advanced": "SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation": (
            "REPEAT_FRESH_COMBINED_CONTINUATION_AT_THE_ACCEPTED_STATE_UNTIL_"
            "ALL_N3_BLOCKS_AND_THE_SOFT_EVENT_CLOSE_TOGETHER"
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
    path = target / "BHSM_aether_n3_combined_fresh_continuation_v16_38.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v16_37_raw_vector",
    "fresh_continuation_from", "combined_fresh_continuation", "completion_payload",
    "deterministic_json", "materialize",
]
