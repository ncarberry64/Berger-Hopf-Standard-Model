"""Audit partial-action support for the measurement-supported response cone."""

from __future__ import annotations

from pathlib import Path

from ..neutrino_scale.common import repository_path
from ..neutrino_spectral.admissible_domain import DOMAIN_CONSTRAINTS
from ..neutrino_spectral.positivity_proof import prove_neutral_positivity_on_domain
from .action_source_search import search_neutral_action_sources
from .common import ActionDerivedResponseConeResult, guard_fields, provenance


def derive_response_cone_from_neutral_action(
    repository: str | Path | None = None,
) -> ActionDerivedResponseConeResult:
    root = repository_path(repository)
    search = search_neutral_action_sources(root)
    proof = prove_neutral_positivity_on_domain(root)
    supporting_keys = {
        "neutral_propagation_source",
        "neutral_boundary_tangential_kinetic",
        "neutral_collar_measure",
        "measurement_interaction_support",
    }
    terms = tuple(term for term in search.terms if term.term_key in supporting_keys)
    sources = tuple(dict.fromkeys(path for term in terms for path in term.source_artifacts))
    partial = search.conditional_variational_structure_found and len(terms) == len(supporting_keys)
    complete = search.complete_normalized_action_found
    return ActionDerivedResponseConeResult(
        candidate_key="action_supported_neutral_response_cone",
        status=(
            "ARTIFACT_BACKED_ACTION_DERIVED_RESPONSE_CONE"
            if complete
            else "CONDITIONAL_ACTION_DERIVED_RESPONSE_CONE_CANDIDATE"
            if partial
            else "OPEN_MISSING_ACTION_DERIVED_RESPONSE_CONE"
        ),
        value="measurement-supported nonnegative response-magnitude cone",
        unit=None,
        dimension="normalized response domain",
        numeric_value=None,
        symbolic_value="C_nu={x in R^3: x_i>=0, ||x||_2=1, propagation and interaction support active}",
        source_type="author ontology plus partial variational boundary/collar action chain",
        source_artifacts=sources,
        source_equations=tuple(term.symbolic_value or "" for term in terms),
        provenance=provenance(sources),
        author_ontology_dependency="measurement/interaction support selects non-null neutral response",
        claim_boundary=(
            "Boundary kinetic variation, propagation support, and collar geometry partially support the cone, "
            "but the complete normalized action does not yet derive the response-magnitude map or all constraints uniquely."
        ),
        remaining_missing_object=(
            "complete normalized neutral action and variation deriving response magnitudes, active support, "
            "normalization, and admissible boundary data"
        ),
        constraints=DOMAIN_CONSTRAINTS,
        ontology_support=True,
        partial_action_support=partial,
        complete_action_derived=complete,
        positivity_proven_on_cone=proof.positivity_proven_without_thresholding,
        **guard_fields(),
    )
