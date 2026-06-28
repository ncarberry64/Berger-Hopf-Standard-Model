"""Assemble and export the BHSM v1.6 completion audit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..neutrino_closure_status import (
    ACTION_DERIVED_RESPONSE_CONE_STATUS,
    DIMENSIONFUL_EV_GEV_MASS_CLOSURE_STATUS,
    DIMENSIONLESS_PROPAGATION_CLOSURE_STATUS,
    MEASUREMENT_SUPPORTED_ADMISSIBLE_POSITIVITY_STATUS,
    NEUTRAL_SPECTRAL_MASS_THEOREM_STATUS,
)
from .boundary_measure_closure import build_boundary_measure_closure
from .common import FullCompletionStatusReport, repository_root
from .ledger import build_full_completion_blocker_ledger
from .priority import build_full_completion_priority_map, select_highest_leverage_target


ARTIFACT_PATHS = {
    "manifest": "artifacts/BHSM_full_completion_manifest_v1_6.json",
    "ledger": "artifacts/BHSM_full_completion_blocker_ledger_v1_6.json",
    "priority": "artifacts/BHSM_full_completion_priority_map_v1_6.json",
    "selected": "artifacts/BHSM_full_completion_selected_target_v1_6.json",
    "closure": "artifacts/BHSM_full_completion_closure_attempt_v1_6.json",
    "status": "artifacts/BHSM_full_completion_public_status_v1_6.json",
    "claims": "artifacts/BHSM_full_completion_claim_policy_v1_6.json",
}

REQUIRED_STATEMENTS = (
    "BHSM full completion requires action-level or artifact-backed closure of all core sector projectors, mass/mixing laws, gauge/scalar normalization, admissible domains, dimensionful unit maps, and external runtime gates.",
    "BHSM currently has an integrated conditional structural architecture and unchanged frozen predictions.",
    "Physical eV/GeV neutrino mass closure remains open pending numeric neutral stiffness length sqrt(A_nu/Z_nu), physical K_neutral,eff in m^-2, and complete-action derivation of the admissible response cone.",
    "The full-completion ledger distinguishes artifact-backed closures, conditional candidates, runtime-gated items, and open theorem blockers.",
    "No empirical data, PDG values, W calibration, neutrino limits, or legacy particle threshold tables are used as theorem inputs.",
)

PUBLIC_STATUS = (
    "BHSM is an artifact-backed computational framework with an integrated conditional structural "
    "architecture and unchanged frozen predictions. Full completion is not claimed; physical eV/GeV "
    "neutrino mass and external HEP runtime integration remain open."
)


def build_full_completion_status_report(
    repository: str | Path | None = None,
) -> FullCompletionStatusReport:
    blockers = build_full_completion_blocker_ledger()
    priority = build_full_completion_priority_map()
    selected = select_highest_leverage_target()
    closure = build_boundary_measure_closure(repository)
    statuses = [blocker.current_status for blocker in blockers]
    return FullCompletionStatusReport(
        report_name="BHSM Full Completion Audit and Next Closure",
        version="1.6",
        full_completion_status="INTEGRATED_CONDITIONAL_ARCHITECTURE_WITH_OPEN_BLOCKERS",
        blockers=blockers,
        priority_rows=priority,
        selected_target=selected,
        closure_attempt=closure,
        completion_claimed=False,
        artifact_backed_count=statuses.count("ARTIFACT_BACKED"),
        conditional_count=statuses.count("CONDITIONAL"),
        open_count=sum(status.startswith("OPEN_") for status in statuses),
        runtime_gated_count=statuses.count("RUNTIME_GATED"),
        frozen_predictions_changed=False,
        official_prediction_logic_changed=False,
        empirical_inputs_used=False,
        internet_required=False,
        external_hep_tools_required=False,
        public_status=PUBLIC_STATUS,
        required_statements=REQUIRED_STATEMENTS,
    )


def full_completion_status_to_markdown(report: FullCompletionStatusReport) -> str:
    lines = [
        "# BHSM Full Completion Status",
        "",
        report.public_status,
        "",
        *report.required_statements,
        "",
        "## Completion Ledger",
        "",
        "| ID | Category | Sector | Class | Status |",
        "| --- | ---: | --- | --- | --- |",
    ]
    lines.extend(
        f"| `{row.blocker_id}` | {row.category_number} | {row.sector} | `{row.blocker_class}` | `{row.current_status}` |"
        for row in report.blockers
    )
    lines.extend([
        "",
        "## Selected Target",
        "",
        f"`{report.selected_target.target_id}`: {report.selected_target.title}",
        f"Score: `{report.selected_target.total_score}`",
        "",
        f"Closure result: `{report.closure_attempt.closure_result}`",
        f"Status after: `{report.closure_attempt.status_after}`",
        "",
        "The physical measure normalization and cross-scale transport remain open.",
        "No physical eV/GeV neutrino mass is emitted.",
    ])
    return "\n".join(lines) + "\n"


def _artifact_payloads(report: FullCompletionStatusReport) -> dict[str, dict[str, Any]]:
    return {
        "manifest": {
            "version": "1.6",
            "artifacts": ARTIFACT_PATHS,
            "selected_target": report.selected_target.target_id,
            "completion_claimed": False,
        },
        "ledger": {
            "blocker_classes": list({row.blocker_class for row in report.blockers}),
            "blocker_count": len(report.blockers),
            "blockers": [row.to_dict() for row in report.blockers],
        },
        "priority": {
            "scoring_formula": "necessity + artifact_locality + no_empirical_path + cross_sector_leverage + feasibility_now - external_runtime_penalty",
            "selected_target": report.selected_target.target_id,
            "rows": [row.to_dict() for row in report.priority_rows],
        },
        "selected": {
            **report.selected_target.to_dict(),
            "selected_by_explicit_scoring": True,
            "observed_residuals_used": False,
        },
        "closure": report.closure_attempt.to_dict(),
        "status": {
            "full_completion_status": report.full_completion_status,
            "completion_claimed": report.completion_claimed,
            "dimensionless_propagation_closure_status": DIMENSIONLESS_PROPAGATION_CLOSURE_STATUS,
            "neutral_spectral_mass_theorem_status": NEUTRAL_SPECTRAL_MASS_THEOREM_STATUS,
            "measurement_supported_admissible_positivity_status": MEASUREMENT_SUPPORTED_ADMISSIBLE_POSITIVITY_STATUS,
            "action_derived_response_cone_status": ACTION_DERIVED_RESPONSE_CONE_STATUS,
            "dimensionful_ev_gev_mass_closure_status": DIMENSIONFUL_EV_GEV_MASS_CLOSURE_STATUS,
            "public_status": report.public_status,
            "required_statements": list(report.required_statements),
            "frozen_predictions_changed": False,
            "official_prediction_logic_changed": False,
            "empirical_inputs_used": False,
            "physical_mass_emitted": False,
        },
        "claims": {
            "allowed": [
                "BHSM has an integrated conditional structural architecture.",
                "The collar Jacobian shape and same-scale identity transport have a conditional/exact partial closure.",
                "The completion ledger is an obstruction and priority map, not a full-completion claim.",
            ],
            "forbidden": [
                "BHSM is fully complete.",
                "BHSM is empirically validated.",
                "The raw neutral kernel is positive semidefinite.",
                "A physical eV/GeV neutrino mass has been derived.",
                "FeynRules, UFO, or MadGraph readiness has been established.",
            ],
            "empirical_inputs_used": False,
            "frozen_predictions_changed": False,
        },
    }


def write_full_completion_artifacts(repository: str | Path | None = None) -> tuple[Path, ...]:
    root = repository_root(repository)
    report = build_full_completion_status_report(root)
    written = []
    for key, payload in _artifact_payloads(report).items():
        destination = root / ARTIFACT_PATHS[key]
        destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(destination)
    return tuple(written)
