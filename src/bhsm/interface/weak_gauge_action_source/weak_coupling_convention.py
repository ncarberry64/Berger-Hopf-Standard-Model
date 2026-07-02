"""Reuse the conditional weak-coupling convention without value promotion."""

from .common import STATUS_CONVENTION, input_guard


def audit_weak_gauge_coupling_convention() -> dict[str, object]:
    return {"candidate_relation": "g2_BH^2/(4*pi)=alpha2_BH", "is_action_derivation": False, "status": STATUS_CONVENTION, "claim_boundary": "A coupling convention relates symbols but derives neither value.", **input_guard()}
