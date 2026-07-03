import json

from .common import GATES, INPUT_GUARD, REJECTED_CLAIMS, REQUIRED_STATEMENTS, build_gate
from .source_search import search_berger_frame_weighting_sources


def build_berger_frame_weighting_report():
    return {
        "status": "FRAME_WEIGHTING_OPEN_ANISOTROPY_COMPATIBILITY_CONDITIONAL",
        "claim_boundary": "The orthonormal-frame compatibility route is conditional and does not promote the denominator or couplings.",
        "candidate_formula": "FrameAvg_B[X]=(1/3) sum_a X_a",
        "evidence_for": ["three coframe directions", "conditional orthonormalization route"],
        "evidence_against": ["no action-selected equal weights, average normalization, or gauge trace attachment"],
        "dependencies": list(GATES),
        "blocking_conditions": [name for name, gate in GATES.items() if str(gate["status"]).startswith(("OPEN_", "FULL_"))],
        "promoted_from": "v4.1 boundary/collar measure audit",
        "not_promoted_because": ["the frame-average theorem conjunction remains false"],
        "source_search": search_berger_frame_weighting_sources(),
        "gates": {name: build_gate(name) for name in GATES},
        "artifact_backed_closures": [],
        "conditional_closures": ["CONDITIONAL_BERGER_ANISOTROPY_COMPATIBILITY"],
        "retired_or_rejected_claims": list(REJECTED_CLAIMS),
        "required_statements": list(REQUIRED_STATEMENTS),
        **INPUT_GUARD,
    }


def berger_frame_weighting_report_to_markdown(payload=None):
    report = payload or build_berger_frame_weighting_report()
    statements = "\n".join(f"- {line}" for line in report["required_statements"])
    return "# BHSM Berger Frame Weighting v4.2\n\n" + statements + "\n\n```json\n" + json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n```"
