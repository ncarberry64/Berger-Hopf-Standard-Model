"""Audit the conditional normalized weak gauge-action skeleton."""

from .common import STATUS_SKELETON, input_guard


def audit_normalized_weak_gauge_action_skeleton() -> dict[str, object]:
    return {
        "candidate_action_form": "S_gauge = k[Tr(F_cyc^2)+Tr(F_orient^2)+eta_Y F_Y^2]",
        "field_strength_sources": ["theory/derived_normalized_gauge_action_skeleton.md"],
        "boundary_measure_sources": ["artifacts/BHSM_author_ontology_v0_8.json"],
        "trace_sources": ["theory/theorem_discharge_boundary_trace_normalization.md"],
        "normalization_sources": ["K1=10/3", "K2=2", "K3=2", "eta_Y=3/5"],
        "variational_sources": [],
        "evidence_for": ["relative gauge kinetic normalization is explicitly recorded"],
        "evidence_against": ["overall coefficient k is not fixed", "no source identifies and fixes k=1/g2_BH^2"],
        "missing_requirements": ["overall kinetic coefficient", "normalized measure attachment", "action-derived g2_BH value"],
        "status": STATUS_SKELETON,
        "claim_boundary": "A gauge action skeleton does not derive g2_BH unless it fixes the coefficient.",
        **input_guard(),
    }
