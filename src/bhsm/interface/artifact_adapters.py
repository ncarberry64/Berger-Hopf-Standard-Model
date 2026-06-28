"""Unified dispatch for claim-safe local BHSM artifact adapters."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from .boundary_adapters import load_boundary_constants_artifact
from .mass_ratio_adapters import load_mass_ratio_predictions_artifact
from .matrix_adapters import load_ckm_matrix_artifact, load_cp_phase_artifact, load_pmns_matrix_artifact
from .provenance import ValueWithProvenance, missing_artifact_value

ARTIFACT_ADAPTERS: dict[str, Callable[..., ValueWithProvenance]] = {
    "CKM_matrix_BHSM": load_ckm_matrix_artifact,
    "PMNS_matrix_BHSM": load_pmns_matrix_artifact,
    "cp_holonomy_phase_attachment": load_cp_phase_artifact,
    "boundary_constants": load_boundary_constants_artifact,
    "mass_ratios": load_mass_ratio_predictions_artifact,
}


def compute_artifact(artifact_key: str, repository: str | Path | None = None) -> ValueWithProvenance:
    loader = ARTIFACT_ADAPTERS.get(artifact_key)
    if loader is None:
        return missing_artifact_value(artifact_key, "", value_kind="unknown", notes=("No registered artifact adapter exists; no value was guessed.",))
    return loader(repository)


def artifact_prediction_values(repository: str | Path | None = None) -> dict[str, object]:
    values = [compute_artifact(key, repository).to_dict() for key in ARTIFACT_ADAPTERS]
    return {
        "report_name": "BHSM Artifact-Backed Predictions",
        "version": "0.3",
        "values": values,
        "artifact_backed_count": sum(row["source_status"] == "DISCOVERED" for row in values),
        "missing_count": sum(row["source_status"] == "ARTIFACT_NOT_FOUND" for row in values),
        "empirical_derivation_inputs_used": any(row["empirical_derivation_input"] for row in values),
        "reference_values_used_as_derivation_inputs": False,
        "frozen_predictions_changed": False,
    }
