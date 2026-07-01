"""Exact mathematical action lemmas and fail-closed BHSM application gates."""

from .ckm_application_gate import audit_ckm_log_transport_application
from .closure_report import build_action_lemma_closure_report
from .log_transport_averaging import (
    energy_excess_identity,
    log_transport_minimizer,
    prove_log_transport_averaging,
    quadratic_log_energy,
)
from .maximal_overlap_bridge_rule import audit_maximal_overlap_bridge_rule
from .primitive_lattice_rule import audit_primitive_lattice_rule
from .source_search import search_action_lemma_sources

__all__ = [name for name in globals() if name.startswith(("audit_", "build_", "prove_", "log_", "quadratic_", "energy_"))]
