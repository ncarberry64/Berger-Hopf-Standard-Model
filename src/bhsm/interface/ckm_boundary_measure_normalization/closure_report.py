"""Combined v2.8 report."""

import json

from .boundary_measure_source import audit_boundary_measure_source
from .coefficient_normalization import audit_coefficient_normalization
from .common import REQUIRED_STATEMENTS, input_guard
from .measure_coefficient_pair import audit_measure_coefficient_pair
from .normalized_action_candidate import audit_normalized_ckm_action_candidate
from .paired_normalization_rule import audit_paired_normalization_rule
from .projector_sandwich_requirement import audit_projector_sandwich_requirement
from .source_search import search_boundary_measure_normalization_sources
from .transport_space_blocker import audit_transport_space_blocker


def build_boundary_measure_normalization_report() -> dict[str, object]:
    return {"audit": "ckm_boundary_measure_normalization_report", "source_search": search_boundary_measure_normalization_sources(), "boundary_measure": audit_boundary_measure_source(), "coefficient": audit_coefficient_normalization(), "measure_coefficient_pair": audit_measure_coefficient_pair(), "normalized_action": audit_normalized_ckm_action_candidate(), "projector": audit_projector_sandwich_requirement(), "paired_normalization": audit_paired_normalization_rule(), "transport_blocker": audit_transport_space_blocker(), "artifact_backed_closures": ["ARTIFACT_BACKED_BOUNDED_CKM_INTERFACE_TERM"], "conditional_closures": ["CONDITIONAL_BOUNDARY_MEASURE_SOURCE"], "retired_or_rejected_claims": ["REJECTED_BOUNDED_INTERFACE_IMPLIES_NORMALIZED_ACTION", "REJECTED_MEASURE_EXISTS_IMPLIES_CKM_IDENTIFICATION", "REJECTED_COEFFICIENT_ARITHMETIC_IMPLIES_ACTION_NORMALIZATION", "RETIRED_MAXIMAL_SELF_RESPONSE_AS_PRIMARY_CKM_SOURCE"], "required_boundary_statements": list(REQUIRED_STATEMENTS), **input_guard()}


def boundary_measure_normalization_report_to_markdown(payload=None) -> str:
    report = payload or build_boundary_measure_normalization_report()
    lines = ["# CKM Boundary Measure Normalization Audit", "", f"Measure: `{report['boundary_measure']['status']}`", f"Coefficient: `{report['coefficient']['status']}`", f"Normalized action: `{report['normalized_action']['status']}`", f"CKM exponent: `{report['transport_blocker']['ckm_exponent_status']}`", "", "## Claim Boundaries"]
    lines.extend(f"- {item}" for item in report["required_boundary_statements"])
    lines.extend(["", "```json", json.dumps(report, indent=2, sort_keys=True), "```"])
    return "\n".join(lines)
