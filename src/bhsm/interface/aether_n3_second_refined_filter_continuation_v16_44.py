"""Second refined filtered continuation from the accepted v16.43 state."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

from bhsm.interface.aether_n3_post_basin_refresh_v16_25 import refreshed_system_at
from bhsm.interface.aether_n3_refined_filter_continuation_v16_43 import refined_filter_trial_bank
from bhsm.interface.aether_n3_third_physical_refresh_v16_29 import spectral_and_block_audit_from_system

VERSION = "v16.44"
CLASSIFICATION = "BHSM_N3_SECOND_REFINED_FILTERED_PHYSICAL_CONTINUATION"
FULL_BHSM_COMPLETE = False


def v16_43_raw_vector() -> np.ndarray:
    payload = json.loads(Path("artifacts/BHSM_aether_n3_refined_filter_continuation_v16_43.json").read_text(encoding="utf-8"))
    values = payload["refined_filter_continuation"]["refined_filter_trial_bank"]["best_accepted"]["raw_vector_hex"]
    raw = np.asarray([float.fromhex(value) for value in values])
    if raw.shape != (376,): raise ValueError("v16.43 vector has wrong dimension")
    return raw


def second_refined_continuation() -> dict[str, Any]:
    matrix, residual, raw = refreshed_system_at(v16_43_raw_vector())
    return {
        "fresh_physical_audit": spectral_and_block_audit_from_system(matrix, residual, raw),
        "refined_filter_trial_bank": refined_filter_trial_bank(matrix, residual, raw),
    }


def completion_payload() -> dict[str, Any]:
    result = second_refined_continuation(); audit = result["fresh_physical_audit"]
    bank = result["refined_filter_trial_bank"]; best = bank["best_accepted"]
    validation = {
        "accepted_v16_43_residual_reproduced": math.isclose(audit["residual_norm"], 6.482403137748, rel_tol=0.0, abs_tol=2e-9),
        "fresh_physical_jacobian_symmetric": audit["symmetric_relative_residual"] < 1e-14,
        "filter_provenance_preserved": bool(best is not None and best.get("relative_filter_scale_label")),
        "at_least_one_joint_step_accepted": best is not None,
        "complete_residual_reduced": bool(best is not None and best["residual_norm"] < audit["residual_norm"]),
        "eta_domain_preserved": bool(best is not None and best["eta_minimum"] > 1e-5),
        "full_precision_state_preserved": bool(best is not None and len(best["raw_vector_hex"]) == 376),
    }
    return {
        "artifact": "BHSM_aether_n3_second_refined_filter_continuation_v16_44", "version": VERSION,
        "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "second_refined_filter_continuation": result,
        "status": "VALIDATED" if all(validation.values()) else "RECLASSIFIED",
        "real_physical_property_explained": "TERMINAL_HOPF_ANISOTROPY_AND_FIBER_LOCALIZATION_OF_THE_COMMON_EVENT_BACKGROUND",
        "dependency_advanced": "SIMULTANEOUS_N3_PHYSICAL_EVENT_SADDLE_CLOSURE",
        "active_calculation": "CLASSIFY_THE_POST_STEP_RESIDUAL_CONCENTRATION_AND_CONTINUE_OR_REDIRECT_TO_ITS_UPSTREAM_OBJECT",
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
    path = target / "BHSM_aether_n3_second_refined_filter_continuation_v16_44.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path

__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v16_43_raw_vector", "second_refined_continuation", "completion_payload", "deterministic_json", "materialize"]
