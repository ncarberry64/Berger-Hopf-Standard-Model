"""Audit the conditional weak finite-algebra source."""

from .common import STATUS_ALGEBRA, input_guard


def audit_weak_gauge_algebra_source() -> dict[str, object]:
    return {
        "candidate_algebra": "A_weak = M2(C)_{w=1} direct_sum C_+ direct_sum C_-",
        "source_locations": ["theory/finite_boundary_algebra_source_gate.md", "theory/derived_finite_algebra_uniqueness.md"],
        "weak_doublet_sources": ["theory/derived_electroweak_breaking_generator.md"],
        "finite_algebra_sources": ["theory/theorem_discharge_finite_algebra_charge.md"],
        "status": STATUS_ALGEBRA,
        "claim_boundary": "A weak gauge algebra source does not derive the coupling value.",
        **input_guard(),
    }
