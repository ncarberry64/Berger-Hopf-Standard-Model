"""Natural-unit mapping between dimensionless BHSM tension and mass."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Any

from .constants import EV_PER_GEV, GEV_PER_EV, JOULE_PER_GEV, KG_PER_GEV_C2


@dataclass(frozen=True)
class GeometricUnitMapper:
    """Map geometric tension to GeV using an explicit calibration record."""

    scale_gev_per_tension: float = 1.0
    anchor_particle: str | None = None
    anchor_mass_gev: float | None = None
    anchor_source: str | None = None
    calibration_mode: str = "NATURAL_UNIT_SCALE"

    def __post_init__(self) -> None:
        if not isfinite(self.scale_gev_per_tension) or self.scale_gev_per_tension <= 0.0:
            raise ValueError("scale_gev_per_tension must be finite and positive")

    @classmethod
    def from_anchor(
        cls,
        anchor_tension: float,
        anchor_mass_gev: float,
        anchor_particle: str,
        anchor_source: str,
    ) -> "GeometricUnitMapper":
        """Calibrate one unit scale while recording the non-independent anchor."""

        if not isfinite(anchor_tension) or anchor_tension == 0.0:
            raise ValueError("anchor_tension must be finite and nonzero")
        if not isfinite(anchor_mass_gev) or anchor_mass_gev <= 0.0:
            raise ValueError("anchor_mass_gev must be finite and positive")
        return cls(
            scale_gev_per_tension=anchor_mass_gev / anchor_tension,
            anchor_particle=anchor_particle,
            anchor_mass_gev=anchor_mass_gev,
            anchor_source=anchor_source,
            calibration_mode="EMPIRICAL_CALIBRATION_ANCHOR",
        )

    def tension_to_mass_gev(self, tension: float) -> float:
        return float(tension) * self.scale_gev_per_tension

    @staticmethod
    def mass_gev_to_ev(mass_gev: float) -> float:
        return float(mass_gev) * EV_PER_GEV

    @staticmethod
    def mass_ev_to_gev(mass_ev: float) -> float:
        return float(mass_ev) * GEV_PER_EV

    @staticmethod
    def mass_gev_to_kg(mass_gev: float) -> float:
        return float(mass_gev) * KG_PER_GEV_C2

    @staticmethod
    def mass_kg_to_gev(mass_kg: float) -> float:
        return float(mass_kg) / KG_PER_GEV_C2

    @staticmethod
    def energy_gev_to_joule(energy_gev: float) -> float:
        return float(energy_gev) * JOULE_PER_GEV

    @staticmethod
    def energy_joule_to_gev(energy_joule: float) -> float:
        return float(energy_joule) / JOULE_PER_GEV

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["natural_units"] = "c=1; masses reported in GeV/c^2 convention"
        payload["anchor_is_independent_prediction"] = False if self.anchor_particle else None
        return payload
