"""Bounded source inventory for the v3.1 gauge-coupling quantum audit."""

from .common import STATUS_REGISTRY, input_guard


def search_gauge_coupling_quantum_sources() -> dict[str, object]:
    return {
        "files_scanned": [
            "artifacts/", "docs/", "src/", "tests/", "manuscript/", "theory/",
            "README.md", "STATUS.md", "CLAIMS.md", "ROADMAP.md", "CLI_REFERENCE.md",
        ],
        "hits": [
            "src/gauge_couplings.py",
            "src/charged_lepton_eta_derivation.py",
            "theory/full_bhsm_candidate_theory_line_v0_1.md",
            "theory/full_bhsm_completion_v1_candidate.md",
            "theory/sm_low_energy_limit_derivation_gate.md",
            "theory/derived_normalized_gauge_action_skeleton.md",
            "theory/theorem_discharge_boundary_trace_normalization.md",
            "artifacts/berger_measure_domain_v1.json",
        ],
        "registry_pattern_evidence": [
            "alpha_1=1/(6*pi^2), alpha_2=2/(6*pi^2), alpha_3=7/(6*pi^2) are supplied screens",
        ],
        "volume_denominator_evidence": [
            "candidate 6*pi^2 denominator occurs, but no source derives it as 3 Vol(S^3_unit)",
        ],
        "sector_weight_evidence": [
            "candidate C_U1=1, C_SU2=dim(SU2)-1=2, C_SU3=dim(SU3)-1=7",
        ],
        "universal_quantum_evidence": ["alpha_G=C_G/(6*pi^2) is a structural candidate"],
        "action_attachment_evidence": [],
        "alpha_i_action_evidence": [],
        "g2_action_evidence": [],
        "ckm_value_evidence": [],
        "evidence_against_action_derivation": [
            "coupling_screens() labels the values supplied matching screens",
            "overall gauge-action coefficient k remains open",
            "Berger measure audit does not assume unit-S^3 volume coefficients",
            "no action identifies weights 1,2,7 as physical coupling coefficients",
        ],
        "missing_sources": [
            "derivation of 6*pi^2 from the normalized boundary measure",
            "action-selected gauge-sector weights",
            "same-action attachment of the denominator and weights",
            "action-derived alpha_i and g2_BH values",
        ],
        "status": STATUS_REGISTRY,
        **input_guard(),
    }
