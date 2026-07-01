"""Public interface for the v2.7 bounded CKM interface normalization audit."""

from .bounded_interface_term import audit_ckm_bounded_interface_term
from .ckm_identification_gate import audit_ckm_identification_gate
from .closure_report import build_ckm_bounded_interface_report, ckm_bounded_interface_report_to_markdown
from .normalized_projector_sandwich import audit_normalized_projector_sandwich
from .paired_term_normalization import audit_paired_term_normalization
from .projector_domain_codomain import audit_projector_domain_codomain
from .source_search import search_ckm_bounded_interface_sources
from .transport_space_selection import audit_ckm_transport_space_selection

__all__ = [
    "audit_ckm_bounded_interface_term",
    "audit_ckm_identification_gate",
    "audit_ckm_transport_space_selection",
    "audit_normalized_projector_sandwich",
    "audit_paired_term_normalization",
    "audit_projector_domain_codomain",
    "build_ckm_bounded_interface_report",
    "ckm_bounded_interface_report_to_markdown",
    "search_ckm_bounded_interface_sources",
]
