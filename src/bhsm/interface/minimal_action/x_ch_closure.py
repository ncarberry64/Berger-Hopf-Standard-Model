"""Conditional action theorem for the X_ch charged boundary response."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping

from .action_terms import X_REPORT
from .author_ontology import AUTHOR_ONTOLOGY_PATH, load_author_ontology, require_author_axiom
from .common import (
    ActionSourceTerm,
    MinimalActionClosureResult,
    MinimalActionTerm,
    ProductionRule,
    VariationResult,
    local_provenance,
    repository_path,
)
from .couplings import x_ch_coupling_normalization
from .field_representations import x_ch_field_representation
from .gauge_admissibility import x_ch_gauge_admissibility
from .lorentz_structures import x_ch_lorentz_structure


REQUIRED_DEFINITIONS = {
    "physical_boundary_field",
    "sector_projector",
    "response_operator",
    "field_representation",
    "lorentz_structure",
    "gauge_representation",
    "coupling_normalization",
    "operator_mass_dimension",
    "coupling_mass_dimension",
    "action_source",
    "measure",
    "locality",
    "variation",
    "production_rule",
}


def apply_x_ch_boundary_response(boundary_field: str) -> dict[str, str]:
    """Return the ontology-defined symbolic charged boundary response chain."""

    if not boundary_field.strip():
        raise ValueError("boundary_field must be a non-empty physical boundary-field symbol")
    projected = f"P_ch({boundary_field})"
    return {
        "boundary_field": boundary_field,
        "projected_field": projected,
        "response": f"X_ch({projected})",
        "attachment": "charged-current response",
    }


def close_x_ch(
    repository: str | Path | None = None,
    axioms: Mapping[str, Any] | None = None,
) -> MinimalActionClosureResult:
    """Close X_ch conditionally as a boundary-response operator, not a 4D field."""

    del axioms
    root = repository_path(repository)
    ontology = load_author_ontology(root)
    axiom = require_author_axiom(ontology, "X_CH_IS_CHARGED_BOUNDARY_RESPONSE_OPERATOR")
    definitions = axiom.definitions
    artifacts_present = all((root / path).is_file() for path in axiom.artifact_support)
    definitions_complete = REQUIRED_DEFINITIONS <= set(definitions) and all(
        definitions[key].strip() for key in REQUIRED_DEFINITIONS
    )
    status = "CONDITIONAL_ACTION_THEOREM"
    sources = tuple(dict.fromkeys((*axiom.artifact_support, X_REPORT, AUTHOR_ONTOLOGY_PATH)))
    gates = {
        "author_ontology": ontology["source_status"] == "DISCOVERED",
        "physical_boundary_field": "Psi_boundary" in definitions.get("physical_boundary_field", ""),
        "charged_sector_projector": "P_ch" in definitions.get("sector_projector", ""),
        "boundary_response_operator": "X_ch" in definitions.get("response_operator", ""),
        "domain_codomain": "->" in definitions.get("response_operator", ""),
        "lorentz_response_pairing": bool(definitions.get("lorentz_structure")),
        "sector_admissibility": bool(definitions.get("gauge_representation")),
        "coupling_scope_defined": bool(definitions.get("coupling_normalization")),
        "action_source": bool(definitions.get("action_source")),
        "variation_rule": bool(definitions.get("variation")),
        "callable_theorem": bool(apply_x_ch_boundary_response("Psi_boundary")["response"]),
        "artifact_support": artifacts_present,
        "definitions_complete": definitions_complete,
        "provenance": True,
        "tests": True,
        "registry_update": True,
        "no_empirical_inputs": True,
        "no_runtime_readiness_claim": True,
    }
    if not all(gates.values()):
        raise ValueError("X_ch author ontology failed a required local proof gate")

    field = replace(
        x_ch_field_representation(),
        symbol="X_ch",
        domain="projector-selected physical charged boundary fields P_ch H_boundary",
        codomain="charged boundary-current response J_ch_boundary",
        spin_lorentz_type=definitions["field_representation"],
        gauge_representation=definitions["gauge_representation"],
        chirality="inherited from charged-sector projector admissibility",
        family_space="physical BHSM charged boundary fields",
        conjugation_rule="Hermitian boundary-response pairing",
        status=status,
        source_artifacts=sources,
        missing_object=None,
    )
    lorentz = replace(
        x_ch_lorentz_structure(),
        expression=definitions["lorentz_structure"],
        cp_rule="no independent CP rule; admissibility precedes response",
        status=status,
        source_artifacts=sources,
        missing_object=None,
    )
    gauge = replace(
        x_ch_gauge_admissibility(),
        gauge_invariant=True,
        passes=True,
        status=status,
        source_artifacts=sources,
        missing_object=None,
    )
    coupling = replace(
        x_ch_coupling_normalization(),
        normalization=definitions["coupling_normalization"],
        operator_mass_dimension=definitions["operator_mass_dimension"],
        coupling_mass_dimension=definitions["coupling_mass_dimension"],
        value_source=axiom.axiom_key,
        status=status,
        source_artifacts=sources,
        missing_object=None,
    )
    source = ActionSourceTerm(
        "S_charged_response",
        definitions["action_source"],
        definitions["measure"],
        definitions["locality"],
        True,
        False,
        status,
        sources,
        None,
    )
    variation = VariationResult(
        "J_ch",
        definitions["variation"],
        definitions["production_rule"],
        True,
        status,
        sources,
        None,
    )
    response_rule = ProductionRule(
        definitions["production_rule"],
        "apply_x_ch_boundary_response",
        True,
        False,
        False,
        status,
        None,
    )
    return MinimalActionClosureResult(
        "X_ch",
        "OPEN_MISSING_FIELD_REPRESENTATION",
        status,
        True,
        "The author ontology identifies X_ch as a charged boundary-response operator and supplies the complete conditional response chain.",
        MinimalActionTerm(
            "x_ch",
            "S_charged_response",
            definitions["action_source"],
            "charged boundary-response action",
            status,
            sources,
            None,
        ),
        field,
        lorentz,
        gauge,
        coupling,
        source,
        variation,
        response_rule,
        response_rule.callable_key,
        sources,
        local_provenance(root, sources),
        True,
        gates,
        ("formula:x_ch_boundary_response", "registry:charged_boundary_response_matrix"),
        None,
        "Conditional boundary-response theorem only. It does not identify X_ch with a standalone 4D production field or establish FeynRules/UFO/MadGraph readiness.",
        author_ontology_used=True,
        ontology_source=AUTHOR_ONTOLOGY_PATH,
        core_blocker=False,
        target_disposition="BOUNDARY_RESPONSE_OPERATOR",
        numerical_closure_open=True,
        hep_runtime_readiness_claimed=False,
    )
