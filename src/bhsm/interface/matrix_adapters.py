"""Adapters for existing machine-readable BHSM matrix artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .artifact_sources import load_artifact_json, repository_root
from .provenance import ProvenanceRecord, ValueWithProvenance, missing_artifact_value

CKM_PATH = "artifacts/CKM_no_fit_operator_output_v1.json"
PMNS_PATH = "artifacts/PMNS_no_fit_operator_output_v1.json"
CP_PATH = "artifacts/CP_no_fit_holonomy_output_v1.json"


def _load_matrix_value(
    value_key: str,
    relative_path: str,
    field: str,
    *,
    repository: str | Path | None = None,
    claim_status: str,
) -> ValueWithProvenance:
    root = Path(repository).resolve() if repository is not None else repository_root()
    path = root / relative_path
    if not path.is_file():
        return missing_artifact_value(value_key, relative_path, value_kind="matrix")
    payload = load_artifact_json(path)
    if not isinstance(payload, dict) or field not in payload:
        return missing_artifact_value(
            value_key,
            relative_path,
            value_kind="matrix",
            notes=(f"Required field {field!r} was not found; no value was inferred.",),
        )
    artifact_key = str(payload.get("artifact", path.stem))
    return ValueWithProvenance(
        value_key=value_key,
        value=payload[field],
        unit="dimensionless",
        value_kind="matrix",
        provenance=ProvenanceRecord(
            source_path=relative_path,
            source_artifact_key=artifact_key,
            source_field=field,
            source_status="DISCOVERED",
            loaded_at_runtime=True,
            empirical_derivation_input=bool(payload.get("empirical_derivation_inputs_used", False)),
            calibration_input=False,
            reference_comparison_input=False,
            frozen_prediction=True,
            claim_status=claim_status,
            notes=("Loaded from an existing local BHSM machine-readable artifact.",),
        ),
        metadata={
            "public_status": payload.get("public_status"),
            "official_predictions_changed": payload.get("official_predictions_changed"),
        },
    )


def load_ckm_matrix_artifact(repository: str | Path | None = None) -> ValueWithProvenance:
    return _load_matrix_value(
        "CKM_matrix_BHSM",
        CKM_PATH,
        "magnitude_matrix",
        repository=repository,
        claim_status="ARTIFACT_BACKED_INTERNAL_OUTPUT_NOT_EMPIRICAL_VALIDATION",
    )


def load_pmns_matrix_artifact(repository: str | Path | None = None) -> ValueWithProvenance:
    return _load_matrix_value(
        "PMNS_matrix_BHSM",
        PMNS_PATH,
        "magnitude_matrix",
        repository=repository,
        claim_status="ARTIFACT_BACKED_EFFECTIVE_EXTENSION_OUTPUT",
    )


def load_cp_phase_artifact(repository: str | Path | None = None) -> ValueWithProvenance:
    root = Path(repository).resolve() if repository is not None else repository_root()
    path = root / CP_PATH
    if not path.is_file():
        return missing_artifact_value("cp_holonomy_phase_attachment", CP_PATH, value_kind="phase")
    payload: dict[str, Any] = load_artifact_json(path)
    required = ("delta_BH", "delta_BH_formula", "Z6_boundary_phase")
    if not all(field in payload for field in required):
        return missing_artifact_value(
            "cp_holonomy_phase_attachment",
            CP_PATH,
            value_kind="phase",
            notes=("Required CP phase fields were not found; no phase was inferred.",),
        )
    return ValueWithProvenance(
        value_key="cp_holonomy_phase_attachment",
        value={field: payload[field] for field in required},
        unit="radian and dimensionless phase",
        value_kind="complex_phase",
        provenance=ProvenanceRecord(
            source_path=CP_PATH,
            source_artifact_key=str(payload.get("artifact", path.stem)),
            source_field="delta_BH,delta_BH_formula,Z6_boundary_phase",
            source_status="DISCOVERED",
            loaded_at_runtime=True,
            empirical_derivation_input=bool(payload.get("empirical_derivation_inputs_used", False)),
            calibration_input=False,
            reference_comparison_input=False,
            frozen_prediction=True,
            claim_status="PHASE_ARTIFACT_AVAILABLE_STANDALONE_O_INT_REMAINS_OPEN",
            notes=("Artifact-backed phase seed; not a standalone production CP vertex.",),
        ),
        metadata={"CP_boundary_holonomy": payload.get("CP_boundary_holonomy")},
    )
