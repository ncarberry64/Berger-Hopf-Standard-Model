"""Explicit multiplier continuation from the promoted v20.83 geometry."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_rayleigh_multiplier_continuation_v20_82 import rayleigh_multiplier_continuation
from bhsm.interface.aether_n3_rayleigh_square_kkt_continuation_v20_83 import v20_83_selected_raw_vector


VERSION = "v20.84"
CLASSIFICATION = "BHSM_N3_RAYLEIGH_EXPLICIT_MULTIPLIER_CONTINUATION"
FULL_BHSM_COMPLETE = False


def v20_84_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_RAYLEIGH_MULTIPLIER_CONTINUATION_V20_84.json"
    ).read_text(encoding="utf-8"))["rayleigh_multiplier_continuation"]
    if not payload["promotion"]["promoted"]:
        raise ValueError("v20.84 has no physically promoted state")
    return np.asarray([float.fromhex(value) for value in payload["candidate"]["raw_vector_hex"]])


def completion_payload() -> dict[str, Any]:
    result = rayleigh_multiplier_continuation(v20_83_selected_raw_vector(), source_label="v20.83")
    validation = {
        "source_v20_83_reproduced": abs(result["source"]["exact_rayleigh_f376_l2"] - 0.787990238928623) < 5.0e-12,
        "exact_merit_reduced": result["candidate"]["exact_reduction"] > 0.0,
        "explicit_multiplier_preserved": result["event_multiplier_remains_explicit_376TH_UNKNOWN"],
        "fresh_child_passes": result["promotion"]["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"] and not result["event_definition_changed"] and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values()) and result["promotion"]["promoted"]
    return {
        "artifact": "BHSM_N3_RAYLEIGH_MULTIPLIER_CONTINUATION_V20_84", "version": VERSION,
        "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "rayleigh_multiplier_continuation": result, "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation, "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_RAYLEIGH_MULTIPLIER_CONTINUATION_V20_84.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v20_84_selected_raw_vector", "completion_payload", "materialize"]
