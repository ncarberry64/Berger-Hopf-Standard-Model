"""Gate 30B scalar/topographic decoupling scaffold.

This module audits a finite scalar inventory. It does not prove scalar
decoupling in the full action.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi
from typing import Iterable

from constants import V_HIGGS_EMPIRICAL_GEV

ALLOWED_COUPLING_TYPES = {
    "higgs_projection",
    "heavy_orthogonal",
    "derivative_filtered",
    "curvature_filtered",
    "screened",
    "dangerous_light",
}
CONDITIONAL_TYPES = {"derivative_filtered", "curvature_filtered", "screened"}
HBAR_C_GEV_M = 1.973269804e-16


@dataclass(frozen=True)
class ScalarMode:
    """Finite-basis scalar/topographic mode record."""

    mode_id: str
    sector: str
    eigenvalue: float
    coupling_type: str
    coupling_strength: float
    is_higgs_projection: bool

    def __post_init__(self) -> None:
        if self.eigenvalue < 0:
            raise ValueError("eigenvalue must be nonnegative")
        if self.coupling_strength < 0:
            raise ValueError("coupling_strength must be nonnegative")
        if self.coupling_type not in ALLOWED_COUPLING_TYPES:
            raise ValueError(f"unknown coupling_type: {self.coupling_type}")


def hopf_gap_mass(v: float) -> float:
    """Return M_lift = 4 pi^2 v."""

    if v <= 0:
        raise ValueError("v must be positive")
    return 4.0 * pi**2 * v


def classify_scalar_mode(mode: ScalarMode, gap: float) -> dict[str, object]:
    """Classify one scalar mode against the Gate 30B pass conditions."""

    if gap <= 0:
        raise ValueError("gap must be positive")
    is_light = mode.eigenvalue < gap
    if mode.is_higgs_projection:
        passes = mode.coupling_type == "higgs_projection"
        status = "light_higgs_projection" if passes else "invalid_higgs_projection"
        conditional = False
    elif mode.eigenvalue >= gap:
        passes = True
        status = "heavy_orthogonal"
        conditional = False
    elif mode.coupling_type in CONDITIONAL_TYPES:
        passes = True
        status = f"conditional_{mode.coupling_type}"
        conditional = True
    else:
        passes = False
        status = "dangerous_light"
        conditional = False
    return {
        "mode_id": mode.mode_id,
        "sector": mode.sector,
        "eigenvalue": mode.eigenvalue,
        "gap": gap,
        "is_light": is_light,
        "coupling_type": mode.coupling_type,
        "coupling_strength": mode.coupling_strength,
        "is_higgs_projection": mode.is_higgs_projection,
        "status": status,
        "conditional": conditional,
        "passes": passes,
    }


def build_scalar_proxy_spectrum(
    n_modes: int,
    higgs_light: bool = True,
    gap_scale: float | None = None,
) -> list[ScalarMode]:
    """Build a transparent finite scalar proxy spectrum."""

    if n_modes < 1:
        raise ValueError("n_modes must be at least 1")
    gap = hopf_gap_mass(V_HIGGS_EMPIRICAL_GEV) if gap_scale is None else gap_scale
    if gap <= 0:
        raise ValueError("gap_scale must be positive")
    modes: list[ScalarMode] = []
    if higgs_light:
        modes.append(
            ScalarMode("phi_0", "higgs", 125.10, "higgs_projection", 1.0, True)
        )
    else:
        modes.append(
            ScalarMode("phi_0", "higgs", gap, "heavy_orthogonal", 0.0, False)
        )
    coupling_cycle = ["heavy_orthogonal", "derivative_filtered", "curvature_filtered", "screened"]
    for idx in range(1, n_modes):
        ctype = coupling_cycle[(idx - 1) % len(coupling_cycle)]
        if ctype == "heavy_orthogonal":
            eigenvalue = gap * (1.0 + 0.1 * idx)
        else:
            eigenvalue = gap / (idx + 2.0)
        modes.append(
            ScalarMode(
                mode_id=f"phi_{idx}",
                sector="orthogonal",
                eigenvalue=eigenvalue,
                coupling_type=ctype,
                coupling_strength=1.0 / (idx + 1.0),
                is_higgs_projection=False,
            )
        )
    return modes


def orthogonal_scalar_modes(modes: Iterable[ScalarMode]) -> list[ScalarMode]:
    """Return modes orthogonal to the Higgs projection."""

    return [mode for mode in modes if not mode.is_higgs_projection]


def check_scalar_gap(modes: Iterable[ScalarMode], gap: float) -> dict[str, object]:
    """Check scalar gap and coupling-screen conditions."""

    mode_list = list(modes)
    classifications = [classify_scalar_mode(mode, gap) for mode in mode_list]
    higgs_count = sum(1 for mode in mode_list if mode.is_higgs_projection and mode.eigenvalue < gap)
    dangerous = [row for row in classifications if not row["passes"]]
    conditional = [row for row in classifications if row["conditional"]]
    return {
        "mode_count": len(mode_list),
        "light_higgs_projection_count": higgs_count,
        "exactly_one_light_higgs_projection": higgs_count == 1,
        "dangerous_light_modes": dangerous,
        "conditional_modes": conditional,
        "passes": bool(higgs_count == 1 and not dangerous),
        "classifications": classifications,
    }


def fifth_force_range(mass_gev: float) -> float:
    """Return Compton range in meters for a scalar mass in GeV."""

    if mass_gev <= 0:
        raise ValueError("mass_gev must be positive")
    return HBAR_C_GEV_M / mass_gev


def coupling_suppression_factor(mode: ScalarMode, suppression_scale: float) -> float:
    """Return a simple screened coupling factor for audit purposes."""

    if suppression_scale <= 0:
        raise ValueError("suppression_scale must be positive")
    return mode.coupling_strength / (1.0 + mode.eigenvalue / suppression_scale)


def scalar_decoupling_report(modes: Iterable[ScalarMode], gap: float) -> dict[str, object]:
    """Return an auditable scalar/topographic decoupling report."""

    check = check_scalar_gap(modes, gap)
    return {
        **check,
        "gap": gap,
        "status": "SCAFFOLD_AUDIT",
        "theorem_complete": False,
        "limitations": (
            "Full action-level scalar/topographic decoupling remains OPEN; "
            "filtered and screened modes are conditional."
        ),
    }
