"""Offline neutral kinetic/curvature stiffness search."""

from __future__ import annotations

from pathlib import Path

from ..neutrino_scale.common import repository_path
from .common import (
    NeutralCurvaturePenalty,
    NeutralKineticStiffness,
    NeutralStiffnessRatio,
    clean_provenance,
    guard_fields,
)


SOURCES = (
    "theory/legacy_sources/v1_1/mass_gap.pdf",
    "docs/bhsm_numerical_input_closure_map.md",
    "artifacts/BHSM_author_ontology_v0_8.json",
)


def search_neutral_stiffness_ratio(
    repository: str | Path | None = None,
) -> NeutralStiffnessRatio:
    """Return a symbolic ratio while refusing scalar lambda as neutral closure."""

    root = repository_path(repository)
    found = tuple(path for path in SOURCES if (root / path).is_file())
    provenance = clean_provenance(found)
    common = {
        "source_type": "local artifact and symbolic neutral-action inventory",
        "source_artifacts": found,
        "provenance": provenance,
        "author_ontology_dependency": "propagation-locked neutral curvature response",
        **guard_fields(),
    }
    kinetic = NeutralKineticStiffness(
        candidate_key="neutral_kinetic_stiffness_Z_nu",
        status="OPEN_MISSING_NEUTRAL_KINETIC_STIFFNESS",
        value="Z_nu",
        unit="symbolic",
        dimension="neutral wave normalization",
        source_equations=("1/2 Z_nu (partial phi_nu)^2",),
        claim_boundary="Z_nu is named by the conditional neutral action but no numeric neutral coefficient is derived.",
        remaining_missing_object="action-derived numeric neutral kinetic stiffness Z_nu",
        symbolic_available=True,
        numeric_available=False,
        **common,
    )
    penalty = NeutralCurvaturePenalty(
        candidate_key="neutral_curvature_penalty_A_nu",
        status="OPEN_MISSING_NEUTRAL_CURVATURE_PENALTY",
        value="A_nu",
        unit="symbolic",
        dimension="neutral curvature-penalty coefficient",
        source_equations=("1/2 A_nu(-nabla^2 phi_nu-K_neutral,eff)^2",),
        claim_boundary=(
            "Scalar lambda supports the action shape but is not identified with the BHSM neutral coefficient. "
            "Existing Robin A_nu notation is also not silently reused as this curvature penalty."
        ),
        remaining_missing_object="action-derived numeric neutral curvature penalty A_nu",
        symbolic_available=True,
        numeric_available=False,
        **common,
    )
    return NeutralStiffnessRatio(
        candidate_key="neutral_stiffness_ratio",
        status="CONDITIONAL_NEUTRAL_STIFFNESS_RATIO_CANDIDATE",
        value="sqrt(A_nu/Z_nu)",
        unit="m (required; symbolic only)",
        dimension="length",
        source_type=common["source_type"],
        source_artifacts=found,
        source_equations=("ell_nu = sqrt(A_nu/Z_nu)",),
        provenance=provenance,
        author_ontology_dependency=common["author_ontology_dependency"],
        claim_boundary="The neutral stiffness length is symbolically defined but has no artifact-backed numeric metre value.",
        remaining_missing_object="numeric action-derived sqrt(A_nu/Z_nu) in metres",
        kinetic_stiffness=kinetic,
        curvature_penalty=penalty,
        symbolic_ratio_available=True,
        numeric_length_available=False,
        stiffness_length_m=None,
        **guard_fields(),
    )
