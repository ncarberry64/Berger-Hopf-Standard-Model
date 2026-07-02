"""Audit the proposed 6*pi^2 boundary-volume denominator."""

from .common import STATUS_VOLUME, input_guard


def audit_gauge_coupling_volume_denominator() -> dict[str, object]:
    return {
        "candidate_denominator": "6*pi^2",
        "volume_identity": "6*pi^2 = 3 Vol(S^3_unit), with Vol(S^3_unit)=2*pi^2",
        "source_locations": [
            "theory/full_bhsm_candidate_theory_line_v0_1.md",
            "src/gauge_couplings.py",
        ],
        "boundary_measure_sources": ["artifacts/BHSM_author_ontology_v0_8.json"],
        "collar_measure_sources": ["theory/theorem_discharge_collar_measure_extrinsic_geometry.md"],
        "S3_volume_sources": [],
        "evidence_for": ["the registry and candidate gauge layer use the denominator 6*pi^2"],
        "evidence_against": [
            "no located source identifies that denominator with 3 Vol(S^3_unit)",
            "Berger measure artifacts explicitly avoid assuming unit-S^3 volume coefficients",
            "boundary and collar measures do not fix the physical gauge-action normalization",
        ],
        "status": STATUS_VOLUME,
        "claim_boundary": "The identity 6π² = 3 Vol(S³) does not by itself derive the gauge couplings.",
        **input_guard(),
    }
