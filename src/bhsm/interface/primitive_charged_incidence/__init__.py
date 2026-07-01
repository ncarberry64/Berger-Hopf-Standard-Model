"""Primitive charged-incidence exact arithmetic and fail-closed action gates."""

from .bridge_beta_identity_audit import audit_bridge_beta_identity
from .ckm_log_transport_gate import audit_ckm_log_transport
from .closure_report import build_primitive_charged_incidence_report
from .external_reproduction_status import audit_external_reproduction_status
from .omega_trace_audit import audit_omega_trace
from .overlap_4_over_3_audit import audit_overlap_4_over_3
from .physical_normalization_gate import audit_physical_normalization
from .projector_reduction_audit import audit_projector_reduction
from .rho_gcd_audit import audit_rho_gcd_selection

__all__ = [name for name in globals() if name.startswith(("audit_", "build_"))]
