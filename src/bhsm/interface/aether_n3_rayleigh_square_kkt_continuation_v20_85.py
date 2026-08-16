"""Continue the validated Rayleigh square-KKT solve from v20.84."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_rayleigh_multiplier_continuation_v20_84 import v20_84_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_square_kkt_proposal_v20_81 import rayleigh_square_kkt_proposal


VERSION = "v20.85"
CLASSIFICATION = "BHSM_N3_RAYLEIGH_SQUARE_KKT_CONTINUATION"
FULL_BHSM_COMPLETE = False


def v20_85_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_RAYLEIGH_SQUARE_KKT_CONTINUATION_V20_85.json"
    ).read_text(encoding="utf-8"))["rayleigh_square_kkt_continuation"]
    if not payload["promotion"]["promoted"]:
        raise ValueError("v20.85 has no physically promoted state")
    return np.asarray([float.fromhex(value) for value in payload["exact_line_search"]["best"]["raw_vector_hex"]])


def completion_payload() -> dict[str, Any]:
    result = rayleigh_square_kkt_proposal(v20_84_selected_raw_vector(), source_label="v20.84")
    best = result["exact_line_search"]["best"]
    validation = {
        "source_v20_84_reproduced": abs(result["source"]["exact_rayleigh_f376_l2"] - 0.787884419734758) < 5.0e-12,
        "response_resolved": result["response"]["resolved"],
        "exact_rows_decide": result["exact_line_search"]["original_unweighted_376_rows_authoritative"],
        "candidate_reduces_merit": best is None or best["exact_reduction"] > 0.0,
        "promotion_requires_child": not result["promotion"]["promoted"] or result["promotion"]["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"] and not result["event_definition_changed"] and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_RAYLEIGH_SQUARE_KKT_CONTINUATION_V20_85", "version": VERSION,
        "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "rayleigh_square_kkt_continuation": result, "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation, "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_RAYLEIGH_SQUARE_KKT_CONTINUATION_V20_85.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v20_85_selected_raw_vector", "completion_payload", "materialize"]
