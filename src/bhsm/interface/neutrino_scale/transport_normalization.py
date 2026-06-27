"""Audit the neutral transport normalization from boundary response to curvature."""

from __future__ import annotations

from pathlib import Path

from .common import repository_path
from .radius_curvature_common import TransportNormalizationCandidate, clean_provenance, common_guard_fields


SOURCES = (
    "artifacts/BHSM_boundary_no_fit_prediction_package_v1.json",
    "artifacts/BHSM_neutrino_numerical_closure_report_v0_9.json",
    "artifacts/BHSM_author_ontology_v0_8.json",
)


def search_transport_normalization(
    repository: str | Path | None = None,
) -> TransportNormalizationCandidate:
    root = repository_path(repository)
    found = tuple(path for path in SOURCES if (root / path).is_file())
    return TransportNormalizationCandidate(
        candidate_key="neutral_transport_normalization",
        status="OPEN_MISSING_PHYSICAL_NEUTRAL_CURVATURE_MAP",
        value="T(mu_BH_boundary -> mu_BH_boundary) = 1",
        unit=None,
        dimension="dimensionless transport identity",
        source_type="local boundary transport artifact",
        source_artifacts=found,
        provenance=clean_provenance(found),
        author_ontology_dependency="neutral propagation map U_nu(t)",
        claim_boundary="The boundary identity transport is dimensionless and does not normalize curvature in m^-2.",
        remaining_missing_object="physical neutral transport normalization connecting one kernel-response unit to curvature",
        dimensionless_transport_available=True,
        physical_transport_normalization_available=False,
        **common_guard_fields(),
    )

