"""Combined v3.1 gauge-coupling quantum report."""

import json

from .action_attachment import audit_gauge_coupling_action_attachment
from .alpha_i_action_derivation import audit_alpha_i_action_derivation
from .ckm_value_update import audit_ckm_value_source_update
from .common import REJECTED_CLAIMS, REQUIRED_STATEMENTS, input_guard
from .g2_action_source_update import audit_g2_action_source_update
from .registry_pattern import audit_gauge_coupling_registry_pattern
from .sector_weight_source import audit_gauge_sector_weight_source
from .source_search import search_gauge_coupling_quantum_sources
from .universal_quantum import audit_universal_gauge_coupling_quantum
from .volume_denominator import audit_gauge_coupling_volume_denominator


def build_gauge_coupling_quantum_report() -> dict[str, object]:
    return {
        "source_search": search_gauge_coupling_quantum_sources(),
        "registry_pattern": audit_gauge_coupling_registry_pattern(),
        "volume_denominator": audit_gauge_coupling_volume_denominator(),
        "sector_weights": audit_gauge_sector_weight_source(),
        "universal_quantum": audit_universal_gauge_coupling_quantum(),
        "action_attachment": audit_gauge_coupling_action_attachment(),
        "alpha_i": audit_alpha_i_action_derivation(),
        "g2": audit_g2_action_source_update(),
        "ckm": audit_ckm_value_source_update(),
        "artifact_backed_closures": ["ARTIFACT_BACKED_GAUGE_COUPLING_REGISTRY_PATTERN"],
        "conditional_closures": ["CONDITIONAL_GAUGE_SECTOR_WEIGHT_SOURCE"],
        "retired_or_rejected_claims": list(REJECTED_CLAIMS),
        "required_statements": list(REQUIRED_STATEMENTS),
        **input_guard(),
    }


def gauge_coupling_quantum_report_to_markdown(payload=None) -> str:
    report = payload or build_gauge_coupling_quantum_report()
    statements = "\n".join(f"- {line}" for line in report["required_statements"])
    return "# Gauge Coupling Quantum Audit\n\n" + statements + "\n\n```json\n" + json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n```"
