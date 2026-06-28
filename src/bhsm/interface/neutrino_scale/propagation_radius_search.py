"""Structured search for a BHSM neutral propagation/localization radius."""

from __future__ import annotations

import json
from pathlib import Path

from .common import repository_path
from .radius_curvature_common import (
    PropagationRadiusCandidate,
    PropagationRadiusSearchResult,
    clean_provenance,
    common_guard_fields,
)


SOURCES = (
    "artifacts/BHSM_author_ontology_v0_8.json",
    "artifacts/BHSM_boundary_no_fit_prediction_package_v1.json",
    "artifacts/neutral_operator_no_fit_output_v1.json",
    "artifacts/internal_profile_radius_normalization_v1.json",
    "theory/theorem_discharge_neutral_effective_action.md",
    "theory/theorem_discharge_scalar_topographic_profile_input_classification.md",
    "theory/legacy_sources/v1_1/mass_from_local_curvature_thresholds_scalar_topographic_eft.pdf",
)


def _candidate(
    key: str,
    status: str,
    value: float | str | None,
    unit: str | None,
    dimension: str,
    source: str,
    boundary: str,
    missing: str,
    numeric: bool = False,
    symbolic: bool = False,
    neutrino_specific: bool = False,
    zero_consistent: bool = False,
) -> PropagationRadiusCandidate:
    return PropagationRadiusCandidate(
        candidate_key=key,
        status=status,
        value=value,
        unit=unit,
        dimension=dimension,
        source_type="local BHSM artifact or author ontology",
        source_artifacts=(source,),
        provenance=clean_provenance((source,)),
        author_ontology_dependency="NEUTRINO_MASS_IS_PROPAGATION_LOCKED_CURVATURE_RESPONSE",
        claim_boundary=boundary,
        remaining_missing_object=missing,
        numeric_metres_available=numeric,
        symbolic_length_available=symbolic,
        neutrino_specific=neutrino_specific,
        zero_propagation_consistent=zero_consistent,
        **common_guard_fields(),
    )


def search_neutral_propagation_radius(
    repository: str | Path | None = None,
) -> PropagationRadiusSearchResult:
    root = repository_path(repository)
    package = json.loads((root / SOURCES[1]).read_text(encoding="utf-8"))
    profile = package["profile_scale"]
    candidates = (
        _candidate(
            "author_ontology_r_prop",
            "CONDITIONAL_PROPAGATION_RADIUS_CANDIDATE",
            "r_prop: characteristic support scale of a propagating neutral boundary mode",
            "m (symbolic; no value supplied)",
            "length",
            SOURCES[0],
            "The ontology defines the physical neutral boundary-field domain and propagation role; it does not fix a numerical radius.",
            "action-derived numerical r_prop in metres",
            symbolic=True,
            neutrino_specific=True,
            zero_consistent=True,
        ),
        _candidate(
            "legacy_core_radius_r_c",
            "REFERENCE_ONLY",
            "r_c",
            "length (general variable)",
            "length",
            SOURCES[6],
            "The legacy core radius is not identified with the BHSM neutral propagation radius.",
            "neutral-specific identification theorem and numerical value",
            symbolic=True,
        ),
        _candidate(
            "boundary_profile_sigma",
            "DIMENSIONLESS_LENGTH_PROXY",
            float(profile["sigma"]),
            None,
            "dimensionless profile parameter",
            SOURCES[1],
            "Dimensionless sigma cannot become metres without a unit map.",
            "physical boundary length normalization",
        ),
        _candidate(
            "internal_profile_radius",
            "DIMENSIONLESS_LENGTH_PROXY",
            float(profile["r_internal_profile"]),
            None,
            "dimensionless internal radius",
            SOURCES[1],
            "An internal dimensionless profile radius is not a physical neutral propagation length.",
            "theorem identifying the internal radius with r_prop plus a metre conversion",
        ),
        _candidate(
            "empirical_or_mass_derived_length",
            "FORBIDDEN_EMPIRICAL_RADIUS",
            None,
            "m",
            "length",
            "comparison layer only",
            "Neutrino-limit, de Broglie, W-scale, and legacy particle-table lengths are forbidden theorem inputs.",
            "none; this route is rejected",
        ),
    )
    symbolic = any(row.status == "CONDITIONAL_PROPAGATION_RADIUS_CANDIDATE" for row in candidates)
    numeric = any(row.numeric_metres_available for row in candidates)
    status = "ARTIFACT_BACKED_PROPAGATION_RADIUS" if numeric else (
        "CONDITIONAL_PROPAGATION_RADIUS_CANDIDATE" if symbolic else "OPEN_MISSING_PROPAGATION_LOCALIZATION_RADIUS"
    )
    checked = tuple(path for path in SOURCES if (root / path).is_file())
    return PropagationRadiusSearchResult(
        candidate_key="neutral_propagation_radius_search",
        status=status,
        value="r_prop" if symbolic else None,
        unit="m (symbolic only)" if symbolic else None,
        dimension="length",
        source_type="author ontology conditional candidate plus artifact search",
        source_artifacts=checked,
        provenance=clean_provenance(checked),
        author_ontology_dependency="NEUTRINO_MASS_IS_PROPAGATION_LOCKED_CURVATURE_RESPONSE",
        claim_boundary="A symbolic radius domain is defined, but no physical metre value is derived.",
        remaining_missing_object="action-derived numerical r_prop in metres and its neutral-mode support theorem",
        candidates=candidates,
        numeric_metres_found=numeric,
        symbolic_candidate_found=symbolic,
        **common_guard_fields(),
    )

