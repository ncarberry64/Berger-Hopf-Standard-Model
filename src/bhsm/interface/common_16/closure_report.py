"""Build and export the conservative v1.8 final-completion closure report."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..full_completion import build_full_completion_blocker_ledger, build_full_completion_priority_map
from .bridge_beta_audit import audit_common_16_bridge_beta
from .ckm_transport_audit import audit_common_16_ckm_transport
from .common import FinalCompletionReport, TargetScore, TargetSelection, repository_root
from .incidence_audit import audit_common_16_incidence
from .provenance_audit import audit_common_16_provenance
from .source_search import search_common_16_sources


REQUIRED_STATEMENTS = (
    "BHSM full completion is not claimed unless all action, projector, transport, normalization, unit-map, and runtime gates are closed.",
    "Frozen prediction values are unchanged by this sprint.",
    "The CKM 1/16 exponent is not treated as artifact-backed unless the common generator and reciprocal transport theorem are both sourced.",
    "A conditional common-16 generator candidate does not by itself prove the CKM exponent.",
    "No empirical CKM fitting, charged-mass fitting, PDG values, W calibration, neutrino limits, or legacy threshold tables are used as theorem inputs.",
)

PUBLIC_STATUS = (
    "BHSM remains an integrated conditional architecture with open blockers. Full completion and physical "
    "eV/GeV neutrino mass are not claimed."
)

ARTIFACT_PATHS = {
    "manifest": "artifacts/BHSM_final_completion_manifest_v1_8.json",
    "selection": "artifacts/BHSM_final_completion_target_selection_v1_8.json",
    "final_report": "artifacts/BHSM_final_completion_closure_report_v1_8.json",
    "claims": "artifacts/BHSM_final_completion_claim_policy_v1_8.json",
    "source_search": "artifacts/BHSM_common_16_source_search_v1_8.json",
    "incidence": "artifacts/BHSM_common_16_incidence_audit_v1_8.json",
    "bridge_beta": "artifacts/BHSM_common_16_bridge_beta_audit_v1_8.json",
    "ckm_transport": "artifacts/BHSM_common_16_ckm_transport_audit_v1_8.json",
    "provenance": "artifacts/BHSM_common_16_provenance_audit_v1_8.json",
    "common_report": "artifacts/BHSM_common_16_closure_report_v1_8.json",
    "ledger": "artifacts/BHSM_full_completion_blocker_ledger_v1_8.json",
    "priority": "artifacts/BHSM_full_completion_priority_map_v1_8.json",
}


def _score(target_id: str, values: tuple[int, ...], rationale: str) -> TargetScore:
    positive = values[:6]
    penalties = values[6:]
    return TargetScore(target_id, *values, sum(positive) - sum(penalties), rationale)


def select_final_completion_target() -> TargetSelection:
    rows = (
        _score("common_16_ckm_transport", (5, 5, 4, 4, 3, 3, 0, 0, 0), "Exact local identities connect charged incidence, bridge/beta values, and the CKM candidate while provenance gates remain testable."),
        _score("rho_ch_3_action", (5, 4, 3, 4, 3, 3, 0, 0, 0), "Local branches exist, but no action Hessian selects rho_ch=3."),
        _score("omega_f_action", (5, 4, 3, 4, 3, 2, 0, 0, 0), "Boundary operators are structurally integrated, while their complete-action origin remains open."),
        _score("cross_scale_transport", (5, 3, 3, 4, 3, 3, 0, 0, 0), "Same-scale identity transport is exact; nontrivial transport lacks a generator."),
        _score("eta_l_action_transport", (5, 4, 2, 4, 3, 3, 0, 0, 0), "The stochastic/channel route is conditional and still depends on normalization."),
        _score("charged_action_normalization", (5, 4, 4, 4, 3, 2, 5, 0, 0), "It has high leverage but physical normalization units are absent."),
        _score("physical_boundary_measure", (5, 3, 4, 4, 3, 2, 5, 0, 0), "Shape and identity pieces exist; physical units remain absent."),
        _score("gauge_scalar_normalization", (5, 3, 3, 4, 3, 2, 5, 0, 0), "The normalized complete action and scalar profile remain unavailable."),
        _score("external_hep_runtime", (3, 4, 1, 4, 2, 2, 0, 5, 0), "External licensed/runtime tools are unavailable and cannot close theory provenance."),
    )
    rows = tuple(sorted(rows, key=lambda row: (-row.total_score, row.target_id)))
    return TargetSelection(
        candidate_targets=rows,
        scores={row.target_id: row.total_score for row in rows},
        selected_target=rows[0].target_id,
        why_selected="Highest predeclared score, exact offline identities, and leverage across CKM, charged bridge, beta hierarchy, rho_ch, and Omega_f provenance.",
        why_others_not_selected={row.target_id: row.rationale for row in rows[1:]},
        expected_closure_statuses=(
            "CONDITIONAL_COMMON_16_GENERATOR_CANDIDATE",
            "CONDITIONAL_CKM_LOG_TRANSPORT_CANDIDATE",
            "OPEN_MISSING_CKM_EXPONENT_DERIVATION",
        ),
        empirical_inputs_used=False,
    )


def build_final_completion_report(repository: str | Path | None = None) -> FinalCompletionReport:
    root = repository_root(repository)
    return FinalCompletionReport(
        report_name="BHSM v1.8 Common-16 and Final Completion Closure Report",
        version="1.8",
        public_status=PUBLIC_STATUS,
        target_selection=select_final_completion_target(),
        source_search=search_common_16_sources(root),
        incidence=audit_common_16_incidence(root),
        bridge_beta=audit_common_16_bridge_beta(root),
        ckm_transport=audit_common_16_ckm_transport(root),
        provenance=audit_common_16_provenance(root),
        closure_result="CONDITIONAL_COMMON_16_GENERATOR_WITH_OPEN_CKM_TRANSPORT_THEOREM",
        status_before="OPEN_MISSING_COMMON_16_GENERATOR_AND_CKM_EXPONENT_DERIVATION",
        status_after="CONDITIONAL_COMMON_16_GENERATOR_CANDIDATE_CKM_EXPONENT_OPEN",
        completion_claimed=False,
        empirical_inputs_used=False,
        frozen_predictions_changed=False,
        official_prediction_logic_changed=False,
        required_statements=REQUIRED_STATEMENTS,
    )


def final_completion_report_to_markdown(report: FinalCompletionReport) -> str:
    lines = [
        "# BHSM v1.8 Final Completion Status",
        "",
        report.public_status,
        "",
        *report.required_statements,
        "",
        "| Component | Status |",
        "| --- | --- |",
        f"| Selected target | `{report.target_selection.selected_target}` |",
        f"| Common-16 incidence | `{report.incidence.status}` |",
        f"| Omega_f source | `{report.provenance.omega_f_source_status}` |",
        f"| rho_ch source | `{report.provenance.rho_ch_source_status}` |",
        f"| Bridge/beta source | `{report.provenance.bridge_beta_source_status}` |",
        f"| CKM reciprocal transport | `{report.provenance.ckm_reciprocal_transport_status}` |",
        f"| CKM exponent | `{report.provenance.ckm_exponent_final_status}` |",
        "",
        f"Closure result: `{report.closure_result}`",
        "",
        "## Exact identities",
        "",
        "- `s_f=Omega_f/rho_ch=(1,2,4)` conditional on `rho_ch=3`.",
        "- `S_ch=7`, `Pi_f=(1/7,2/7,4/7)`, and `N_16=s_d^2=16`.",
        "- `N_16/(S_ch*rho_ch^3)=16/189=(4/3)^2/21`.",
        "- `1/N_16=1/16` is an identity, not a CKM transport theorem.",
        "",
        "## Open blockers",
        "",
        *(f"- `{item}`" for item in report.provenance.open_blockers),
    ]
    return "\n".join(lines) + "\n"


def _ledger_payload(report: FinalCompletionReport) -> dict[str, Any]:
    details = {
        "FC-03": report.provenance.rho_ch_source_status,
        "FC-06": report.provenance.ckm_exponent_final_status,
        "FC-11": "OPEN_MISSING_CROSS_SCALE_TRANSPORT_THEOREM",
    }
    rows = []
    for blocker in build_full_completion_blocker_ledger():
        row = blocker.to_dict()
        if blocker.blocker_id in details:
            row["v1_8_detail_status"] = details[blocker.blocker_id]
        rows.append(row)
    return {
        "version": "1.8",
        "blocker_count": len(rows),
        "full_completion_claimed": False,
        "selected_target": report.target_selection.selected_target,
        "blockers": rows,
    }


def _payloads(report: FinalCompletionReport) -> dict[str, dict[str, Any]]:
    return {
        "manifest": {"version": "1.8", "artifacts": ARTIFACT_PATHS, "completion_claimed": False},
        "selection": report.target_selection.to_dict(),
        "final_report": report.to_dict(),
        "claims": {
            "required_statements": list(REQUIRED_STATEMENTS),
            "completion_claimed": False,
            "empirical_inputs_used": False,
            "forbidden_claims": [
                "the CKM 1/16 exponent is artifact-backed",
                "rho_ch=3 is action-derived",
                "Omega_f is fully action-derived",
                "BHSM is fully complete",
                "BHSM is empirically validated",
            ],
        },
        "source_search": report.source_search.to_dict(),
        "incidence": report.incidence.to_dict(),
        "bridge_beta": report.bridge_beta.to_dict(),
        "ckm_transport": report.ckm_transport.to_dict(),
        "provenance": report.provenance.to_dict(),
        "common_report": report.to_dict(),
        "ledger": _ledger_payload(report),
        "priority": {
            "version": "1.8",
            "selected_target": report.target_selection.selected_target,
            "rows": [row.to_dict() for row in report.target_selection.candidate_targets],
            "legacy_priority_rows": [row.to_dict() for row in build_full_completion_priority_map()],
            "empirical_inputs_used": False,
        },
    }


def write_final_completion_artifacts(repository: str | Path | None = None) -> tuple[Path, ...]:
    root = repository_root(repository)
    report = build_final_completion_report(root)
    written = []
    for key, payload in _payloads(report).items():
        destination = root / ARTIFACT_PATHS[key]
        destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(destination)
    return tuple(written)
