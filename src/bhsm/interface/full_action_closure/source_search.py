"""Deterministic source inventory used by the v4.0 audit."""

from .common import INPUT_GUARD


def search_full_action_sources() -> dict[str, object]:
    return {
        "status": "SOURCE_SEARCH_COMPLETE_NO_NEW_ACTION_CLOSURE",
        "claim_boundary": "Located candidates are evidence inputs, not automatic theorem closures.",
        "evidence_for": [
            "theory/derived_normalized_gauge_action_skeleton.md",
            "artifacts/BHSM_gauge_coupling_quantum_report_v3_1.json",
            "artifacts/BHSM_ckm_coefficient_form_v2_9.json",
            "artifacts/BHSM_neutral_action_closure_report_v1_5.json",
            "theory/theorem_discharge_complete_scalar_topographic_collar_action.md",
            "src/bhsm/interface/full_completion/ledger.py",
        ],
        "evidence_against": [
            "no unified normalized action source was located",
            "no gauge denominator/frame average was attached to the action",
            "no physical neutral or scalar scale bridge was located",
        ],
        "dependencies": ["repository-local source tree"],
        "blocking_conditions": ["missing theorem sources listed by the blocker DAG"],
        "promoted_from": None,
        "not_promoted_because": ["search hits preserve their existing conditional/open classifications"],
        "searched_roots": ["artifacts", "docs", "src", "tests", "manuscript", "reports", "theory", "README.md", "STATUS.md", "CLAIMS.md", "ROADMAP.md", "CLI_REFERENCE.md"],
        **INPUT_GUARD,
    }
