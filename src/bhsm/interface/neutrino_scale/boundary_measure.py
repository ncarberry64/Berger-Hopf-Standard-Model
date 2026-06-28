"""Boundary-measure dimensional analysis for the neutral action."""

from __future__ import annotations

from pathlib import Path

from .common import BoundaryMeasureCandidate, repository_path


AUTHOR_ONTOLOGY = "artifacts/BHSM_author_ontology_v0_8.json"


def analyze_neutral_boundary_measure(
    repository: str | Path | None = None,
) -> BoundaryMeasureCandidate:
    root = repository_path(repository)
    if not (root / AUTHOR_ONTOLOGY).is_file():
        raise FileNotFoundError(AUTHOR_ONTOLOGY)
    return BoundaryMeasureCandidate(
        measure_symbol="dmu_boundary dt",
        source=AUTHOR_ONTOLOGY,
        status="OPEN_MISSING_BOUNDARY_MEASURE",
        physical_dimension=None,
        unit=None,
        normalization_value=None,
        couples_to_neutral_kernel=True,
        physical_normalization_available=False,
        background_energy_density_available=False,
        missing_object="physical dimension and normalization of dmu_boundary dt, plus neutral background energy density",
        claim_boundary="The author ontology supplies a symbolic neutral-action measure, not its physical unit normalization.",
    )

