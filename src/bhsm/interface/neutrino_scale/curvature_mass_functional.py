"""Adapter for the author-supplied legacy curvature mass functional."""

from __future__ import annotations

from pathlib import Path

from .legacy_artifact_parser import index_legacy_curvature_artifacts
from .legacy_curvature_threshold import CurvatureActivation, CurvatureMassFunctional


def load_curvature_mass_functional_from_legacy_artifacts(
    repository: str | Path | None = None,
) -> CurvatureMassFunctional:
    artifacts = {row.artifact_key: row for row in index_legacy_curvature_artifacts(repository)}
    source = artifacts["local_curvature_threshold_eft"]
    return CurvatureMassFunctional(
        artifact_key="legacy_curvature_mass_functional",
        source_file=source.source_file,
        source_document_title=source.source_document_title,
        source_equation="Eq. (2), repeated as Eq. (60); energy form recorded in the legacy EFT corpus",
        mass_formula="m = (c^2/(2G)) r_c^2 k_loc",
        energy_formula="E = (c^4/(2G)) r_c^2 k_loc",
        candidate_status="ARTIFACT_BACKED_CURVATURE_MASS_FUNCTIONAL",
        physical_dimensions=("[r_c] = length", "[k_loc] = length^-2", "[c^2/G] = mass/length"),
        action_derived=False,
        matching_ansatz_disclosed=True,
        claim_boundary=(
            "Artifact-backed as an author-supplied geometric matching functional. "
            "The source itself does not derive this formula from the scalar action. With K of dimension L^-2, "
            "the expression has dimension mass/length and is retained only as a dimensionally gated legacy stiffness ansatz."
        ),
    )


def load_curvature_activation_from_legacy_artifacts(
    repository: str | Path | None = None,
) -> CurvatureActivation:
    source = index_legacy_curvature_artifacts(repository)[0]
    return CurvatureActivation(
        curvature_operator="K[rho] = -nabla^2 ln rho",
        effective_local_curvature="k_loc = K[rho](r_c)",
        activation_number="N_K = integral sigma K[rho](r) dr",
        single_activation_normalization="N_K = 1",
        stability_conditions=(
            "k_loc > 0: stable localized mode",
            "k_loc = 0: delocalized, massless, or marginal mode",
            "k_loc < 0: unstable mode",
        ),
        source_file=source.source_file,
        candidate_status="ARTIFACT_BACKED_LEGACY_CURVATURE_STRUCTURE",
    )
