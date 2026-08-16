"""Prospectively test one action-owned right preconditioner for exact F376 Jv."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from bhsm.interface.aether_n3_exact_matrix_free_response_proposal_v21_14 import (
    completion_payload as base_payload,
)
from bhsm.interface.aether_n3_fresh_sbp_asymmetric_period_v0_priority_v17_42 import (
    deterministic_json,
)


VERSION = "v21.16"
CLASSIFICATION = "BHSM_N3_EXACT_MATRIX_FREE_ACTION_PRECONDITIONED_PROPOSAL"
FULL_BHSM_COMPLETE = False


def completion_payload() -> dict[str, Any]:
    base = base_payload(restart=30, right_precondition=True)
    result = base["exact_matrix_free_response_proposal"]
    audit = result["matrix_free_response"]["response_audit"]
    preconditioner = result["matrix_free_response"]["right_response_preconditioner"]
    best = result["prospective_exact_search"]["best"]
    validation = {
        "base_validation_passed": base["validation_passed"],
        "action_owned_right_preconditioner_used": preconditioner["used"],
        "right_map_invertible": preconditioner[
            "root_equivalent_invertible_right_coordinate_map"
        ],
        "no_left_residual_scaling": not preconditioner["left_residual_scaling_added"],
        "exact_response_step_stable": audit["half_vs_reference_relative"] < 1.0e-3
        and audit["double_vs_reference_relative"] < 1.0e-3,
        "exact_rows_decide": result["prospective_exact_search"][
            "original_unweighted_rayleigh_f376_authoritative"
        ],
        "candidate_reduces_merit": best is None or best["exact_reduction"] > 0.0,
        "promotion_requires_child": not result["promotion"]["promoted"]
        or result["promotion"]["child"]["all_pass"],
        "same_physics": not result["physical_equations_changed"]
        and not result["event_definition_changed"]
        and not result["complete_child_gate_changed"],
    }
    passed = all(validation.values())
    return {
        "artifact": "BHSM_N3_EXACT_MATRIX_FREE_ACTION_PRECONDITIONED_PROPOSAL_V21_16",
        "version": VERSION,
        "classification": CLASSIFICATION,
        "FULL_BHSM_COMPLETE": FULL_BHSM_COMPLETE,
        "exact_matrix_free_action_preconditioned_proposal": result,
        "status": "VALIDATED" if passed else "INVALIDATED",
        "validation": validation,
        "validation_passed": passed,
    }


def materialize(directory: str | Path) -> Path:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    path = target / "BHSM_N3_EXACT_MATRIX_FREE_ACTION_PRECONDITIONED_PROPOSAL_V21_16.json"
    path.write_text(deterministic_json(completion_payload()), encoding="utf-8")
    return path


__all__ = ["VERSION", "CLASSIFICATION", "FULL_BHSM_COMPLETE", "completion_payload", "materialize"]
