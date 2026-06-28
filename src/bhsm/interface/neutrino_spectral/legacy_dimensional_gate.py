"""Dimensional fail-closed gate for the legacy gravitational expression."""

from __future__ import annotations

from pathlib import Path

from ..neutrino_scale.common import repository_path
from .common import LegacyDimensionalGateResult, clean_provenance, guard_fields


SOURCE = "theory/legacy_sources/v1_1/mass_from_local_curvature_thresholds_scalar_topographic_eft.pdf"


def audit_legacy_gravitational_mass_formula_dimensions(
    repository: str | Path | None = None,
) -> LegacyDimensionalGateResult:
    root = repository_path(repository)
    sources = (SOURCE,) if (root / SOURCE).is_file() else ()
    return LegacyDimensionalGateResult(
        candidate_key="legacy_gravitational_dimensional_gate",
        status="DIMENSIONALLY_GATED_LEGACY_FUNCTIONAL",
        value="(c^2/(2G)) r^2 K",
        unit="kg/m",
        dimension="mass_per_length",
        source_type="legacy geometric matching ansatz with explicit SI dimension audit",
        source_artifacts=sources,
        source_equations=("K = -nabla^2 ln rho", "[K]=L^-2", "[c^2/G]=M/L"),
        provenance=clean_provenance(sources),
        author_ontology_dependency="none; dimensional identity",
        claim_boundary=(
            "The legacy curvature expression supplies a stiffness-like or mass-per-length bridge "
            "under its stated curvature definition, not a direct physical particle mass."
        ),
        remaining_missing_object="action-derived length or measure normalization",
        curvature_dimension="length^-2",
        radius_squared_curvature_dimension="dimensionless",
        prefactor_dimension="mass/length",
        formula_output_dimension="mass_per_length",
        physical_mass_dimension_passed=False,
        numeric_particle_mass_output_allowed=False,
        **guard_fields(),
    )
