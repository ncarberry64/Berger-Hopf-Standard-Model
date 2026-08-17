"""Audit the demonstrated 12-vector Krylov proposal restriction at v20.85."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import deterministic_json
from bhsm.interface.aether_n3_rayleigh_square_kkt_continuation_v20_85 import v20_85_selected_raw_vector
from bhsm.interface.aether_n3_rayleigh_square_kkt_proposal_v20_81 import rayleigh_square_kkt_proposal


VERSION = "v20.86"
CLASSIFICATION = "BHSM_N3_RAYLEIGH_KRYLOV_RESTRICTION_AUDIT"
FULL_BHSM_COMPLETE = False


def v20_86_selected_raw_vector() -> np.ndarray:
    payload = json.loads(Path(
        "artifacts/BHSM_N3_RAYLEIGH_KRYLOV_RESTRICTION_AUDIT_V20_86.json"
    ).read_text(encoding="utf-8"))["rayleigh_krylov_restriction_audit"]
    if not payload["promotion"]["promoted"]:
        raise ValueError("v20.86 has no physically promoted state")
    return np.asarray([float.fromhex(value) for value in payload["exact_line_search"]["best"]["raw_vector_hex"]])


def completion_payload() -> dict[str, Any]:
    result = rayleigh_square_kkt_proposal(
        v20_85_selected_raw_vector(), source_label="v20.85", krylov_restart=24,
        child_fallback_limit=4,
    )
    best = result["exact_line_search"]["best"]
    result["restriction_audit"] = {
        "prior_restart": 12, "audited_restart": 24,
        "prior_callback_relative_residual": 0.997768570800663,
        "physical_constraint_added": False,
        "interpretation": "NUMERICAL_PROPOSAL_CONTROL_ONLY",
    }
    validation = {
        "source_v20_85_reproduced": abs(result["source"]["exact_rayleigh_f376_l2"] - 0.787515112996569) < 5.0e-12,
        "response_resolved": result["response"]["resolved"],
        "restriction_actually_relaxed": result["response"]["krylov_restart_numerical_control"] == 24,
        "exact_rows_decide": result["exact_line_search"]["original_unweighted_376_rows_authoritative"],
        "candidate_reduces_merit": best is None or best["exact_reduction"] > 0.0,
        "promotion_requires_child": not result["promotion"]["promoted"] or result["promotion"]["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"] and not result["event_definition_changed"] and not result["acceptance_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_RAYLEIGH_KRYLOV_RESTRICTION_AUDIT_V20_86", "version": VERSION,
        "classification": CLASSIFICATION, "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "rayleigh_krylov_restriction_audit": result, "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation, "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory); target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_RAYLEIGH_KRYLOV_RESTRICTION_AUDIT_V20_86.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "v20_86_selected_raw_vector", "completion_payload", "materialize"]
