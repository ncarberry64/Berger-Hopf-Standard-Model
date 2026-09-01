"""Single-calibration dimensional map for BHSM 1.0.

BHSM supplies a dimensionless action coefficient ``c_F`` and adopts the one
owner-authorized physical calibration ``G_F = c_F / Lambda^2``.  The resulting
``Lambda`` is shared by every sector.  This module deliberately has no API for
sector-specific scales or observable-by-observable retuning.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class UniversalGFScaleMap:
    dimensionless_fermi_coefficient: float
    fermi_constant: float
    action_version: str
    background_id: str
    coefficient_provenance: tuple[str, ...]
    calibration_provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        values = (self.dimensionless_fermi_coefficient, self.fermi_constant)
        if any(not math.isfinite(value) or value <= 0.0 for value in values):
            raise ValueError("Fermi coefficient and calibration must be finite and positive")
        if not self.coefficient_provenance:
            raise ValueError("action-derived Fermi coefficient provenance is required")
        if not self.calibration_provenance:
            raise ValueError("G_F calibration provenance is required")

    @property
    def mass_scale(self) -> float:
        return math.sqrt(self.dimensionless_fermi_coefficient / self.fermi_constant)

    @property
    def length_scale(self) -> float:
        return 1.0 / self.mass_scale

    @property
    def scale_map_id(self) -> str:
        return f"GF:{self.action_version}:{self.background_id}"

    def mass(self, dimensionless_mass: float) -> float:
        self._require_finite(dimensionless_mass)
        if dimensionless_mass < 0.0:
            raise ValueError("dimensionless mass must be nonnegative")
        return dimensionless_mass * self.mass_scale

    def width(self, dimensionless_width: float) -> float:
        self._require_finite(dimensionless_width)
        if dimensionless_width < 0.0:
            raise ValueError("dimensionless width must be nonnegative")
        return dimensionless_width * self.mass_scale

    def inverse_mass_squared(self, dimensionless_value: float) -> float:
        """Convert an area/cross-section coefficient in natural units."""

        self._require_finite(dimensionless_value)
        if dimensionless_value < 0.0:
            raise ValueError("dimensionless inverse-mass-squared value must be nonnegative")
        return dimensionless_value / self.mass_scale**2

    def metadata(self) -> dict:
        return {
            "scale_map_id": self.scale_map_id,
            "action_version": self.action_version,
            "background_id": self.background_id,
            "calibration_count": 1,
            "calibration_observable": "G_F",
            "relation": "G_F=c_F/Lambda^2",
            "sector_specific_scales_allowed": False,
            "prediction_retuning_allowed": False,
            "coefficient_provenance": list(self.coefficient_provenance),
            "calibration_provenance": list(self.calibration_provenance),
        }

    @staticmethod
    def _require_finite(value: float) -> None:
        if not math.isfinite(value):
            raise ValueError("scale-map input must be finite")


__all__ = ["UniversalGFScaleMap"]
