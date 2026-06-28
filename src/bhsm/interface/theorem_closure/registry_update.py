"""Generate non-destructive prediction-registry update proposals."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..predictions import default_prediction_registry
from .closure_report import build_theorem_closure_report
from .proof_gates import proof_gate_summary


def build_cp_o_int_registry_update(repository: str | Path | None = None) -> dict[str, Any]:
    """Propose CP-specific statuses without mutating the production registry."""

    from .cp_o_int_report import build_cp_o_int_report

    report = build_cp_o_int_report(repository=repository)
    registry = default_prediction_registry()
    rows = []
    for key in report.registry_entries_affected:
        entry = registry.require(key)
        rows.append({
            "entry_key": key,
            "status_before": entry.default_status.value,
            "status_after": entry.default_status.value,
            "promotion_allowed": False,
            "promotion_reason": report.promotion_reason,
            "claim_boundary": entry.claim_boundary,
        })
    return {
        "proposal_name": "BHSM CP O_int Registry Update Proposal",
        "version": "0.5",
        "cp_o_int_status": report.status_after,
        "entries": rows,
        "promotions_allowed": [],
        "promotions_applied": [],
        "runtime_gates_changed": False,
        "production_registry_mutated": False,
    }


def build_cp_o_int_sprint_c_registry_update(repository: str | Path | None = None) -> dict[str, Any]:
    """Annotate the symbolic candidate while preserving production statuses."""

    from .cp_o_int_sprint_c_report import build_cp_o_int_field_action_report

    report = build_cp_o_int_field_action_report(repository=repository)
    registry = default_prediction_registry()
    rows = []
    for key in report.registry_entries_affected:
        entry = registry.require(key)
        rows.append({
            "entry_key": key,
            "status_before": entry.default_status.value,
            "status_after": entry.default_status.value,
            "candidate_annotation": report.candidate_status if key == "cp_holonomy_phase_attachment" else None,
            "theorem_status": report.status_after if key == "cp_holonomy_phase_attachment" else entry.theorem_status,
            "promotion_allowed": False,
            "claim_boundary": entry.claim_boundary,
        })
    return {
        "proposal_name": "BHSM CP O_int Sprint C Registry Update Proposal",
        "version": "0.6",
        "entries": rows,
        "promotions_allowed": [],
        "promotions_applied": [],
        "runtime_gates_changed": False,
        "production_registry_mutated": False,
    }


def build_theorem_registry_update(repository: str | Path | None = None) -> dict[str, Any]:
    report = build_theorem_closure_report(repository)
    registry = default_prediction_registry()
    result_by_entry = {
        entry: result
        for result in report.results
        for entry in result.registry_entries_affected
    }
    entries = []
    for entry_key in (
        "charged_boundary_response_matrix",
        "neutral_operator_kernel_BH",
        "cp_holonomy_phase_attachment",
        "minimal_collider_interface_subset",
        "feynrules_minimal_model",
        "ufo_export",
        "madgraph_smoke_test",
    ):
        current = registry.require(entry_key)
        result = result_by_entry.get(entry_key)
        promotion = bool(result and result.promotion_allowed)
        # This sprint never bypasses runtime validation or broadens the bounded subset.
        if entry_key in {"feynrules_minimal_model", "ufo_export", "madgraph_smoke_test", "minimal_collider_interface_subset"}:
            promotion = False
        after = current.default_status.value
        if promotion:
            after = "FROZEN_INTERNAL_PREDICTION"
        entries.append({
            "entry_key": entry_key,
            "status_before": current.default_status.value,
            "status_after": after,
            "promotion_allowed": promotion,
            "promotion_reason": result.promotion_reason if result else "No theorem result targets this entry.",
            "proof_gate_summary": proof_gate_summary(result.proof_gates) if result else None,
            "claim_boundary": current.claim_boundary,
        })
    return {
        "proposal_name": "BHSM Theorem Registry Update Proposal",
        "version": "0.4",
        "entries": entries,
        "promotions_allowed": [row["entry_key"] for row in entries if row["promotion_allowed"]],
        "promotions_applied": [],
        "runtime_gates_changed": False,
        "production_registry_mutated": False,
    }
