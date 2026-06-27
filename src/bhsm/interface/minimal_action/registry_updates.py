"""Non-destructive registry updates for minimal-action theorem results."""

from __future__ import annotations

from .common import MinimalActionClosureResult


def minimal_action_registry_updates(results: tuple[MinimalActionClosureResult, ...]) -> dict[str, object]:
    entries = {
        "cp_o_int": "cp_holonomy_phase_attachment",
        "X_ch": "charged_boundary_response_matrix",
        "neutrino_basis_scale": "neutral_operator_kernel_BH",
    }
    return {
        "update_name": "BHSM Minimal Action Registry Updates",
        "version": "0.8",
        "updates": [
            {
                "theorem_key": row.theorem_key,
                "registry_entry": entries[row.theorem_key],
                "status": row.status_after,
                "promoted": row.promoted,
                "remaining_missing_object": row.remaining_missing_object,
            }
            for row in results
        ],
        "runtime_gates_changed": any(row.runtime_gates_changed for row in results),
        "frozen_predictions_changed": False,
    }
