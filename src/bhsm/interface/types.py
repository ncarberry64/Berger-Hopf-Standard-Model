"""Shared serializable records for the BHSM computational interface."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class CalibrationMetadata:
    """Describe a geometric-to-physical unit calibration."""

    scale_gev_per_tension: float
    anchor_particle: str | None = None
    anchor_mass_gev: float | None = None
    anchor_source: str | None = None
    calibration_mode: str = "UNCALIBRATED"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PredictionResult:
    """Minimal common prediction payload used by downstream interfaces."""

    particle_key: str
    mass_gev: float | None
    status: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ParticleReference:
    """Portable external-reference record."""

    particle_key: str
    reference_kind: str
    source_label: str
    value_gev: float | None = None
    uncertainty_gev: float | None = None
    upper_limit_gev: float | None = None
    lower_limit_gev: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ComparisonResult:
    """Portable validation-comparison record."""

    particle_key: str
    reference_kind: str
    predicted_mass_gev: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
