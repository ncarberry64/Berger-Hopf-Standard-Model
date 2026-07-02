"""Combined v4.0 full-action closure report."""

import json

from .common import GATES, INPUT_GUARD, REQUIRED_STATEMENTS, build_gate, build_status_snapshot
from .source_search import search_full_action_sources
from .theorem_blocker_dag import build_theorem_blocker_dag


def build_full_action_closure_report() -> dict[str, object]:
    return {
        "status_snapshot": build_status_snapshot(),
        "source_search": search_full_action_sources(),
        "theorem_blocker_dag": build_theorem_blocker_dag(),
        "gates": {name: build_gate(name) for name in GATES},
        "artifact_backed_closures": [
            "ARTIFACT_BACKED_GAUGE_COUPLING_REGISTRY_PATTERN",
            "ARTIFACT_BACKED_CKM_COEFFICIENT_FORM",
            "STRUCTURAL_DOCTRINE_LOCKED",
        ],
        "conditional_closures": [
            "CONDITIONAL_UNIFIED_ACTION_SKELETON",
            "CONDITIONAL_GAUGE_SECTOR_WEIGHT_SOURCE",
            "CONDITIONAL_NEUTRAL_DIMENSIONLESS_STRUCTURE",
        ],
        "open_blockers": build_theorem_blocker_dag()["blocking_conditions"],
        "retired_or_rejected_claims": [
            "registry pattern as action derivation",
            "volume identity alone as coupling derivation",
            "sector count alone as coupling derivation",
            "CKM coefficient form as coefficient value or exponent",
            "dimensionless neutral structure as physical mass",
            "full BHSM completion",
        ],
        "required_statements": list(REQUIRED_STATEMENTS),
        **INPUT_GUARD,
    }


def full_action_closure_report_to_markdown(payload: dict[str, object] | None = None) -> str:
    report = payload or build_full_action_closure_report()
    statements = "\n".join(f"- {line}" for line in report["required_statements"])
    return "# BHSM Full Action Closure v4.0\n\n" + statements + "\n\n```json\n" + json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n```"
