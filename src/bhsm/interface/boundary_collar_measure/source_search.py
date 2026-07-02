from .common import INPUT_GUARD


def search_boundary_collar_measure_sources():
    return {
        "status": "SOURCE_SEARCH_COMPLETE_MEASURE_CONDITIONAL_FRAME_AVERAGE_OPEN",
        "claim_boundary": "Search hits preserve their source classifications and do not imply action attachment.",
        "candidate_formula": "<X>_B=[3 Vol(S^3_unit)]^-1 sum_a int X_a dmu_B",
        "evidence_for": [
            "theory/theorem_discharge_collar_measure_extrinsic_geometry.md",
            "theory/theorem_discharge_boundary_embedding_shape_operator.md",
            "artifacts/berger_measure_domain_v1.json",
            "src/bhsm_berger_base_action_coupling.py",
        ],
        "evidence_against": [
            "Berger measure normalization explicitly remains open",
            "coframe-average candidates are diagnostic only",
            "no gauge trace-density attachment was located",
        ],
        "dependencies": ["repository-local geometry and action sources"],
        "blocking_conditions": ["unit S3 normalization", "action-selected frame average", "gauge trace attachment"],
        "promoted_from": None,
        "not_promoted_because": ["the theorem conjunction is incomplete"],
        "searched_roots": ["artifacts", "docs", "src", "tests", "manuscript", "reports", "theory", "README.md", "STATUS.md", "CLAIMS.md", "ROADMAP.md", "CLI_REFERENCE.md"],
        **INPUT_GUARD,
    }
