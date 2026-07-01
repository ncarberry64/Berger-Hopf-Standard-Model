"""Combined primitive charged-incidence closure report."""

from __future__ import annotations

from .bridge_beta_identity_audit import audit_bridge_beta_identity
from .ckm_log_transport_gate import audit_ckm_log_transport
from .external_reproduction_status import audit_external_reproduction_status
from .omega_trace_audit import audit_omega_trace
from .overlap_4_over_3_audit import audit_overlap_4_over_3
from .physical_normalization_gate import audit_physical_normalization
from .projector_reduction_audit import audit_projector_reduction
from .rho_gcd_audit import audit_rho_gcd_selection


def build_primitive_charged_incidence_report() -> dict[str, object]:
    return {
        "version": "2.0",
        "status": "EXACT_CONDITIONAL_ALGEBRA_WITH_OPEN_ACTION_GATES",
        "omega_trace": audit_omega_trace(),
        "rho_gcd": audit_rho_gcd_selection(),
        "projector_reduction": audit_projector_reduction(),
        "overlap": audit_overlap_4_over_3(),
        "bridge_beta": audit_bridge_beta_identity(),
        "ckm_transport": audit_ckm_log_transport(),
        "physical_normalization": audit_physical_normalization(),
        "external_reproduction": audit_external_reproduction_status(),
        "official_predictions_modified": False,
        "frozen_predictions_modified": False,
        "full_completion_claimed": False,
        "claim_boundary": "The primitive charged incidence audit establishes exact conditional algebraic identities, not full action derivations.",
    }
