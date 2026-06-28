"""Dimensionally guarded historical neutral mass candidate.

The action-normalized spectral route in ``neutrino_spectral`` supersedes this
legacy path for particle-mass construction.
"""

from __future__ import annotations

from pathlib import Path

from .common import repository_path
from .radius_curvature_common import (
    DimensionfulNeutrinoMassCandidate,
    NeutralRadiusCurvatureClosureResult,
    clean_provenance,
    common_guard_fields,
)


LEGACY_FUNCTIONAL_SOURCE = "artifacts/BHSM_curvature_mass_functional_v1_1.json"


def legacy_mass_functional_output_dimension() -> str:
    """Return the SI dimension of (c^2/G) r^2 k for [k]=L^-2."""

    return "mass_per_length"


def compute_dimensionful_neutrino_mass_candidate(
    closure: NeutralRadiusCurvatureClosureResult,
    radius_m: float | None = None,
    curvature_per_m2: float | None = None,
    repository: str | Path | None = None,
) -> DimensionfulNeutrinoMassCandidate:
    """Refuse eV/GeV output until units and the mass functional are consistent.

    Numeric radius and curvature are necessary but not sufficient: with the
    legacy definition [k]=L^-2, the documented formula has dimension M/L.
    """

    root = repository_path(repository)
    sources = tuple(
        path
        for path in (
            LEGACY_FUNCTIONAL_SOURCE,
            *closure.source_artifacts,
        )
        if (root / path).is_file()
    )
    numeric_inputs = radius_m is not None and curvature_per_m2 is not None
    dimension_ok = closure.dimensional_consistency_passed
    available = bool(numeric_inputs and closure.numeric_bridge_available and dimension_ok)
    missing = closure.remaining_missing_object
    if numeric_inputs and not dimension_ok:
        missing = (
            "dimensionally consistent action-derived mass normalization: with [k]=m^-2, "
            "(c^2/G) r_prop^2 k_neutral,eff has units kg/m, not kg"
        )
    return DimensionfulNeutrinoMassCandidate(
        candidate_key="dimensionful_neutrino_mass_candidate",
        status="CONDITIONAL_DIMENSIONFUL_MASS_CANDIDATE" if available else "DIMENSIONFUL_MASS_NOT_AVAILABLE",
        value="m_nu = (c^2/(2G)) r_prop^2 k_neutral,eff",
        unit=None,
        dimension=legacy_mass_functional_output_dimension(),
        source_type="legacy functional plus neutral radius/curvature closure",
        source_artifacts=sources,
        provenance=clean_provenance(sources),
        author_ontology_dependency="propagation-locked neutral curvature response",
        claim_boundary=(
            "No eV/GeV output is produced. Numeric r_prop and k_neutral,eff remain absent, "
            "and the documented legacy functional also requires dimensional correction or an additional length normalization."
        ),
        remaining_missing_object=missing,
        radius_m=radius_m,
        curvature_per_m2=curvature_per_m2,
        dimensionful_mass_available=available,
        dimensionful_mass_kg=None,
        dimensionful_mass_eV=None,
        dimensionful_mass_GeV=None,
        dimensional_consistency_passed=dimension_ok,
        formula_output_dimension=legacy_mass_functional_output_dimension(),
        **common_guard_fields(),
    )
