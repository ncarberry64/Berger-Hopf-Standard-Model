"""Deterministic offline BHSM prediction report builder."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence

from .geometry import HypersphericalGeometry
from .pdg_interface import load_reference_with_fallback
from .predictions import PredictionRegistry, PredictionStatus, default_prediction_registry
from .solver import ParticleMassSolver
from .units import GeometricUnitMapper
from .validation import ExperimentalValue, ValidationComparison

CALIBRATION_WARNING = "If a particle mass is used to calibrate the geometric-to-physical unit scale, that same particle cannot be counted as an independent prediction in that run."
NEUTRINO_WARNING = "The electron-neutrino comparison is treated as an upper-limit comparison unless a vetted central experimental mass reference is explicitly supplied."
OPEN_THEOREM_WARNING = "Open-theorem entries are registry blockers, not production-ready predictions."
RUNTIME_WARNING = "Runtime-disabled software entries require live external validation before readiness can be claimed."


@dataclass
class PredictionReport:
    report_name: str
    release_basis: str
    anchor_particle: str | None
    calibration_metadata: dict[str, Any]
    predictions: list[dict[str, Any]]
    comparisons: list[dict[str, Any]]
    registry_statuses: list[dict[str, Any]]
    warnings: list[str]
    claim_boundaries: list[str]
    empirical_derivation_inputs_used: bool = False
    boundary_predictions_modified_by_runtime_inputs: bool = False
    internet_required: bool = False
    pdg_dependency_required: bool = False
    claims_of_empirical_validation: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def demo_geometry(particle_key: str) -> HypersphericalGeometry:
    """Return deterministic placeholder geometry for CLI demonstrations."""

    if particle_key == "W_boson":
        return HypersphericalGeometry((1.0,), (0.0,), sector="electroweak_vector", mode_label="interface_demo_w_anchor")
    if particle_key == "electron_neutrino":
        return HypersphericalGeometry((1.0e-12,), (0.0,), sector="effective_neutrino_extension", mode_label="interface_demo_electron_neutrino")
    raise KeyError(f"no deterministic demo geometry for {particle_key!r}")


def _default_mapper(anchor_particle: str | None, geometry_by_particle: Mapping[str, HypersphericalGeometry], references: Mapping[str, ExperimentalValue]) -> GeometricUnitMapper:
    if anchor_particle is None:
        return GeometricUnitMapper()
    geometry = geometry_by_particle[anchor_particle]
    reference = references[anchor_particle]
    if reference.value_gev is None:
        raise ValueError("calibration anchor requires a central value")
    return GeometricUnitMapper.from_anchor(geometry.geometric_tension(), reference.value_gev, anchor_particle, reference.source_label)


def build_prediction_report(
    anchor_particle: str | None = "W_boson",
    particles: Sequence[str] = ("W_boson", "electron_neutrino"),
    geometry_by_particle: Mapping[str, HypersphericalGeometry] | None = None,
    sector_factors: Mapping[str, float] | None = None,
    mapper: GeometricUnitMapper | None = None,
    references: Mapping[str, ExperimentalValue] | None = None,
    include_open_theorem_entries: bool = False,
    format: str = "json",
    registry: PredictionRegistry | None = None,
) -> PredictionReport:
    """Build a report while preserving calibration/prediction/comparison boundaries."""

    del format  # serialization is handled by CLI or caller
    registry = registry or default_prediction_registry()
    requested = list(dict.fromkeys(particles))
    geometries = dict(geometry_by_particle or {})
    refs = dict(references or {})
    for key in requested + ([anchor_particle] if anchor_particle else []):
        if key in ("W_boson", "electron_neutrino"):
            geometries.setdefault(key, demo_geometry(key))
            refs.setdefault(key, load_reference_with_fallback(key))
    mapper = mapper or _default_mapper(anchor_particle, geometries, refs)
    factors = dict(sector_factors or {})
    solver = ParticleMassSolver()
    predictions: list[dict[str, Any]] = []
    comparisons: list[dict[str, Any]] = []
    statuses: list[dict[str, Any]] = []
    warnings: list[str] = []

    if anchor_particle and anchor_particle in requested:
        warnings.append(CALIBRATION_WARNING)
    if "electron_neutrino" in requested:
        warnings.append(NEUTRINO_WARNING)
    requested_entries = [registry.get(key) for key in requested]
    if any(entry and entry.default_status is PredictionStatus.OPEN_THEOREM_REQUIRED for entry in requested_entries):
        warnings.append(OPEN_THEOREM_WARNING)
    if any(entry and entry.default_status is PredictionStatus.DISABLED_UNTIL_RUNTIME_VALIDATED for entry in requested_entries):
        warnings.append(RUNTIME_WARNING)

    for key in requested:
        entry = registry.get(key)
        if entry is None:
            statuses.append({"particle_key": key, "status": PredictionStatus.UNKNOWN_OR_UNREGISTERED.value})
            continue
        status = entry.default_status
        if key in geometries:
            result = solver.solve_mass(geometries[key], key, mapper.anchor_mass_gev or 1.0, mapper, sector_factor=factors.get(key, 1.0))
            status = PredictionStatus(result.prediction_status)
            prediction = result.to_dict()
            prediction["registry_default_status"] = entry.default_status.value
            prediction["formula_status"] = geometries[key].to_dict()["formula_status"]
            predictions.append(prediction)
            if result.success and result.mass_gev is not None and key in refs:
                comparison = ValidationComparison.compare(result.mass_gev, refs[key]).to_dict()
                comparisons.append(comparison)
        statuses.append({"particle_key": key, "status": status.value, "claim_boundary": entry.claim_boundary})

    if include_open_theorem_entries:
        blocker_statuses = (PredictionStatus.OPEN_THEOREM_REQUIRED, PredictionStatus.DISABLED_UNTIL_RUNTIME_VALIDATED)
        for entry in registry.select_by_status(blocker_statuses):
            if entry.particle_key not in requested:
                statuses.append({"particle_key": entry.particle_key, "status": entry.default_status.value, "claim_boundary": entry.claim_boundary, "theorem_status": entry.theorem_status})
        for warning in (OPEN_THEOREM_WARNING, RUNTIME_WARNING):
            if warning not in warnings:
                warnings.append(warning)

    return PredictionReport(
        report_name="BHSM Prediction Report",
        release_basis=registry.release_basis,
        anchor_particle=anchor_particle,
        calibration_metadata=mapper.to_dict(),
        predictions=predictions,
        comparisons=comparisons,
        registry_statuses=statuses,
        warnings=warnings,
        claim_boundaries=[entry.claim_boundary for entry in registry.list_entries()],
    )
