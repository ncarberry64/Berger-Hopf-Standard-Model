"""Combined weak gauge action source report."""

import json

from .alpha2_action_source import audit_alpha2_bh_action_source
from .ckm_value_blocker import audit_ckm_value_source_blocker
from .common import REJECTED_CLAIMS, REQUIRED_STATEMENTS, input_guard
from .g2_action_source import audit_g2_bh_action_source
from .normalized_weak_gauge_action_skeleton import audit_normalized_weak_gauge_action_skeleton
from .source_search import search_weak_gauge_action_sources
from .weak_coupling_convention import audit_weak_gauge_coupling_convention
from .weak_gauge_action_coefficient import audit_normalized_weak_gauge_action_coefficient
from .weak_gauge_algebra_source import audit_weak_gauge_algebra_source
from .weak_gauge_trace_normalization import audit_weak_gauge_trace_normalization


def build_weak_gauge_action_source_report() -> dict[str, object]:
    return {"source_search": search_weak_gauge_action_sources(), "algebra": audit_weak_gauge_algebra_source(), "skeleton": audit_normalized_weak_gauge_action_skeleton(), "trace": audit_weak_gauge_trace_normalization(), "g2": audit_g2_bh_action_source(), "alpha2": audit_alpha2_bh_action_source(), "convention": audit_weak_gauge_coupling_convention(), "coefficient": audit_normalized_weak_gauge_action_coefficient(), "ckm_blocker": audit_ckm_value_source_blocker(), "artifact_backed_closures": ["ARTIFACT_BACKED_G2_BH_RUNTIME_INPUT", "ARTIFACT_BACKED_ALPHA2_BH_REGISTERED_COUPLING"], "conditional_closures": ["CONDITIONAL_WEAK_GAUGE_ALGEBRA_SOURCE", "CONDITIONAL_NORMALIZED_WEAK_GAUGE_ACTION_SKELETON", "CONDITIONAL_WEAK_GAUGE_TRACE_NORMALIZATION", "CONDITIONAL_WEAK_COUPLING_CONVENTION"], "retired_or_rejected_claims": list(REJECTED_CLAIMS), "required_statements": list(REQUIRED_STATEMENTS), **input_guard()}


def weak_gauge_action_source_report_to_markdown(payload=None) -> str:
    report = payload or build_weak_gauge_action_source_report()
    return "# Weak Gauge Action Source Audit\n\n" + "\n".join(f"- {line}" for line in report["required_statements"]) + "\n\n```json\n" + json.dumps(report, indent=2, sort_keys=True) + "\n```"
