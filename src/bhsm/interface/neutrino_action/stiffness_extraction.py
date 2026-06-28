"""Fail-closed extraction of neutral kinetic and curvature stiffness."""

from __future__ import annotations

from pathlib import Path

from ..neutrino_scale.common import repository_path
from .action_source_search import search_neutral_action_sources
from .common import (
    NeutralCurvaturePenaltyResult,
    NeutralKineticStiffnessResult,
    NeutralStiffnessLengthResult,
    guard_fields,
    provenance,
)


def derive_or_locate_neutral_kinetic_stiffness(
    repository: str | Path | None = None,
) -> NeutralKineticStiffnessResult:
    search = search_neutral_action_sources(repository)
    sources = tuple(
        path
        for term in search.terms
        if term.term_key in {"neutral_propagation_source", "neutral_boundary_tangential_kinetic"}
        for path in term.source_artifacts
    )
    return NeutralKineticStiffnessResult(
        candidate_key="neutral_kinetic_stiffness",
        status="OPEN_MISSING_NEUTRAL_KINETIC_STIFFNESS",
        value="Z_nu",
        unit=None,
        dimension="coefficient required to normalize neutral kinetic terms",
        numeric_value=None,
        symbolic_value="Z_nu",
        source_type="partial neutral boundary-action source chain",
        source_artifacts=tuple(dict.fromkeys(sources)),
        source_equations=("1/2 Z_nu (partial_tau phi_nu)^2", "1/2 chi_nu^{AB}D_A Phi D_B Phi"),
        provenance=provenance(tuple(dict.fromkeys(sources))),
        author_ontology_dependency="neutral propagation field on the physical boundary support",
        claim_boundary="The action requires a kinetic normalization, but no theorem identifies a numeric Z_nu from chi_nu, the metric, and the support measure.",
        remaining_missing_object="normalized support metric/measure and operator-to-Z_nu identification",
        coefficient_symbol="Z_nu",
        symbolic_available=True,
        numeric_available=False,
        **guard_fields(),
    )


def derive_or_locate_neutral_curvature_penalty(
    repository: str | Path | None = None,
) -> NeutralCurvaturePenaltyResult:
    search = search_neutral_action_sources(repository)
    sources = tuple(
        path
        for term in search.terms
        if term.term_key in {"scalar_mass_gap_analogue", "neutral_boundary_normal_coupling"}
        for path in term.source_artifacts
    )
    return NeutralCurvaturePenaltyResult(
        candidate_key="neutral_curvature_penalty",
        status="OPEN_MISSING_NEUTRAL_CURVATURE_PENALTY",
        value="A_nu_gap",
        unit=None,
        dimension="coefficient required to turn curvature mismatch squared into action density",
        numeric_value=None,
        symbolic_value="A_nu_gap",
        source_type="scalar mass-gap analogue plus partial neutral boundary action",
        source_artifacts=tuple(dict.fromkeys(sources)),
        source_equations=("1/2 A_nu_gap(-Delta_support phi_nu-K_neutral,eff)^2",),
        provenance=provenance(tuple(dict.fromkeys(sources))),
        author_ontology_dependency="propagation-conditioned neutral curvature response",
        claim_boundary=(
            "Scalar lambda supports the penalty shape but is not a neutral coefficient. A_nu_gap is explicitly "
            "distinct from the open Robin coefficient also named A_nu in earlier collar documents."
        ),
        remaining_missing_object="neutral operator-to-penalty theorem and normalized A_nu_gap coefficient",
        coefficient_symbol="A_nu_gap",
        symbolic_available=True,
        numeric_available=False,
        distinct_from_robin_coefficient=True,
        **guard_fields(),
    )


def derive_neutral_stiffness_length(
    repository: str | Path | None = None,
) -> NeutralStiffnessLengthResult:
    root = repository_path(repository)
    kinetic = derive_or_locate_neutral_kinetic_stiffness(root)
    penalty = derive_or_locate_neutral_curvature_penalty(root)
    sources = tuple(dict.fromkeys((*kinetic.source_artifacts, *penalty.source_artifacts)))
    return NeutralStiffnessLengthResult(
        candidate_key="neutral_stiffness_length",
        status="OPEN_MISSING_NUMERIC_STIFFNESS_LENGTH",
        value="sqrt(A_nu_gap/Z_nu)",
        unit="m required; unavailable",
        dimension="length required by spectral-gap dimensional closure",
        numeric_value=None,
        symbolic_value="ell_nu=sqrt(A_nu_gap/Z_nu)",
        source_type="conditional normalized neutral action",
        source_artifacts=sources,
        source_equations=("ell_nu=sqrt(A_nu_gap/Z_nu)", "[ell_nu]=L"),
        provenance=provenance(sources),
        author_ontology_dependency="propagation-locked curvature response",
        claim_boundary="The stiffness length is algebraically defined but neither coefficient nor their dimensionful ratio is numerically derived.",
        remaining_missing_object="numeric action-derived A_nu_gap/Z_nu with dimension length^2",
        kinetic=kinetic,
        curvature_penalty=penalty,
        ratio_symbolic="A_nu_gap/Z_nu",
        numeric_length_available=False,
        stiffness_length_m=None,
        **guard_fields(),
    )
