"""Offline inventory of neutral action sources and exact normalization gaps."""

from __future__ import annotations

import json
from pathlib import Path

from ..neutrino_scale.common import repository_path
from .common import NeutralActionSourceSearchResult, guard_fields, provenance
from .neutral_action_terms import extract_neutral_action_terms


def search_neutral_action_sources(
    repository: str | Path | None = None,
) -> NeutralActionSourceSearchResult:
    root = repository_path(repository)
    terms = extract_neutral_action_terms(root)
    closure_map_path = root / "data/bhsm_numerical_input_closure_map.json"
    if not closure_map_path.is_file():
        raise FileNotFoundError("data/bhsm_numerical_input_closure_map.json")
    closure_map = json.loads(closure_map_path.read_text(encoding="utf-8"))
    variation_found = closure_map["explicit_scalar_topographic_boundary_variation"]["status"] == "DERIVED_CONDITIONAL"
    collar_formula_found = closure_map["collar_measure_extrinsic_geometry"]["status"] == "DERIVED_CONDITIONAL"
    complete = closure_map["complete_scalar_topographic_collar_action"]["status"] != "OPEN_LOCALIZABLE"
    sources = tuple(dict.fromkeys(path for term in terms for path in term.source_artifacts))
    return NeutralActionSourceSearchResult(
        candidate_key="neutral_action_source_search",
        status="OPEN_MISSING_NEUTRAL_ACTION_NORMALIZATION",
        value="S_nu = S_bulk + S_boundary + S_support (partial source chain)",
        unit=None,
        dimension="action, physical normalization open",
        numeric_value=None,
        symbolic_value="S_nu[Phi_nu; chi_nu,lambda_nu,J,U_nu,R_curv]",
        source_type="offline local action and theorem-discharge inventory",
        source_artifacts=sources,
        source_equations=tuple(term.symbolic_value or "" for term in terms),
        provenance=provenance(sources),
        author_ontology_dependency="physical boundary modes with propagation-locked and interaction-supported neutral response",
        claim_boundary=(
            "The repository contains a real partial variational/action chain, but no complete normalized neutral action "
            "that fixes Z_nu, A_nu, the support measure, transport length, or physical curvature units."
        ),
        remaining_missing_object=(
            "complete normalized neutral action: chi_nu and lambda_nu values; normalized collar/support measure; "
            "orientation and edge data; profile/embedding; neutral curvature-penalty identification"
        ),
        terms=terms,
        artifact_backed_terms_found=bool(sources),
        conditional_variational_structure_found=variation_found and collar_formula_found,
        complete_normalized_action_found=complete,
        **guard_fields(),
    )
