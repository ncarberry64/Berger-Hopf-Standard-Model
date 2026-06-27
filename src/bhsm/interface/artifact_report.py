"""Combined reviewer report for artifact-backed BHSM interface values."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .artifact_adapters import ARTIFACT_ADAPTERS, compute_artifact
from .artifact_sources import discover_bhsm_artifacts
from .formula_registry import default_formula_registry
from .predictions import default_prediction_registry
from .theorem_blockers import default_theorem_blockers

WARNINGS = (
    "Artifact-backed outputs are local BHSM outputs with provenance, not empirical validation claims.",
    "Interface default formulas remain interface defaults unless a theorem-backed artifact or callable replaces them.",
    "Reference values, including PDG values, are comparison inputs only and are never BHSM derivation inputs.",
    "Missing artifacts are reported as missing, not inferred.",
    "Theorem blockers remain blockers unless explicit artifact-backed theorem support is present.",
)


@dataclass
class ArtifactPredictionReport:
    report_name: str
    release_basis: str
    anchor_particle: str | None
    artifact_sources_checked: int
    artifact_backed_values: list[dict[str, Any]]
    interface_default_values: list[dict[str, Any]]
    reference_comparison_values: list[dict[str, Any]]
    calibration_inputs: list[dict[str, Any]]
    missing_artifacts: list[dict[str, Any]]
    missing_callables: list[str]
    callable_registry: dict[str, Any]
    prediction_registry_status: dict[str, Any]
    theorem_blocker_status: dict[str, Any]
    calibration_policy: str
    reference_policy: str
    warnings: list[str]
    claim_boundaries: list[str]
    empirical_derivation_inputs_used: bool
    reference_values_used_as_derivation_inputs: bool
    frozen_predictions_changed: bool
    internet_required: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_artifact_prediction_report(
    anchor_particle: str | None = "W_boson",
    repository: str | Path | None = None,
) -> ArtifactPredictionReport:
    discovery = discover_bhsm_artifacts(repository)
    values = [compute_artifact(key, repository).to_dict() for key in ARTIFACT_ADAPTERS]
    backed = [row for row in values if row["source_status"] == "DISCOVERED"]
    missing = [row for row in values if row["source_status"] == "ARTIFACT_NOT_FOUND"]
    formulas = default_formula_registry(repository).to_dict()
    defaults = [row for row in formulas["formula_entries"] if row["status"] == "AVAILABLE_INTERFACE_DEFAULT"]
    missing_callables = [row["formula_key"] for row in formulas["formula_entries"] if row["status"] in {"CALLABLE_NOT_AVAILABLE", "OPEN_THEOREM_REQUIRED"}]
    prediction_registry = default_prediction_registry()
    return ArtifactPredictionReport(
        report_name="BHSM Artifact-Backed Prediction Report",
        release_basis=f"{prediction_registry.release_basis}; artifact adapter v0.3",
        anchor_particle=anchor_particle,
        artifact_sources_checked=len(discovery.index.sources),
        artifact_backed_values=backed,
        interface_default_values=defaults,
        reference_comparison_values=[],
        calibration_inputs=[{"particle_key": anchor_particle, "role": "calibration_anchor", "value": None}] if anchor_particle else [],
        missing_artifacts=missing,
        missing_callables=missing_callables,
        callable_registry=formulas,
        prediction_registry_status={"registry_name": prediction_registry.registry_name, "entry_count": len(prediction_registry.entries)},
        theorem_blocker_status=default_theorem_blockers().to_dict(),
        calibration_policy="A calibration anchor is not an independent prediction in the same run.",
        reference_policy="Reference values are comparison inputs only and never BHSM derivation inputs.",
        warnings=list(WARNINGS),
        claim_boundaries=["Artifact presence does not close a theorem.", "Boundary seeds are not physical production vertices without their missing theorems."],
        empirical_derivation_inputs_used=any(row["empirical_derivation_input"] for row in backed),
        reference_values_used_as_derivation_inputs=False,
        frozen_predictions_changed=False,
    )


def artifact_report_to_markdown(report: ArtifactPredictionReport) -> str:
    lines = [
        "# BHSM Artifact-Backed Prediction Report",
        "",
        f"Calibration anchor: `{report.anchor_particle}`",
        f"Local sources checked: {report.artifact_sources_checked}",
        "",
        "## Artifact-backed values",
        "",
        "| Key | Kind | Source | Claim status |",
        "| --- | --- | --- | --- |",
    ]
    lines.extend(f"| `{row['value_key']}` | {row['value_kind']} | `{row['source_path']}` | `{row['claim_status']}` |" for row in report.artifact_backed_values)
    lines.extend(["", "## Missing callables", ""])
    lines.extend(f"- `{key}`" for key in report.missing_callables)
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- {warning}" for warning in report.warnings)
    return "\n".join(lines) + "\n"
