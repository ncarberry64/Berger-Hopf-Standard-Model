"""Adaptive spectral continuation from the accepted v16.41 N=3 state."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_filtered_merit_continuation_v16_41 import (
    filtered_trial_bank_from_system,
)
from bhsm.interface.aether_n3_post_basin_multirank_step_v16_26 import (
    multirank_trial_bank_from_system,
)
from bhsm.interface.aether_n3_post_basin_refresh_v16_25 import refreshed_system_at
from bhsm.interface.aether_n3_third_physical_refresh_v16_29 import (
    spectral_and_block_audit_from_system,
)


VERSION = "v16.42"
CLASSIFICATION = "BHSM_N3_ADAPTIVE_SPECTRAL_PHYSICAL_CONTINUATION"
FULL_BHSM_COMPLETE = False


def v16_41_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_filtered_merit_continuation_v16_41.json"
    ).read_text(encoding="utf-8"))
    values = payload["filtered_continuation"]["filtered_trial_bank"]["best_accepted"]["raw_vector_hex"]
    result = np.asarray([float.fromhex(value) for value in values])
    if result.shape != (376,):
        raise ValueError("v16.41 vector has wrong dimension")
    return result


def adaptive_spectral_continuation() -> dict[str, Any]:
    matrix, residual, raw = refreshed_system_at(v16_41_raw_vector())
    audit = spectral_and_block_audit_from_system(matrix, residual, raw)
    hard = multirank_trial_bank_from_system(matrix, residual, raw)
    filtered = filtered_trial_bank_from_system(matrix, residual, raw)
    candidates = []
    if hard["best_accepted"] is not None:
        candidates.append((hard["best_accepted"]["residual_norm"], "hard_multirank", hard["best_accepted"]))
    if filtered["best_accepted"] is not None:
        candidates.append((filtered["best_accepted"]["residual_norm"], "continuous_filter", filtered["best_accepted"]))
    selected = None
    if candidates:
        _, method, row = min(candidates, key=lambda item: item[0])
        selected = {"method": method, **row}
    return {
        "fresh_physical_audit": audit,
        "hard_multirank_trial_bank": hard,
        "filtered_trial_bank": filtered,
        "selected_best_accepted": selected,
    }


def completion_payload() -> dict[str, Any]:
    result = adaptive_spectral_continuation()
    audit = result["fresh_physical_audit"]
    selected = result["selected_best_accepted"]
    validation = {
        "accepted_v16_41_residual_reproduced": math.isclose(
            audit["residual_norm"], 6.514658743303, rel_tol=0.0, abs_tol=2.0e-9
        ),
        "fresh_physical_jacobian_symmetric": audit["symmetric_relative_residual"] < 1.0e-14,
        "both_spectral_regularizations_probed": (
            result["hard_multirank_trial_bank"]["trial_count"] == 20
            and result["filtered_trial_bank"]["trial_count"] == 28
        ),
        "at_least_one_joint_step_accepted": selected is not None,
        "complete_residual_reduced": bool(
            selected is not None and selected["residual_norm"] < audit["residual_norm"]
        ),
        "eta_domain_preserved": bool(selected is not None and selected["eta_minimum"] > 1.0e-5),
        "full_precision_state_preserved": bool(
            selected is not None and len(selected["raw_vector_hex"]) == 376
        ),
    }
    return {
        "artifact": "BHSM_aether_n3_adaptive_spectral_continuation_v16_42",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "adaptive_spectral_continuation": result,
        "status": "VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained": (
            "THE_COMMON_EVENT_BACKGROUND_REQUIRED_BY_BOTH_RETURNED_ELECTRON_LR_MASS_"
            "AND_BROKEN_ELECTROWEAK_GAUGE_OPERATORS"
        ),
        "dependency_advanced": "SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation": "REFRESH_AT_THE_SELECTED_STATE_AND_CONTINUE_EXACT_JOINT_CLOSURE",
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, np.ndarray): return [_canonical(item) for item in value.tolist()]
    if isinstance(value, np.bool_): return bool(value)
    if isinstance(value, np.integer): return int(value)
    if isinstance(value, np.floating): value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value): raise ValueError("non-finite float")
        return round(value, 12)
    if isinstance(value, Mapping): return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)): return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_adaptive_spectral_continuation_v16_42.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v16_41_raw_vector",
    "adaptive_spectral_continuation", "completion_payload", "deterministic_json", "materialize",
]
