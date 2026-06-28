"""Adapter for the bundled scalar topographic mass-gap action analogue."""

from __future__ import annotations

from pathlib import Path

from ..neutrino_scale.common import repository_path
from ..neutrino_scale.legacy_artifact_parser import index_legacy_curvature_artifacts
from .common import MassGapActionCandidate, clean_provenance, guard_fields


SCALAR_ACTION = "L = 1/2(dt phi)^2 - 1/2(grad phi)^2 - lambda/2(-nabla^2 phi - k_loc)^2"
SCALAR_GAP = "m_gap = sqrt(lambda) k_loc"
NEUTRAL_ACTION = "L_nu = 1/2 Z_nu(dt phi_nu)^2 - 1/2 Z_nu(grad phi_nu)^2 - 1/2 A_nu(-nabla^2 phi_nu - K_neutral,eff)^2"
NEUTRAL_GAP = "mu_nu = sqrt(A_nu/Z_nu) K_neutral,eff"


def load_neutral_mass_gap_action(
    repository: str | Path | None = None,
) -> MassGapActionCandidate:
    root = repository_path(repository)
    artifacts = {row.artifact_key: row for row in index_legacy_curvature_artifacts(root)}
    source = artifacts["curvature_mass_gap_eft"]
    recognized = SCALAR_ACTION in source.recognized_formulas and SCALAR_GAP in source.recognized_formulas
    if not recognized:
        raise ValueError("bundled mass-gap artifact does not expose the registered action and gap equations")
    sources = (source.source_file,)
    return MassGapActionCandidate(
        candidate_key="neutral_mass_gap_action",
        status="ARTIFACT_BACKED_MASS_GAP_ACTION",
        value=NEUTRAL_GAP,
        unit="symbolic",
        dimension="inverse_length",
        source_type="bundled scalar topographic EFT analogue",
        source_artifacts=sources,
        source_equations=(SCALAR_ACTION, SCALAR_GAP, NEUTRAL_ACTION, NEUTRAL_GAP),
        provenance=clean_provenance(sources),
        author_ontology_dependency="neutrino mass is propagation-locked curvature response",
        claim_boundary=(
            "The scalar action and its gap structure are artifact-backed. The neutral-sector "
            "normalization is a conditional generalization until A_nu, Z_nu, and K_neutral,eff are derived."
        ),
        remaining_missing_object="neutral A_nu, Z_nu, and physical K_neutral,eff",
        scalar_action_artifact_backed=True,
        neutral_action_generalization_conditional=True,
        action_density=NEUTRAL_ACTION,
        spectral_gap_formula=NEUTRAL_GAP,
        **guard_fields(),
    )
