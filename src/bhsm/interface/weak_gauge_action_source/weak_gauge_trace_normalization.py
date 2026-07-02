"""Audit relative trace normalization versus physical coupling normalization."""

from .common import STATUS_TRACE, input_guard


def audit_weak_gauge_trace_normalization() -> dict[str, object]:
    return {
        "trace_type": "finite boundary representation trace",
        "trace_source": "theory/theorem_discharge_boundary_trace_normalization.md",
        "finite_algebra_trace": "K2_orientation=2",
        "boundary_trace": "K1=10/3, K2=K3=2",
        "Hilbert_Schmidt_trace": None,
        "generator_normalization": "fundamental active-orientation index 1/2; conditional convention",
        "does_trace_fix_coupling_value": False,
        "evidence_for": ["relative trace weights and eta_Y=3/5 are conditionally derived"],
        "evidence_against": ["global trace normalization and physical kinetic coefficient remain open"],
        "status": STATUS_TRACE,
        "claim_boundary": "Trace/generator normalization may fix conventions without fixing the physical coupling.",
        **input_guard(),
    }
