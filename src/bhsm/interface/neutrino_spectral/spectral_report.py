"""Assemble and export the BHSM neutral spectral-stiffness report."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..neutrino_scale.common import repository_path
from .common import NeutralSpectralMassReport
from .legacy_dimensional_gate import audit_legacy_gravitational_mass_formula_dimensions
from .mass_gap_action import load_neutral_mass_gap_action
from .neutral_kernel_positivity import audit_neutral_kernel_positivity
from .neutral_spectral_gap import build_neutral_spectral_gap_candidate
from .stiffness_ratio import search_neutral_stiffness_ratio


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"
ARTIFACT_PATHS = {
    "manifest": "artifacts/BHSM_neutral_spectral_manifest_v1_3.json",
    "action": "artifacts/BHSM_mass_gap_action_candidate_v1_3.json",
    "legacy_gate": "artifacts/BHSM_legacy_dimensional_gate_v1_3.json",
    "stiffness": "artifacts/BHSM_neutral_stiffness_ratio_v1_3.json",
    "gap": "artifacts/BHSM_neutral_spectral_gap_candidate_v1_3.json",
    "positivity": "artifacts/BHSM_neutral_kernel_positivity_audit_v1_3.json",
    "report": "artifacts/BHSM_neutral_spectral_report_v1_3.json",
    "claims": "artifacts/BHSM_neutral_spectral_claim_policy_v1_3.json",
}

REQUIRED_STATEMENTS = (
    "The legacy gravitational curvature expression is dimensionally gated because K has units L^-2 and (c^2/G) r^2 K has units M/L, not M.",
    "BHSM does not use the legacy gravitational curvature expression as a direct particle mass formula.",
    "The neutral spectral-gap candidate has the symbolic form m_nu c^2 = hbar c sqrt(A_nu/Z_nu) K_neutral,eff.",
    "A physical eV/GeV neutrino mass requires a numeric neutral stiffness length and a physical neutral curvature map.",
    "BHSM does not use neutrino limits, PDG values, W calibration, empirical fitting, or legacy particle threshold tables to set the neutral spectral scale.",
)


def build_neutral_spectral_report(
    repository: str | Path | None = None,
) -> NeutralSpectralMassReport:
    root = repository_path(repository)
    action = load_neutral_mass_gap_action(root)
    legacy_gate = audit_legacy_gravitational_mass_formula_dimensions(root)
    ratio = search_neutral_stiffness_ratio(root)
    gap = build_neutral_spectral_gap_candidate(root)
    positivity = audit_neutral_kernel_positivity(root)
    return NeutralSpectralMassReport(
        report_name="BHSM Neutral Spectral Stiffness and Mass-Gap Theorem",
        version="1.3",
        public_status=PUBLIC_STATUS,
        mass_gap_action=action,
        legacy_dimensional_gate=legacy_gate,
        stiffness_ratio=ratio,
        spectral_gap=gap,
        kernel_positivity=positivity,
        dimensionful_mass_available=False,
        remaining_missing_object=(
            "numeric action-derived sqrt(A_nu/Z_nu) in metres; physical K_neutral,eff in m^-2; "
            "admissible neutral-kernel positivity proof"
        ),
        frozen_predictions_changed=False,
        production_physics_model_logic_changed=False,
        empirical_derivation_inputs_used=False,
        internet_required=False,
        external_hep_tools_required=False,
        libreoffice_required=False,
    )


def neutral_spectral_report_to_markdown(report: NeutralSpectralMassReport) -> str:
    rows = (
        ("Mass-gap action", report.mass_gap_action.status),
        ("Legacy dimensional gate", report.legacy_dimensional_gate.status),
        ("Neutral stiffness ratio", report.stiffness_ratio.status),
        ("Neutral spectral gap", report.spectral_gap.status),
        ("Neutral kernel positivity", report.kernel_positivity.status),
        ("Dimensionful mass", "DIMENSIONFUL_MASS_NOT_AVAILABLE"),
    )
    lines = [
        "# BHSM Neutral Spectral Stiffness Report",
        "",
        f"Public status: `{report.public_status}`.",
        "",
        *REQUIRED_STATEMENTS,
        "",
        "| Gate | Status |",
        "| --- | --- |",
        *(f"| {name} | `{status}` |" for name, status in rows),
        "",
        f"Raw neutral-kernel eigenvalues: `{list(report.kernel_positivity.raw_eigenvalues)}`.",
        "",
        f"Remaining object: {report.remaining_missing_object}.",
        "",
    ]
    return "\n".join(lines)


def _claim_policy() -> dict[str, Any]:
    return {
        "artifact_name": "BHSM Neutral Spectral Claim Policy",
        "version": "1.3",
        "allowed": [
            "BHSM has an artifact-backed scalar topographic mass-gap action analogue.",
            "BHSM has a conditional neutral spectral-gap theorem shape.",
            "The neutral spectral mass candidate requires a neutral stiffness ratio and a physical neutral curvature map.",
            "The legacy gravitational curvature expression is dimensionally gated and is not used as a direct particle mass formula.",
        ],
        "forbidden": [
            "BHSM empirically validates neutrino mass.",
            "BHSM centrally measures electron-neutrino mass.",
            "The electron-neutrino upper limit is used to set the neutral stiffness ratio.",
            "PDG/reference values are theorem inputs.",
            "W calibration is used as the neutral scale.",
            "Legacy particle threshold tables are no-fit BHSM derivations.",
            "The legacy gravitational formula directly produces physical particle mass under K=L^-2.",
            "A symbolic spectral-gap theorem produces a physical eV/GeV mass by itself.",
            "Raw neutral kernel positivity is claimed if only projected/admissible positivity is shown.",
        ],
        "required_statements": list(REQUIRED_STATEMENTS),
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
    }


def write_neutral_spectral_artifacts(
    repository: str | Path | None = None,
) -> NeutralSpectralMassReport:
    root = repository_path(repository)
    report = build_neutral_spectral_report(root)
    report_dict = report.to_dict()
    payloads: dict[str, Any] = {
        "manifest": {
            "artifact_name": "BHSM Neutral Spectral Manifest",
            "version": "1.3",
            "artifact_paths": list(ARTIFACT_PATHS.values()),
            "public_status": PUBLIC_STATUS,
            "dimensionful_mass_output_produced": False,
            "frozen_predictions_changed": False,
        },
        "action": report.mass_gap_action.to_dict(),
        "legacy_gate": report.legacy_dimensional_gate.to_dict(),
        "stiffness": report.stiffness_ratio.to_dict(),
        "gap": report.spectral_gap.to_dict(),
        "positivity": report.kernel_positivity.to_dict(),
        "report": report_dict,
        "claims": _claim_policy(),
    }
    for key, relative in ARTIFACT_PATHS.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payloads[key], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
