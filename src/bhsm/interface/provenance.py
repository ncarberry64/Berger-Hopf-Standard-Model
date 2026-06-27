"""JSON-safe provenance records for local BHSM artifact values."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProvenanceRecord:
    """Describe one local source without implying empirical validation."""

    source_path: str
    source_artifact_key: str
    source_field: str
    source_status: str
    loaded_at_runtime: bool
    empirical_derivation_input: bool
    calibration_input: bool
    reference_comparison_input: bool
    frozen_prediction: bool
    claim_status: str
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["notes"] = list(self.notes)
        return payload


@dataclass(frozen=True)
class ProvenanceChain:
    """Ordered source chain for a value assembled from multiple artifacts."""

    records: tuple[ProvenanceRecord, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"records": [record.to_dict() for record in self.records]}


@dataclass(frozen=True)
class ValueWithProvenance:
    """A JSON-serializable value plus explicit scientific-use boundaries."""

    value_key: str
    value: Any
    unit: str
    value_kind: str
    provenance: ProvenanceRecord
    provenance_chain: ProvenanceChain | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def source_status(self) -> str:
        return self.provenance.source_status

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "value_key": self.value_key,
            "value": self.value,
            "unit": self.unit,
            "value_kind": self.value_kind,
            **self.provenance.to_dict(),
            "metadata": dict(self.metadata),
        }
        if self.provenance_chain is not None:
            payload["provenance_chain"] = self.provenance_chain.to_dict()
        return payload


def missing_artifact_value(
    value_key: str,
    expected_path: str,
    *,
    value_kind: str,
    unit: str = "dimensionless",
    notes: tuple[str, ...] = (),
) -> ValueWithProvenance:
    """Return the required structured missing result instead of a fallback."""

    return ValueWithProvenance(
        value_key=value_key,
        value=None,
        unit=unit,
        value_kind=value_kind,
        provenance=ProvenanceRecord(
            source_path=expected_path,
            source_artifact_key=value_key,
            source_field="",
            source_status="ARTIFACT_NOT_FOUND",
            loaded_at_runtime=False,
            empirical_derivation_input=False,
            calibration_input=False,
            reference_comparison_input=False,
            frozen_prediction=False,
            claim_status="MISSING_NOT_INFERRED",
            notes=notes or ("Missing artifacts are reported as missing, not inferred.",),
        ),
    )
