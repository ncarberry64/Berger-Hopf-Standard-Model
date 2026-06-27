"""Structured search for a physical BHSM neutral-curvature map."""

from __future__ import annotations

from pathlib import Path

from .boundary_stiffness import search_boundary_stiffness
from .common import repository_path
from .radius_curvature_common import (
    NeutralPhysicalCurvatureCandidate,
    NeutralPhysicalCurvatureMap,
    clean_provenance,
    common_guard_fields,
)
from .transport_normalization import search_transport_normalization


SOURCES = (
    "artifacts/neutral_operator_no_fit_output_v1.json",
    "artifacts/BHSM_neutrino_curvature_threshold_v0_9.json",
    "artifacts/BHSM_author_ontology_v0_8.json",
    "theory/legacy_sources/v1_1/mass_from_local_curvature_thresholds_scalar_topographic_eft.pdf",
)


def _candidate(
    key: str,
    status: str,
    value: str | None,
    unit: str | None,
    dimension: str,
    source: str,
    boundary: str,
    missing: str,
    numeric: bool = False,
    symbolic: bool = False,
    neutral_specific: bool = False,
) -> NeutralPhysicalCurvatureCandidate:
    return NeutralPhysicalCurvatureCandidate(
        candidate_key=key,
        status=status,
        value=value,
        unit=unit,
        dimension=dimension,
        source_type="local BHSM artifact or legacy theory source",
        source_artifacts=(source,),
        provenance=clean_provenance((source,)),
        author_ontology_dependency="NEUTRINO_MASS_IS_PROPAGATION_LOCKED_CURVATURE_RESPONSE",
        claim_boundary=boundary,
        remaining_missing_object=missing,
        numeric_per_m2_available=numeric,
        symbolic_curvature_available=symbolic,
        neutral_specific=neutral_specific,
        **common_guard_fields(),
    )


def search_neutral_physical_curvature_map(
    repository: str | Path | None = None,
) -> NeutralPhysicalCurvatureMap:
    root = repository_path(repository)
    stiffness = search_boundary_stiffness(root)
    transport = search_transport_normalization(root)
    candidates = (
        _candidate(
            "neutral_dimensionless_threshold_response",
            "DIMENSIONLESS_CURVATURE_RESPONSE",
            "R_nu = max(0, p*g_nu*||K_nu psi||/||psi|| - kappa_nu)",
            None,
            "dimensionless response",
            SOURCES[0],
            "The neutral kernel response is executable but is not curvature in m^-2.",
            "physical curvature normalization",
            neutral_specific=True,
        ),
        _candidate(
            "legacy_general_curvature_operator",
            "REFERENCE_ONLY",
            "K[rho] = -nabla^2 ln rho",
            "m^-2 when rho is defined on a physical spatial metric",
            "inverse length squared",
            SOURCES[3],
            "The legacy operator has the right physical dimension but no explicit map from the BHSM neutral kernel.",
            "neutral profile rho_nu and projection from K_nu response to K[rho_nu]",
            symbolic=True,
        ),
        _candidate(
            "conditional_neutral_curvature_map",
            "CONDITIONAL_PHYSICAL_CURVATURE_MAP_CANDIDATE",
            "k_neutral,eff = kappa_curv * R_nu_dimless",
            "m^-2 (symbolic)",
            "inverse length squared",
            SOURCES[2],
            "The form is explicit and neutral-specific, but kappa_curv is an unresolved physical normalization, not a fitted constant.",
            "action-derived kappa_curv in m^-2 from boundary stiffness and transport normalization",
            symbolic=True,
            neutral_specific=True,
        ),
        _candidate(
            "empirical_curvature_scale",
            "FORBIDDEN_EMPIRICAL_CURVATURE_SCALE",
            None,
            "m^-2",
            "inverse length squared",
            "comparison layer only",
            "Neutrino limits, W calibration, and legacy particle tables cannot set kappa_curv.",
            "none; this route is rejected",
        ),
    )
    numeric = any(row.numeric_per_m2_available for row in candidates)
    symbolic = any(row.status == "CONDITIONAL_PHYSICAL_CURVATURE_MAP_CANDIDATE" for row in candidates)
    status = "ARTIFACT_BACKED_PHYSICAL_CURVATURE_MAP" if numeric else (
        "CONDITIONAL_PHYSICAL_CURVATURE_MAP_CANDIDATE" if symbolic else "OPEN_MISSING_PHYSICAL_NEUTRAL_CURVATURE_MAP"
    )
    found = tuple(path for path in SOURCES if (root / path).is_file())
    missing = "; ".join((stiffness.remaining_missing_object, transport.remaining_missing_object))
    return NeutralPhysicalCurvatureMap(
        candidate_key="neutral_physical_curvature_map",
        status=status,
        value="k_neutral,eff = kappa_curv * R_nu_dimless" if symbolic else None,
        unit="m^-2 (symbolic only)" if symbolic else None,
        dimension="inverse length squared",
        source_type="author-ontology conditional map plus local artifact search",
        source_artifacts=found,
        provenance=clean_provenance(found),
        author_ontology_dependency="propagation-conditioned neutral curvature response",
        claim_boundary="A symbolic physical-curvature map is defined, but its m^-2 normalization is not derived.",
        remaining_missing_object=missing,
        candidates=candidates,
        dimensionless_response_available=True,
        numeric_per_m2_found=numeric,
        symbolic_candidate_found=symbolic,
        physical_unit_normalization_available=False,
        **common_guard_fields(),
    )

