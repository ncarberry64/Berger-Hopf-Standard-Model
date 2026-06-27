"""Assemble and export the neutral dimensionful-scale closure audit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .boundary_measure import analyze_neutral_boundary_measure
from .common import NeutralScaleClosureReport, repository_path
from .neutral_scale_candidates import build_neutral_scale_candidates
from .threshold_energy_map import build_threshold_energy_map
from .unit_map import derive_neutral_scale_law, map_dimensionless_response


ARTIFACT_PATHS = {
    "manifest": "artifacts/BHSM_neutral_dimensionful_scale_manifest_v1_0.json",
    "candidates": "artifacts/BHSM_neutral_scale_candidates_v1_0.json",
    "threshold_map": "artifacts/BHSM_neutral_threshold_energy_map_v1_0.json",
    "boundary_measure": "artifacts/BHSM_neutral_boundary_measure_v1_0.json",
    "scale_law": "artifacts/BHSM_neutral_scale_law_v1_0.json",
    "mass_attempt": "artifacts/BHSM_neutrino_dimensionful_mass_attempt_v1_0.json",
    "report": "artifacts/BHSM_neutral_scale_closure_report_v1_0.json",
    "claims": "artifacts/BHSM_neutral_scale_claim_policy_v1_0.json",
}


REQUIRED_STATEMENTS = (
    "BHSM currently distinguishes dimensionless neutrino propagation closure from physical eV/GeV mass closure.",
    "A physical eV/GeV neutrino mass requires an artifact-backed or explicitly conditional neutral dimensionful scale.",
    "The electron-neutrino upper limit is a comparison reference only and is never used to set the neutral scale.",
    "A dimensionless BHSM response is not, by itself, a physical eV/GeV mass.",
)


def build_neutral_scale_report(
    repository: str | Path | None = None,
) -> NeutralScaleClosureReport:
    from ..neutrino_propagation.numerical_closure import build_numerical_closure

    root = repository_path(repository)
    numerical = build_numerical_closure(root)
    scale = derive_neutral_scale_law(root)
    attempts = tuple(
        map_dimensionless_response(row.effective_mass_dimensionless, scale)
        for row in numerical.channel_results
    )
    return NeutralScaleClosureReport(
        report_name="BHSM Neutral Dimensionful Scale Closure",
        version="1.0",
        candidates=build_neutral_scale_candidates(root),
        boundary_measure=analyze_neutral_boundary_measure(root),
        threshold_energy_map=build_threshold_energy_map(root),
        scale_result=scale,
        dimensionful_mass_attempt=attempts,
        neutrino_status_before=numerical.closure.status_after,
        neutrino_status_after=numerical.closure.status_after,
        dimensionful_scale_achieved=scale.unit_available,
        dimensionful_mass_output_produced=any(row.effective_mass_eV is not None for row in attempts),
        public_status="structural architecture integrated conditional; numerical closure open",
    )


def neutral_scale_report_to_markdown(report: NeutralScaleClosureReport) -> str:
    lines = [
        "# BHSM Neutral Dimensionful Scale Closure",
        "",
        f"Status: `{report.scale_result.status_after}`.",
        "",
        *REQUIRED_STATEMENTS,
        "",
        "| Candidate | Classification | Unit | eV map |",
        "| --- | --- | --- | --- |",
    ]
    for row in report.candidates:
        lines.append(
            f"| `{row.candidate_key}` | `{row.status}` | {row.unit or 'none'} | {'yes' if row.can_map_to_eV else 'no'} |"
        )
    lines.extend(
        [
            "",
            f"Boundary measure: `{report.boundary_measure.status}`.",
            f"Threshold-to-energy map: `{report.threshold_energy_map.status}`.",
            f"Remaining object: {report.scale_result.remaining_missing_object}.",
            "",
        ]
    )
    return "\n".join(lines)


def _claim_policy() -> dict[str, Any]:
    return {
        "artifact_name": "BHSM Neutral Dimensionful Scale Claim Policy",
        "version": "1.0",
        "allowed": [
            "BHSM includes a neutral dimensionful scale search.",
            "BHSM distinguishes dimensionless propagation closure from physical eV/GeV mass closure.",
            "BHSM does not use electron-neutrino upper limits, PDG values, W calibration, or empirical fitting as neutral-scale theorem inputs.",
            "A dimensionful neutrino mass is only reported if a valid neutral scale source exists.",
        ],
        "forbidden": [
            "BHSM empirically validates neutrino mass.",
            "BHSM centrally measures electron-neutrino mass.",
            "The electron-neutrino upper limit is used to set the scale.",
            "PDG/reference values are theorem inputs.",
            "W calibration is used as the neutral scale.",
            "A dimensionless response alone is a physical eV/GeV mass.",
            "A conditional scale candidate is artifact-backed unless the artifact proves it.",
        ],
        "required_statements": list(REQUIRED_STATEMENTS),
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
    }


def write_neutral_scale_artifacts(
    repository: str | Path | None = None,
) -> NeutralScaleClosureReport:
    root = repository_path(repository)
    report = build_neutral_scale_report(root)
    payloads: dict[str, Any] = {
        "manifest": {
            "artifact_name": "BHSM Neutral Dimensionful Scale Manifest",
            "version": "1.0",
            "artifact_paths": list(ARTIFACT_PATHS.values()),
            "status": report.scale_result.status_after,
            "dimensionful_scale_achieved": report.dimensionful_scale_achieved,
            "frozen_predictions_changed": False,
            "internet_required": False,
        },
        "candidates": {"candidates": [row.to_dict() for row in report.candidates]},
        "threshold_map": report.threshold_energy_map.to_dict(),
        "boundary_measure": report.boundary_measure.to_dict(),
        "scale_law": report.scale_result.to_dict(),
        "mass_attempt": {
            "status": report.scale_result.status_after,
            "dimensionful_mass_output_produced": report.dimensionful_mass_output_produced,
            "channel_results": [row.to_dict() for row in report.dimensionful_mass_attempt],
        },
        "report": report.to_dict(),
        "claims": _claim_policy(),
    }
    for key, relative in ARTIFACT_PATHS.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payloads[key], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report

