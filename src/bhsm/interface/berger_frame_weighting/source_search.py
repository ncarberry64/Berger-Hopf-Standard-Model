from .common import INPUT_GUARD


def search_berger_frame_weighting_sources():
    return {
        "status": "SOURCE_SEARCH_COMPLETE_FRAME_WEIGHTING_OPEN",
        "claim_boundary": "Diagnostic 1/3 candidates and an anisotropic metric do not establish an action-selected gauge-frame average.",
        "candidate_formula": "c1=c2=c3 and FrameAvg=(1/3) sum_a",
        "evidence_for": ["artifacts/berger_measure_domain_v1.json", "theory/berger_base_action_coupling_normalization.md", "theory/representation_normalization_audit.md"],
        "evidence_against": ["r_base and r_fiber are distinct", "coframe-average candidates are diagnostic only", "the gauge skeleton has no Berger frame index or 1/3 factor"],
        "dependencies": ["Berger metric", "orthonormal gauge coframe", "normalized gauge action"],
        "blocking_conditions": ["equal coefficient theorem", "average normalization", "gauge trace attachment"],
        "promoted_from": None,
        "not_promoted_because": ["the action basis and normalization are unspecified"],
        "searched_roots": ["artifacts", "docs", "src", "tests", "manuscript", "reports", "theory", "README.md", "STATUS.md", "CLAIMS.md", "ROADMAP.md", "CLI_REFERENCE.md"],
        **INPUT_GUARD,
    }
