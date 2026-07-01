"""Audit symbolic boundary-measure provenance."""

from .common import STATUS_MEASURE, input_guard


def audit_boundary_measure_source() -> dict[str, object]:
    return {
        "audit": "ckm_boundary_measure_source",
        "candidate_measure": "dmu_boundary",
        "measure_location": "artifacts/BHSM_author_ontology_v0_8.json",
        "measure_symbol": "dmu_boundary; extended neutral/collar forms use dmu_boundary dt",
        "measure_type": "symbolic author-ontology boundary/action measure",
        "boundary_trace_sources": ["theory/theorem_discharge_boundary_trace_normalization.md"],
        "collar_or_induced_measure_sources": ["theory/theorem_discharge_collar_measure_extrinsic_geometry.md"],
        "action_integral_sources": ["artifacts/BHSM_minimal_action_report_v0_8.json", "artifacts/BHSM_neutral_action_terms_v1_5.json"],
        "evidence_for": ["symbolic boundary measures occur in action candidates"],
        "evidence_against": ["physical dimension and absolute normalization remain open", "no source attaches the measure to L_CKM_charged_current_bounded"],
        "missing_requirements": ["normalized measure", "CKM-term attachment", "charged-current variational provenance"],
        "status": STATUS_MEASURE,
        "claim_boundary": "A boundary measure alone does not select the CKM transport space.",
        **input_guard(),
    }
