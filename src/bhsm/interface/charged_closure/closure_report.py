"""Assemble and export the charged action/stiffness/mixing closure audit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..full_completion import build_full_completion_blocker_ledger, build_full_completion_priority_map
from .action_stiffness import derive_or_locate_charged_action_stiffness
from .ckm_exponent_source import derive_or_locate_ckm_exponent_source
from .common import ChargedClosureReport, repository_root
from .dimensional_audit import audit_charged_closure_dimensions
from .eta_l_source import derive_or_locate_eta_l_source
from .mixing_law_source import derive_or_locate_charged_mixing_law_source
from .source_search import search_charged_closure_sources


ARTIFACT_PATHS = {
    "manifest": "artifacts/BHSM_charged_closure_manifest_v1_7.json",
    "source_search": "artifacts/BHSM_charged_source_search_v1_7.json",
    "action_stiffness": "artifacts/BHSM_charged_action_stiffness_v1_7.json",
    "eta_l": "artifacts/BHSM_eta_l_source_audit_v1_7.json",
    "ckm_exponent": "artifacts/BHSM_ckm_exponent_source_audit_v1_7.json",
    "mixing_law": "artifacts/BHSM_charged_mixing_law_audit_v1_7.json",
    "dimensions": "artifacts/BHSM_charged_dimensional_audit_v1_7.json",
    "report": "artifacts/BHSM_charged_closure_report_v1_7.json",
    "claims": "artifacts/BHSM_charged_claim_policy_v1_7.json",
}

FULL_COMPLETION_V17_PATHS = {
    "ledger": "artifacts/BHSM_full_completion_blocker_ledger_v1_7.json",
    "priority": "artifacts/BHSM_full_completion_priority_map_v1_7.json",
}

REQUIRED_STATEMENTS = (
    "BHSM does not use charged-lepton masses, CKM reference values, PDG values, W calibration, or empirical fitting as theorem inputs.",
    "Charged-sector closure requires an action/projection/transport source for charged stiffness, eta_l, and the CKM exponent/mixing law.",
    "Frozen CKM and charged-sector prediction values are not changed by the charged closure audit.",
    "Conditional charged-source candidates are not treated as artifact-backed derivations unless the source artifacts prove them.",
)

PUBLIC_STATUS = (
    "BHSM remains an integrated conditional architecture with open charged action-normalization and "
    "mixing-source blockers. Frozen predictions are unchanged and empirical validation is not claimed."
)


def build_charged_closure_report(repository: str | Path | None = None) -> ChargedClosureReport:
    root = repository_root(repository)
    search = search_charged_closure_sources(root)
    action = derive_or_locate_charged_action_stiffness(root)
    eta = derive_or_locate_eta_l_source(root)
    exponent = derive_or_locate_ckm_exponent_source(root)
    mixing = derive_or_locate_charged_mixing_law_source(root)
    dimensions = audit_charged_closure_dimensions()
    return ChargedClosureReport(
        report_name="BHSM Charged Action, Stiffness, and Mixing Source Closure Audit",
        version="1.7",
        public_status=PUBLIC_STATUS,
        source_search=search,
        action_stiffness=action,
        eta_l=eta,
        ckm_exponent=exponent,
        mixing_law=mixing,
        dimensional_audit=dimensions,
        closure_result="CHARGED_SOURCE_CLUSTER_CONDITIONALLY_LOCALIZED_WITH_OPEN_ACTION_NORMALIZATION",
        status_before="OPEN_CHARGED_ACTION_STIFFNESS_ETA_CKM_MIXING_CLUSTER",
        status_after=(
            "CONDITIONAL_CHARGED_SOURCES_WITH_OPEN_ACTION_NORMALIZATION_AND_CKM_EXPONENT_DERIVATION"
        ),
        remaining_blockers=(
            "OPEN_MISSING_CHARGED_ACTION_NORMALIZATION",
            "OPEN_MISSING_CHARGED_KINETIC_STIFFNESS",
            "OPEN_MISSING_CHARGED_CURVATURE_PENALTY",
            "OPEN_MISSING_NUMERIC_CHARGED_STIFFNESS",
            "OPEN_MISSING_ETA_L_ACTION_SOURCE",
            "OPEN_MISSING_ETA_L_TRANSPORT_NORMALIZATION",
            "OPEN_MISSING_CKM_EXPONENT_DERIVATION",
            "OPEN_MISSING_CROSS_SCALE_TRANSPORT",
            "OPEN_MISSING_BOUNDARY_MEASURE_PHYSICAL_NORMALIZATION",
        ),
        completion_claimed=False,
        empirical_inputs_used=False,
        frozen_predictions_changed=False,
        official_prediction_logic_changed=False,
        required_statements=REQUIRED_STATEMENTS,
    )


def charged_closure_report_to_markdown(report: ChargedClosureReport) -> str:
    lines = [
        "# BHSM Charged Closure Report",
        "",
        report.public_status,
        "",
        *report.required_statements,
        "",
        "| Component | Status |",
        "| --- | --- |",
        f"| Charged action/stiffness | `{report.action_stiffness.status}` |",
        f"| rho_ch=1 route | `{report.action_stiffness.rho_ch_1_status}` |",
        f"| rho_ch=3 route | `{report.action_stiffness.rho_ch_3_status}` |",
        f"| eta_l source | `{report.eta_l.status}` |",
        f"| CKM 1/16 exponent | `{report.ckm_exponent.status}` |",
        f"| Charged mixing law | `{report.mixing_law.status}` |",
        f"| Dimensional audit | `{report.dimensional_audit.status}` |",
        "",
        f"Closure result: `{report.closure_result}`",
        "",
        "## Remaining Blockers",
        "",
        *(f"- `{blocker}`" for blocker in report.remaining_blockers),
        "",
        "No frozen charged or CKM value is changed.",
    ]
    return "\n".join(lines) + "\n"


def _charged_payloads(report: ChargedClosureReport) -> dict[str, dict[str, Any]]:
    return {
        "manifest": {
            "version": "1.7",
            "artifacts": ARTIFACT_PATHS,
            "full_completion_updates": FULL_COMPLETION_V17_PATHS,
            "completion_claimed": False,
        },
        "source_search": report.source_search.to_dict(),
        "action_stiffness": report.action_stiffness.to_dict(),
        "eta_l": report.eta_l.to_dict(),
        "ckm_exponent": report.ckm_exponent.to_dict(),
        "mixing_law": report.mixing_law.to_dict(),
        "dimensions": report.dimensional_audit.to_dict(),
        "report": report.to_dict(),
        "claims": {
            "required_statements": list(REQUIRED_STATEMENTS),
            "completion_claimed": False,
            "empirical_inputs_used": False,
            "frozen_predictions_changed": False,
            "official_prediction_logic_changed": False,
            "forbidden_claims": [
                "charged stiffness is action-derived",
                "eta_l is fully derived",
                "the CKM 1/16 exponent is action-derived",
                "the charged mixing law is a complete action theorem",
                "BHSM is empirically validated",
            ],
        },
    }


def _full_completion_updates(report: ChargedClosureReport) -> dict[str, dict[str, Any]]:
    detail = {
        "FC-03": report.action_stiffness.status,
        "FC-05": report.eta_l.status,
        "FC-06": report.ckm_exponent.status,
    }
    blockers = []
    for blocker in build_full_completion_blocker_ledger():
        row = blocker.to_dict()
        if blocker.blocker_id in detail:
            row["v1_7_detail_status"] = detail[blocker.blocker_id]
        blockers.append(row)
    priorities = [row.to_dict() for row in build_full_completion_priority_map()]
    return {
        "ledger": {
            "version": "1.7",
            "blocker_count": len(blockers),
            "charged_cluster_audited": True,
            "blockers": blockers,
        },
        "priority": {
            "version": "1.7",
            "completed_audit_target": "charged_action_stiffness_mixing_cluster",
            "next_target": "complete_charged_action_normalization",
            "next_target_reason": "It is the common upstream dependency for rho_ch, physical charged stiffness, eta_l normalization, and higher-channel mixing provenance.",
            "rows": priorities,
            "empirical_inputs_used": False,
        },
    }


def write_charged_closure_artifacts(repository: str | Path | None = None) -> tuple[Path, ...]:
    root = repository_root(repository)
    report = build_charged_closure_report(root)
    written = []
    for key, payload in _charged_payloads(report).items():
        destination = root / ARTIFACT_PATHS[key]
        destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(destination)
    for key, payload in _full_completion_updates(report).items():
        destination = root / FULL_COMPLETION_V17_PATHS[key]
        destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(destination)
    return tuple(written)
