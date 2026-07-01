"""Combined conservative report for charged action-derivation gates."""

from __future__ import annotations

from .omega_f_action_audit import audit_omega_f_action
from .overlap_source_audit import audit_charged_overlap_source
from .rho_ch_action_audit import audit_rho_ch_action


def build_action_derivation_report() -> dict[str, object]:
    omega = audit_omega_f_action()
    rho = audit_rho_ch_action()
    overlap = audit_charged_overlap_source()
    return {
        "version": "1.9",
        "status": "ACTION_DERIVATION_GATES_OPEN",
        "omega_f": omega,
        "rho_ch": rho,
        "charged_overlap": overlap,
        "no_empirical_theorem_inputs": True,
        "frozen_predictions_modified": False,
        "claim_boundary": "Focused provenance audit only; no charged prediction or theorem status is promoted beyond its evidence.",
    }
