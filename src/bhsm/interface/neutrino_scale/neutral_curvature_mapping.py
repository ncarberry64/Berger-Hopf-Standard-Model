"""Map the BHSM neutral kernel response to curvature without inventing units."""

from __future__ import annotations

from pathlib import Path

from .common import repository_path
from .legacy_curvature_threshold import NeutralCurvatureMapping


CURVATURE_SOURCES = (
    "artifacts/neutral_operator_no_fit_output_v1.json",
    "artifacts/BHSM_neutrino_curvature_threshold_v0_9.json",
    "artifacts/BHSM_neutrino_numerical_closure_report_v0_9.json",
    "artifacts/BHSM_author_ontology_v0_8.json",
)


def derive_or_locate_neutral_curvature_mapping(
    repository: str | Path | None = None,
) -> NeutralCurvatureMapping:
    root = repository_path(repository)
    sources = tuple(path for path in CURVATURE_SOURCES if (root / path).is_file())
    return NeutralCurvatureMapping(
        mapping_formula="R_nu_dimless(psi,p) = max(0, p*g_nu*||K_nu psi||/||psi|| - kappa_nu)",
        status="OPEN_MISSING_NEUTRAL_CURVATURE_MAPPING",
        dimensionless_curvature_response_available=True,
        physical_curvature_units_available=False,
        curvature_value_per_m2=None,
        source_artifacts=sources,
        claim_boundary=(
            "The neutral kernel supplies a dimensionless positive-threshold response. "
            "No artifact maps one response unit to k_neutral,eff in m^-2."
        ),
        remaining_missing_object="artifact-backed conversion from the dimensionless neutral threshold response to physical curvature in m^-2",
    )

