"""Targeted exact-Hessian continuation from the accepted v16.44 N=3 state."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_post_basin_refresh_v16_25 import refreshed_system_at
from bhsm.interface.aether_n3_refined_filter_continuation_v16_43 import refined_filter_trial_bank
from bhsm.interface.aether_n3_third_physical_refresh_v16_29 import spectral_and_block_audit_from_system

VERSION = "v16.46"
CLASSIFICATION = "BHSM_N3_TARGETED_FILTERED_PHYSICAL_CONTINUATION"
FULL_BHSM_COMPLETE = False
FILTER_RELATIVE_SCALES = (3e-9, 1e-9, 3e-10)
STEP_FRACTIONS = (0.0625, 0.03125, 0.015625)


def v16_44_raw_vector() -> np.ndarray:
    payload = json.loads(Path("artifacts/BHSM_aether_n3_second_refined_filter_continuation_v16_44.json").read_text(encoding="utf-8"))
    values = payload["second_refined_filter_continuation"]["refined_filter_trial_bank"]["best_accepted"]["raw_vector_hex"]
    raw = np.asarray([float.fromhex(value) for value in values])
    if raw.shape != (376,): raise ValueError("v16.44 vector has wrong dimension")
    return raw


def targeted_filter_continuation() -> dict[str, Any]:
    matrix, residual, raw = refreshed_system_at(v16_44_raw_vector())
    return {
        "fresh_physical_audit": spectral_and_block_audit_from_system(matrix, residual, raw),
        "targeted_filter_trial_bank": refined_filter_trial_bank(
            matrix, residual, raw, filter_scales=FILTER_RELATIVE_SCALES,
            step_fractions=STEP_FRACTIONS,
        ),
    }


def completion_payload() -> dict[str, Any]:
    result = targeted_filter_continuation(); audit = result["fresh_physical_audit"]
    bank = result["targeted_filter_trial_bank"]; best = bank["best_accepted"]
    validation = {
        "accepted_v16_44_residual_reproduced": math.isclose(audit["residual_norm"], 6.457090170149505, rel_tol=0.0, abs_tol=2e-9),
        "fresh_physical_jacobian_symmetric": audit["symmetric_relative_residual"] < 1e-14,
        "targeted_grid_probed": bank["trial_count"] == 9,
        "at_least_one_joint_step_accepted": best is not None,
        "complete_residual_reduced": bool(best is not None and best["residual_norm"] < audit["residual_norm"]),
        "eta_domain_preserved": bool(best is not None and best["eta_minimum"] > 1e-5),
        "filter_provenance_preserved": bool(best is not None and best.get("relative_filter_scale_label")),
        "full_precision_state_preserved": bool(best is not None and len(best["raw_vector_hex"]) == 376),
    }
    return {
        "artifact": "BHSM_aether_n3_targeted_filter_continuation_v16_46", "version": VERSION,
        "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "targeted_filter_continuation": result,
        "status": "VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained": "JOINT_STATIONARITY_OF_THE_EXISTING_HOPF_FIBER_AND_COMMON_SCALE_EVENT_BACKGROUND",
        "dependency_advanced": "SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation": "REFRESH_AND_CONTINUE_IF_DESCENT_SURVIVES_OR_REDIRECT_TO_THE_DOMINANT_UPSTREAM_RESIDUAL_ROLE",
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
    path = target / "BHSM_aether_n3_targeted_filter_continuation_v16_46.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path

__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "FILTER_RELATIVE_SCALES", "STEP_FRACTIONS", "v16_44_raw_vector", "targeted_filter_continuation", "completion_payload", "deterministic_json", "materialize"]
