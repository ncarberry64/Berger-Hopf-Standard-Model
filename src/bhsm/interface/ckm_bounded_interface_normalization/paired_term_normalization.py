"""Audit whether forward and conjugate terms share one action normalization."""

from __future__ import annotations

from .common import STATUS_OPEN_PAIR, input_guard


def audit_paired_term_normalization() -> dict[str, object]:
    return {
        "audit": "paired_term_normalization",
        "forward_term_present": True,
        "adjoint_term_present": True,
        "same_normalization_source": False,
        "same_measure_source": False,
        "same_projector_source": False,
        "hermiticity_source": "target-level + h.c. convention",
        "paired_as_single_action_object": False,
        "status": STATUS_OPEN_PAIR,
        "blocking_conditions": [
            "no action normalization ties the forward and adjoint terms",
            "no shared boundary/action measure is supplied",
            "no shared Pi_u/Pi_d projector source is attached",
            "target-level Hermitian conjugation is not variational action provenance",
        ],
        **input_guard(),
    }
