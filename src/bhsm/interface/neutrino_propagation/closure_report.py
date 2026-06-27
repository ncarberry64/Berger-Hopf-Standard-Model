"""Export the neutrino propagation-mass candidate and claim policy."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .common import NeutrinoNumericalClosureReport, repository_path
from .numerical_closure import build_numerical_closure
from .validation_policy import neutrino_validation_policy


ARTIFACT_PATHS = {
    "manifest": "artifacts/BHSM_neutrino_propagation_mass_manifest_v0_9.json",
    "theorem": "artifacts/BHSM_neutrino_propagation_theorem_v0_9.json",
    "threshold": "artifacts/BHSM_neutrino_curvature_threshold_v0_9.json",
    "scale": "artifacts/BHSM_neutrino_scale_law_v0_9.json",
    "effective_mass": "artifacts/BHSM_neutrino_effective_mass_candidate_v0_9.json",
    "observable": "artifacts/BHSM_neutrino_observable_map_v0_9.json",
    "report": "artifacts/BHSM_neutrino_numerical_closure_report_v0_9.json",
    "claims": "artifacts/BHSM_neutrino_claim_policy_v0_9.json",
}


def build_neutrino_propagation_report(
    repository: str | Path | None = None,
) -> NeutrinoNumericalClosureReport:
    return build_numerical_closure(repository)


def neutrino_propagation_report_to_markdown(
    report: NeutrinoNumericalClosureReport,
) -> str:
    lines = [
        "# BHSM Neutrino Propagation-Mass Numerical Closure",
        "",
        f"Status: `{report.closure.status_after}`.",
        f"Numerical closure: `{report.numerical_closure}`.",
        "",
        "| Boundary state | Kernel response | Threshold excess | Effective mass (dimensionless) |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in report.channel_results:
        lines.append(
            f"| `{row.state_label}` | {row.kernel_response_norm:.12g} | {row.threshold_excess:.12g} | {row.effective_mass_dimensionless:.12g} |"
        )
    lines.extend(
        [
            "",
            f"Remaining object: {report.closure.remaining_missing_object}.",
            "",
            "The result is dimensionless and conditional. It is not a static rest-mass matrix or an eV/GeV neutrino prediction.",
            "",
        ]
    )
    return "\n".join(lines)


def _claim_policy() -> dict[str, Any]:
    return {
        "artifact_name": "BHSM Neutrino Propagation-Mass Claim Policy",
        "version": "0.9",
        "allowed": [
            "BHSM includes a conditional neutrino propagation-mass theorem.",
            "BHSM treats the neutrino BHSM mass contribution as propagation-locked curvature response.",
            "If propagation response is zero, the BHSM mass contribution vanishes.",
            "The sprint attempts numerical closure using BHSM artifacts only.",
            "Electron-neutrino comparisons remain upper-limit comparisons by default.",
        ],
        "forbidden": [
            "BHSM empirically validates neutrino mass.",
            "BHSM centrally measures electron-neutrino mass.",
            "The electron-neutrino upper limit is used as a derivation input.",
            "PDG/reference values are theorem inputs.",
            "W calibration is used as neutrino theorem input.",
            "BHSM neutrino propagation mass is automatically an ordinary static rest mass.",
            "Dirac/Majorana closure is claimed without a dedicated theorem.",
        ],
        "validation_policy": neutrino_validation_policy(),
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
    }


def write_neutrino_propagation_artifacts(
    repository: str | Path | None = None,
) -> NeutrinoNumericalClosureReport:
    root = repository_path(repository)
    report = build_neutrino_propagation_report(root)
    closure = report.closure
    payloads: dict[str, Any] = {
        "manifest": {
            "artifact_name": "BHSM Neutrino Propagation-Mass Manifest",
            "version": "0.9",
            "artifact_paths": list(ARTIFACT_PATHS.values()),
            "status": closure.status_after,
            "numerical_closure": report.numerical_closure,
            "remaining_missing_object": closure.remaining_missing_object,
            "frozen_predictions_changed": False,
            "internet_required": False,
        },
        "theorem": closure.to_dict(),
        "threshold": closure.curvature_threshold.to_dict(),
        "scale": closure.scale_law.to_dict(),
        "effective_mass": {
            "formula": closure.effective_mass_formula,
            "channel_results": [row.to_dict() for row in report.channel_results],
            "status": closure.status_after,
        },
        "observable": closure.observable_map.to_dict(),
        "report": report.to_dict(),
        "claims": _claim_policy(),
    }
    for key, relative in ARTIFACT_PATHS.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payloads[key], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
