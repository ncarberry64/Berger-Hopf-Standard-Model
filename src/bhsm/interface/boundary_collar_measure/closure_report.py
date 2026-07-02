import json

from .common import GATES, INPUT_GUARD, REJECTED_CLAIMS, REQUIRED_STATEMENTS, build_gate
from .source_search import search_boundary_collar_measure_sources


def build_boundary_collar_measure_report():
    return {
        "status": "CONDITIONAL_BOUNDARY_COLLAR_MEASURE_SOURCE_FRAME_AVERAGE_OPEN",
        "claim_boundary": "The measure formula and three coframe directions do not derive the gauge denominator or couplings.",
        "candidate_formula": "<X>_B=[3 Vol(S^3_unit)]^-1 sum_a int X_a dmu_B",
        "evidence_for": ["conditional collar measure formula", "artifact-backed three coframe directions"],
        "evidence_against": ["unit S3 normalization, action average, and gauge attachment are open"],
        "dependencies": list(GATES),
        "blocking_conditions": [name for name, gate in GATES.items() if str(gate["status"]).startswith(("OPEN_", "FULL_"))],
        "promoted_from": "v4.0 full-action blocker DAG",
        "not_promoted_because": ["gauge normalization conjunction is false"],
        "source_search": search_boundary_collar_measure_sources(),
        "gates": {name: build_gate(name) for name in GATES},
        "artifact_backed_closures": ["ARTIFACT_BACKED_THREE_BOUNDARY_FRAME_DIRECTIONS"],
        "conditional_closures": ["CONDITIONAL_BOUNDARY_COLLAR_MEASURE_SOURCE"],
        "retired_or_rejected_claims": list(REJECTED_CLAIMS),
        "required_statements": list(REQUIRED_STATEMENTS),
        **INPUT_GUARD,
    }


def boundary_collar_measure_report_to_markdown(payload=None):
    report = payload or build_boundary_collar_measure_report()
    statements = "\n".join(f"- {line}" for line in report["required_statements"])
    return "# BHSM Boundary/Collar Measure v4.1\n\n" + statements + "\n\n```json\n" + json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n```"
