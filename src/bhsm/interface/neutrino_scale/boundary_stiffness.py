"""Search for the physical neutral background stiffness required by curvature units."""

from __future__ import annotations

from pathlib import Path

from .common import repository_path
from .radius_curvature_common import BoundaryStiffnessCandidate, clean_provenance, common_guard_fields


SOURCES = (
    "artifacts/BHSM_author_ontology_v0_8.json",
    "artifacts/BHSM_neutrino_basis_scale_minimal_action_closure_v0_8.json",
    "theory/collective_curvature_threshold_layer.md",
)


def search_boundary_stiffness(
    repository: str | Path | None = None,
) -> BoundaryStiffnessCandidate:
    root = repository_path(repository)
    found = tuple(path for path in SOURCES if (root / path).is_file())
    return BoundaryStiffnessCandidate(
        candidate_key="neutral_boundary_stiffness",
        status="OPEN_MISSING_PHYSICAL_NEUTRAL_CURVATURE_MAP",
        value=None,
        unit=None,
        dimension="energy density or curvature normalization",
        source_type="local symbolic action search",
        source_artifacts=found,
        provenance=clean_provenance(found),
        author_ontology_dependency="symbolic dmu_boundary dt and curvature-response action",
        claim_boundary="The local action names a response measure but supplies no physical neutral background stiffness.",
        remaining_missing_object="neutral background stiffness or energy-density coefficient with physical units and kernel coupling",
        numeric_energy_density_available=False,
        neutral_kernel_coupling_available=False,
        **common_guard_fields(),
    )

