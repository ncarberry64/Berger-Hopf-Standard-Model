"""Refined filtered continuation from the accepted v16.42 N=3 state."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_filtered_merit_continuation_v16_41 import (
    filtered_trial_bank_from_system,
)
from bhsm.interface.aether_n3_post_basin_refresh_v16_25 import refreshed_system_at
from bhsm.interface.aether_n3_third_physical_refresh_v16_29 import spectral_and_block_audit_from_system


VERSION = "v16.43"
CLASSIFICATION = "BHSM_N3_REFINED_FILTERED_PHYSICAL_CONTINUATION"
FULL_BHSM_COMPLETE = False
FILTER_RELATIVE_SCALES = (1e-9, 3e-10, 1e-10, 3e-11, 1e-11, 3e-12, 1e-12, 3e-13, 1e-13)
STEP_FRACTIONS = (0.25, 0.125, 0.0625, 0.03125, 0.015625, 0.0078125, 0.00390625)


def v16_42_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_aether_n3_adaptive_spectral_continuation_v16_42.json"
    ).read_text(encoding="utf-8"))
    values = payload["adaptive_spectral_continuation"]["selected_best_accepted"]["raw_vector_hex"]
    raw = np.asarray([float.fromhex(value) for value in values])
    if raw.shape != (376,): raise ValueError("v16.42 vector has wrong dimension")
    return raw


def refined_filter_trial_bank(
    matrix: np.ndarray, residual: np.ndarray, raw: np.ndarray,
    *, filter_scales: tuple[float, ...] = FILTER_RELATIVE_SCALES,
    step_fractions: tuple[float, ...] = STEP_FRACTIONS,
) -> dict[str, Any]:
    import bhsm.interface.aether_n3_filtered_merit_continuation_v16_41 as filter_module
    old_filters, old_fractions = filter_module.FILTER_RELATIVE_SCALES, filter_module.STEP_FRACTIONS
    try:
        filter_module.FILTER_RELATIVE_SCALES = filter_scales
        filter_module.STEP_FRACTIONS = step_fractions
        result = filtered_trial_bank_from_system(matrix, residual, raw)
        for row in result["trials"]:
            row["relative_filter_scale_label"] = f'{row["relative_filter_scale"]:.0e}'
        if result["best_accepted"] is not None:
            result["best_accepted"]["relative_filter_scale_label"] = (
                f'{result["best_accepted"]["relative_filter_scale"]:.0e}'
            )
        return result
    finally:
        filter_module.FILTER_RELATIVE_SCALES = old_filters
        filter_module.STEP_FRACTIONS = old_fractions


def refined_filter_continuation() -> dict[str, Any]:
    matrix, residual, raw = refreshed_system_at(v16_42_raw_vector())
    return {
        "fresh_physical_audit": spectral_and_block_audit_from_system(matrix, residual, raw),
        "refined_filter_trial_bank": refined_filter_trial_bank(matrix, residual, raw),
    }


def completion_payload() -> dict[str, Any]:
    result = refined_filter_continuation(); audit = result["fresh_physical_audit"]
    bank = result["refined_filter_trial_bank"]; best = bank["best_accepted"]
    validation = {
        "accepted_v16_42_residual_reproduced": math.isclose(audit["residual_norm"], 6.500896923864, rel_tol=0.0, abs_tol=2e-9),
        "fresh_physical_jacobian_symmetric": audit["symmetric_relative_residual"] < 1e-14,
        "refined_filter_grid_probed": bank["trial_count"] == len(FILTER_RELATIVE_SCALES) * len(STEP_FRACTIONS),
        "at_least_one_joint_step_accepted": best is not None,
        "complete_residual_reduced": bool(best is not None and best["residual_norm"] < audit["residual_norm"]),
        "eta_domain_preserved": bool(best is not None and best["eta_minimum"] > 1e-5),
        "full_precision_state_preserved": bool(best is not None and len(best["raw_vector_hex"]) == 376),
    }
    return {
        "artifact": "BHSM_aether_n3_refined_filter_continuation_v16_43", "version": VERSION,
        "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "refined_filter_continuation": result,
        "status": "VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained": "COMMON_CONSTRAINED_EVENT_BACKGROUND_FOR_RETURNED_ELECTRON_AND_ELECTROWEAK_MASS_OPERATORS",
        "dependency_advanced": "SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation": "REFRESH_AT_THE_ACCEPTED_REFINED_FILTER_STATE_OR_REDIRECT_TO_THE_DOMINANT_UPSTREAM_BLOCK",
        "validation": validation, "validation_passed": all(validation.values()),
    }


def _canonical(value: Any) -> Any:
    if isinstance(value, np.ndarray): return [_canonical(item) for item in value.tolist()]
    if isinstance(value, np.bool_): return bool(value)
    if isinstance(value, np.integer): return int(value)
    if isinstance(value, np.floating): value = float(value)
    if isinstance(value, float):
        if not math.isfinite(value): raise ValueError("non-finite float")
        return round(value, 15)
    if isinstance(value, Mapping): return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)): return [_canonical(item) for item in value]
    return value


def deterministic_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(_canonical(payload), indent=2, sort_keys=True) + "\n"


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_aether_n3_refined_filter_continuation_v16_43.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "FILTER_RELATIVE_SCALES", "STEP_FRACTIONS", "v16_42_raw_vector", "refined_filter_trial_bank", "refined_filter_continuation", "completion_payload", "deterministic_json", "materialize"]
