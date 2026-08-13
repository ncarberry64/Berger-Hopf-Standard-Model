"""Resolve and accept the nonlinear rank-aware descent basin from v16.23."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_rank_aware_trust_step_v16_23 import (
    rank_aware_trial_bank,
)


VERSION = "v16.24"
CLASSIFICATION = "BHSM_N3_RANK_AWARE_NONLINEAR_BASIN_STEP"
FULL_BHSM_COMPLETE = False
SEARCH_RADII = (320.0, 352.0, 368.0, 384.0, 400.0, 416.0, 432.0, 448.0)


def resolved_basin_step() -> dict[str, Any]:
    return rank_aware_trial_bank(
        relative_cutoffs=(1.0e-14,),
        trust_radii=SEARCH_RADII,
    )


def completion_payload() -> dict[str, Any]:
    result = resolved_basin_step()
    best = result["best_accepted"]
    validation = {
        "rank_184_direction_used": bool(best is not None and best["rank"] == 184),
        "nonlinear_basin_bracketed": bool(
            best is not None
            and best["trust_radius"] == 400.0
            and result["trials"][0]["residual_norm"] > best["residual_norm"]
            and result["trials"][-1]["residual_norm"] > best["residual_norm"]
        ),
        "material_residual_reduction": bool(
            best is not None
            and best["residual_norm"] < 0.75 * result["initial_residual_norm"]
        ),
        "eta_domain_preserved": bool(
            best is not None and best["eta_minimum"] > 1.0e-5
        ),
        "full_precision_state_preserved": bool(
            best is not None and len(best["raw_vector_hex"]) == 376
        ),
    }
    return {
        "artifact": "BHSM_aether_n3_rank_aware_basin_step_v16_24",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "basin_step": result,
        "status": "VALIDATED",
        "dependency_advanced": (
            "CONVERTS_THE_V16_21_CASE_1_RANGE_DIAGNOSIS_INTO_A_MATERIAL_"
            "NONLINEAR_DESCENT_STEP_OF_THE_UNCHANGED_ANCHORED_N3_EVENT_KKT"
        ),
        "active_calculation": (
            "REFRESH_THE_COMPLETE_PHYSICAL_KKT_JACOBIAN_AT_THE_ACCEPTED_"
            "RANK_AWARE_BASIN_STATE_AND_CONTINUE_TO_THE_COMMON_SADDLE"
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
    path = target / "BHSM_aether_n3_rank_aware_basin_step_v16_24.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = [
    "VERSION",
    "CLASSIFICATION",
    "FULL_BHSM_COMPLETE",
    "SEARCH_RADII",
    "resolved_basin_step",
    "completion_payload",
    "deterministic_json",
    "materialize",
]
