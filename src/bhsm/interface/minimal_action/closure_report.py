"""Build and export the ontology-aware minimal-action decision."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .action_terms import build_minimal_action_terms, load_minimal_action_axioms
from .author_ontology import AUTHOR_ONTOLOGY_PATH, load_author_ontology
from .common import MinimalActionClosureReport, MinimalActionClosureResult, STATUS_TAXONOMY, repository_path
from .cp_o_int_closure import close_cp_o_int
from .neutrino_basis_closure import close_neutrino_basis_scale
from .registry_updates import minimal_action_registry_updates
from .sector_projectors import build_sector_projectors, projectors_are_orthogonal
from .x_ch_closure import close_x_ch


ARTIFACT_PATHS = {
    "manifest": "artifacts/BHSM_minimal_action_closure_manifest_v0_8.json",
    "report": "artifacts/BHSM_minimal_action_report_v0_8.json",
    "cp_o_int": "artifacts/BHSM_cp_o_int_minimal_action_closure_v0_8.json",
    "X_ch": "artifacts/BHSM_x_ch_minimal_action_closure_v0_8.json",
    "neutrino_basis_scale": "artifacts/BHSM_neutrino_basis_scale_minimal_action_closure_v0_8.json",
    "registry": "artifacts/BHSM_minimal_action_registry_updates_v0_8.json",
    "claims": "artifacts/BHSM_minimal_action_claim_policy_v0_8.json",
}


def build_minimal_action_report(
    repository: str | Path | None = None,
    axioms: Mapping[str, Any] | None = None,
) -> MinimalActionClosureReport:
    projectors = build_sector_projectors()
    if not projectors_are_orthogonal(projectors):
        raise ValueError("minimal sector projectors are not orthogonal")
    results = (
        close_cp_o_int(repository, axioms),
        close_x_ch(repository, axioms),
        close_neutrino_basis_scale(repository, axioms),
    )
    return MinimalActionClosureReport(
        action_symbol="S_BHSM,min",
        action_expression="S_boundary + S_sector + S_phase + S_charged + S_neutral",
        terms=build_minimal_action_terms(),
        sector_projectors=projectors,
        results=results,
    )


def close_minimal_action(
    theorem_key: str,
    repository: str | Path | None = None,
    axioms: Mapping[str, Any] | None = None,
) -> MinimalActionClosureResult:
    aliases = {
        "cp_o_int": close_cp_o_int,
        "X_ch": close_x_ch,
        "neutrino_basis_scale": close_neutrino_basis_scale,
    }
    try:
        return aliases[theorem_key](repository, axioms)
    except KeyError as exc:
        raise KeyError(f"unknown minimal-action theorem: {theorem_key}") from exc


def minimal_action_status(report: MinimalActionClosureReport | None = None) -> dict[str, Any]:
    selected = report or build_minimal_action_report()
    return {
        "report_name": selected.report_name,
        "version": selected.version,
        "statuses": {row.theorem_key: row.status_after for row in selected.results},
        "promoted": [row.theorem_key for row in selected.results if row.promoted],
        "core_blockers": [row.theorem_key for row in selected.results if row.core_blocker],
        "retired_targets": [row.theorem_key for row in selected.results if row.target_disposition == "RETIRED_TARGET"],
        "numerical_closure_open": [row.theorem_key for row in selected.results if row.numerical_closure_open],
        "runtime_gates_changed": any(row.runtime_gates_changed for row in selected.results),
        "frozen_predictions_changed": selected.frozen_predictions_changed,
        "internet_required": selected.internet_required,
    }


def minimal_action_report_to_markdown(report: MinimalActionClosureReport) -> str:
    lines = [
        "# BHSM Minimal Action Closure",
        "",
        f"`{report.action_symbol} = {report.action_expression}`",
        "",
        "| Theorem | Status | Promoted | Remaining object |",
        "| --- | --- | ---: | --- |",
    ]
    for row in report.results:
        lines.append(
            f"| `{row.theorem_key}` | `{row.status_after}` | `{str(row.promoted).lower()}` | {row.remaining_missing_object or 'none'} |"
        )
    lines.extend(
        [
            "",
            "The report uses the author ontology plus local artifacts. Runtime HEP gates and frozen predictions are unchanged.",
            "",
        ]
    )
    return "\n".join(lines)


def _manifest(report: MinimalActionClosureReport) -> dict[str, Any]:
    return {
        "artifact_name": "BHSM Minimal Action Closure Manifest",
        "version": "0.8",
        "action_expression": report.action_expression,
        "status_taxonomy": list(STATUS_TAXONOMY),
        "results": {row.theorem_key: row.status_after for row in report.results},
        "promotions": [row.theorem_key for row in report.results if row.promoted],
        "artifact_paths": [*ARTIFACT_PATHS.values(), AUTHOR_ONTOLOGY_PATH],
        "axiom_template": "data/theorem_inputs/minimal_action_axioms_template.json",
        "axiom_template_enabled": any(row.get("enabled") is True for row in load_minimal_action_axioms().get("axioms", [])),
        "author_ontology": AUTHOR_ONTOLOGY_PATH,
        "author_ontology_status": load_author_ontology()["source_status"],
        "frozen_predictions_changed": False,
        "production_physics_model_logic_changed": False,
        "empirical_derivation_inputs_used": False,
        "reference_values_used_as_theorem_inputs": False,
        "pdg_values_used_as_theorem_inputs": False,
        "w_calibration_used_as_theorem_input": False,
        "internet_required": False,
        "external_hep_tools_required": False,
    }


def _claim_policy(report: MinimalActionClosureReport) -> dict[str, Any]:
    return {
        "artifact_name": "BHSM Minimal Action Claim Policy",
        "version": "0.8",
        "allowed": [
            "A minimal action-closure evaluator exists.",
            "The CP/Z6 holonomy and phase attachment are artifact-backed; a standalone CP O_int production vertex is a retired target.",
            "X_ch is a conditional charged boundary-response action theorem under the author ontology.",
            "Neutrino BHSM mass is a conditional propagation-locked curvature-response theorem under the author ontology.",
        ],
        "unsupported": [
            "empirical validation",
            "complete 4D Lagrangian export",
            "validated FeynRules, UFO, or MadGraph readiness",
            "production promotion of any open minimal-action theorem",
            "a static neutrino rest-mass matrix derived from the propagation theorem",
        ],
        "statuses": {row.theorem_key: row.status_after for row in report.results},
        "claim_boundaries_preserved": True,
        "public_status": report.public_status,
    }


def write_minimal_action_artifacts(
    repository: str | Path | None = None,
    axioms: Mapping[str, Any] | None = None,
) -> MinimalActionClosureReport:
    root = repository_path(repository)
    report = build_minimal_action_report(root, axioms)
    payloads: dict[str, Any] = {
        "manifest": _manifest(report),
        "report": report.to_dict(),
        "cp_o_int": report.results[0].to_dict(),
        "X_ch": report.results[1].to_dict(),
        "neutrino_basis_scale": report.results[2].to_dict(),
        "registry": minimal_action_registry_updates(report.results),
        "claims": _claim_policy(report),
    }
    for key, relative in ARTIFACT_PATHS.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payloads[key], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
