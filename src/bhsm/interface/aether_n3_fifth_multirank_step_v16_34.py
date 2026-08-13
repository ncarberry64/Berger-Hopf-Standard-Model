"""Fifth multirank continuation from the v16.33 physical KKT refresh."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_fifth_physical_refresh_v16_33 import (
    refreshed_fifth_system,
)
from bhsm.interface.aether_n3_post_basin_multirank_step_v16_26 import (
    multirank_trial_bank_from_system,
)


VERSION = "v16.34"
CLASSIFICATION = "BHSM_N3_FIFTH_FRESH_MULTIRANK_NONLINEAR_STEP"
FULL_BHSM_COMPLETE = False


def fifth_multirank_step() -> dict[str, Any]:
    return multirank_trial_bank_from_system(*refreshed_fifth_system())


def completion_payload() -> dict[str, Any]:
    result = fifth_multirank_step()
    best = result["best_accepted"]
    validation = {
        "all_fresh_rank_fractions_probed": result["trial_count"] == 20,
        "at_least_one_joint_step_accepted": best is not None,
        "complete_residual_reduced": bool(
            best is not None and best["residual_norm"] < result["initial_residual_norm"]
        ),
        "eta_domain_preserved": bool(
            best is not None and best["eta_minimum"] > 1.0e-5
        ),
        "full_precision_state_preserved": bool(
            best is not None and len(best["raw_vector_hex"]) == 376
        ),
    }
    return {
        "artifact": "BHSM_aether_n3_fifth_multirank_step_v16_34",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "fifth_multirank_step": result,
        "status": "VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "dependency_advanced": (
            "CONTINUES_THE_SAME_JOINT_N3_SADDLE_SOLVE_FROM_THE_FRESH_V16_33_"
            "ACTION_PLUS_EVENT_HESSIAN"
        ),
        "active_calculation": (
            "REFRESH_AT_THE_ACCEPTED_STATE_AND_CONTINUE_TO_SIMULTANEOUS_N3_CLOSURE"
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
    path = target / "BHSM_aether_n3_fifth_multirank_step_v16_34.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "fifth_multirank_step",
    "completion_payload", "deterministic_json", "materialize",
]
