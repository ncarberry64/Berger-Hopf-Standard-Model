"""Adapters for the existing no-fit BHSM boundary package."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .artifact_sources import load_artifact_json, repository_root
from .provenance import ProvenanceRecord, ValueWithProvenance, missing_artifact_value

BOUNDARY_PATH = "artifacts/BHSM_boundary_no_fit_prediction_package_v1.json"


def _load_boundary_section(
    value_key: str,
    field: str,
    value_kind: str,
    claim_status: str,
    repository: str | Path | None = None,
) -> ValueWithProvenance:
    root = Path(repository).resolve() if repository is not None else repository_root()
    path = root / BOUNDARY_PATH
    if not path.is_file():
        return missing_artifact_value(value_key, BOUNDARY_PATH, value_kind=value_kind)
    payload: dict[str, Any] = load_artifact_json(path)
    if field not in payload:
        return missing_artifact_value(
            value_key,
            BOUNDARY_PATH,
            value_kind=value_kind,
            notes=(f"Required boundary field {field!r} was not found; no value was inferred.",),
        )
    return ValueWithProvenance(
        value_key=value_key,
        value=payload[field],
        unit="dimensionless",
        value_kind=value_kind,
        provenance=ProvenanceRecord(
            source_path=BOUNDARY_PATH,
            source_artifact_key=str(payload.get("artifact", path.stem)),
            source_field=field,
            source_status="DISCOVERED",
            loaded_at_runtime=True,
            empirical_derivation_input=bool(payload.get("empirical_derivation_inputs_used", False)),
            calibration_input=False,
            reference_comparison_input=False,
            frozen_prediction=True,
            claim_status=claim_status,
            notes=("Loaded from the existing internal no-fit boundary package.",),
        ),
        metadata={
            "public_status": payload.get("public_status"),
            "official_predictions_changed": payload.get("official_predictions_changed"),
        },
    )


def load_boundary_constants_artifact(repository: str | Path | None = None) -> ValueWithProvenance:
    return _load_boundary_section(
        "boundary_constants",
        "profile_scale",
        "constant_bundle",
        "ARTIFACT_BACKED_INTERNAL_BOUNDARY_CONSTANTS",
        repository,
    )


def load_charged_bridge_constants_artifact(repository: str | Path | None = None) -> ValueWithProvenance:
    return _load_boundary_section(
        "charged_bridge_constants",
        "charged_boundary_values",
        "charged_boundary_bundle",
        "ARTIFACT_BACKED_CONDITIONAL_CHARGED_BOUNDARY_VALUES",
        repository,
    )


def load_neutral_operator_artifact(repository: str | Path | None = None) -> ValueWithProvenance:
    return _load_boundary_section(
        "neutral_operator_kernel_BH",
        "neutral_operator",
        "neutral_operator_seed",
        "BOUNDARY_KERNEL_ARTIFACT_PHYSICAL_BASIS_SCALE_OPEN",
        repository,
    )
