"""Fifth-force range and coupling bounds for BHSM scalar scaffolds."""

from __future__ import annotations

from dataclasses import dataclass

from scalar_decoupling import HBAR_C_GEV_M, ScalarMode


@dataclass(frozen=True)
class FifthForceRangeBound:
    """Fifth-force range/coupling audit row for one scalar mode."""

    mode_id: str
    effective_mass_gev: float | None
    compton_range_m: float | None
    derivative_screened: bool
    curvature_screened: bool
    screened: bool
    couples_to_ordinary_matter: bool
    violates_low_energy_ontology: bool
    status: str
    limitations: tuple[str, ...]


def compton_range_m(mass_gev: float | None) -> float | None:
    """Return Compton range in meters, or ``None`` if mass is unavailable."""

    if mass_gev is None:
        return None
    if mass_gev <= 0:
        raise ValueError("mass_gev must be positive")
    return HBAR_C_GEV_M / float(mass_gev)


def fifth_force_bound_for_mode(mode: ScalarMode, gap: float) -> FifthForceRangeBound:
    """Classify fifth-force risk for one scalar mode."""

    derivative = mode.coupling_type == "derivative_filtered"
    curvature = mode.coupling_type == "curvature_filtered"
    screened = mode.coupling_type == "screened"
    direct = mode.coupling_type == "dangerous_light"
    light = mode.eigenvalue < gap
    violates = bool(light and direct and not mode.is_higgs_projection)
    if mode.is_higgs_projection:
        status = "SM_HIGGS_ALLOWED"
        couples = True
    elif mode.eigenvalue >= gap:
        status = "HEAVY_RANGE_SUPPRESSED"
        couples = False
    elif derivative:
        status = "DERIVATIVE_SCREENED_CONDITIONAL"
        couples = False
    elif curvature:
        status = "CURVATURE_SCREENED_CONDITIONAL"
        couples = False
    elif screened:
        status = "SCREENED_TOPOGRAPHIC_CONDITIONAL"
        couples = False
    elif violates:
        status = "FORBIDDEN_UNSCREENED_LIGHT_SCALAR"
        couples = True
    else:
        status = "OPEN_SCALAR_RISK"
        couples = True
        violates = True
    return FifthForceRangeBound(
        mode_id=mode.mode_id,
        effective_mass_gev=float(mode.eigenvalue),
        compton_range_m=compton_range_m(mode.eigenvalue),
        derivative_screened=derivative,
        curvature_screened=curvature,
        screened=screened,
        couples_to_ordinary_matter=couples,
        violates_low_energy_ontology=violates,
        status=status,
        limitations=(
            "Mass/range row is a scaffold estimate.",
            "Screening proof requires the full scalar/topographic action.",
        ),
    )


def fifth_force_bounds_for_modes(modes: tuple[ScalarMode, ...], gap: float) -> tuple[FifthForceRangeBound, ...]:
    """Return fifth-force bounds for a scalar inventory."""

    return tuple(fifth_force_bound_for_mode(mode, gap) for mode in modes)
