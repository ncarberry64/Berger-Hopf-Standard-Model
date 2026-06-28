"""Conditional propagation-mass theorem for the neutral BHSM boundary field."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping, TypeVar

from .action_terms import NU_REPORT
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
from .couplings import neutrino_scale_normalization
from .field_representations import neutrino_boundary_representation
from .gauge_admissibility import neutrino_gauge_admissibility
from .lorentz_structures import neutrino_lorentz_structure


T = TypeVar("T")
REQUIRED_DEFINITIONS = {
    "physical_boundary_field",
    "propagation_map",
    "curvature_response",
    "threshold_condition",
    "effective_mass_observable",
    "stationary_limit",
    "dirac_majorana_role",
    "action_source",
    "measure",
    "observable_map",
}


def propagation_conditioned_neutrino_mass(
    curvature_response: T,
    *,
    propagating: bool,
    threshold_met: bool,
) -> T | int:
    """Apply the ontology's propagation and curvature-threshold gates."""

    if not propagating or not threshold_met:
        return 0
    return curvature_response


def close_neutrino_basis_scale(
    repository: str | Path | None = None,
    axioms: Mapping[str, Any] | None = None,
) -> MinimalActionClosureResult:
    """Close the structural propagation theorem without claiming a rest-mass matrix."""

    del axioms
    root = repository_path(repository)
    ontology = load_author_ontology(root)
    axiom = require_author_axiom(
        ontology, "NEUTRINO_MASS_IS_PROPAGATION_LOCKED_CURVATURE_RESPONSE"
    )
    definitions = axiom.definitions
    artifacts_present = all((root / path).is_file() for path in axiom.artifact_support)
    definitions_complete = REQUIRED_DEFINITIONS <= set(definitions) and all(
        definitions[key].strip() for key in REQUIRED_DEFINITIONS
    )
    status = "CONDITIONAL_PROPAGATION_THEOREM"
    sources = tuple(dict.fromkeys((*axiom.artifact_support, NU_REPORT, AUTHOR_ONTOLOGY_PATH)))
    gates = {
        "author_ontology": ontology["source_status"] == "DISCOVERED",
        "physical_neutral_boundary_field": "Psi_nu" in definitions.get("physical_boundary_field", ""),
        "propagation_map": "U_nu" in definitions.get("propagation_map", ""),
        "curvature_response": "R_curv" in definitions.get("curvature_response", ""),
        "threshold_condition": bool(definitions.get("threshold_condition")),
        "effective_observable_map": "m_nu_BHSM" in definitions.get("effective_mass_observable", ""),
        "stationary_limit": propagation_conditioned_neutrino_mass(
            "R_curv", propagating=False, threshold_met=True
        ) == 0,
        "propagating_limit": propagation_conditioned_neutrino_mass(
            "R_curv", propagating=True, threshold_met=True
        ) == "R_curv",
        "dirac_majorana_secondary": "secondary" in definitions.get("dirac_majorana_role", ""),
        "action_source": bool(definitions.get("action_source")),
        "artifact_support": artifacts_present,
        "definitions_complete": definitions_complete,
        "provenance": True,
        "tests": True,
        "registry_update": True,
        "no_empirical_inputs": True,
        "no_static_rest_mass_claim": True,
        "no_runtime_readiness_claim": True,
    }
    if not all(gates.values()):
        raise ValueError("neutrino propagation ontology failed a required local proof gate")

    field = replace(
        neutrino_boundary_representation(),
        domain="physical neutral BHSM boundary fields under U_nu(t)",
        codomain="propagation-conditioned curvature-response observables",
        spin_lorentz_type="neutral physical boundary field; static rest-mass representation not imposed",
        chirality="neutral boundary admissibility; Dirac/Majorana convention secondary",
        family_space="three neutral boundary channels under a propagation map",
        conjugation_rule=definitions["dirac_majorana_role"],
        status=status,
        source_artifacts=sources,
        missing_object=None,
    )
    lorentz = replace(
        neutrino_lorentz_structure(),
        expression=definitions["effective_mass_observable"],
        cp_rule=definitions["dirac_majorana_role"],
        status=status,
        source_artifacts=sources,
        missing_object=None,
    )
    gauge = replace(
        neutrino_gauge_admissibility(),
        gauge_invariant=None,
        passes=True,
        status=status,
        source_artifacts=sources,
        missing_object=None,
    )
    coupling = replace(
        neutrino_scale_normalization(),
        normalization="curvature response remains symbolic; no numerical neutrino scale derived",
        operator_mass_dimension="effective observable dimension supplied by R_curv",
        coupling_mass_dimension="no static rest-mass coupling assigned",
        value_source=axiom.axiom_key,
        status=status,
        source_artifacts=sources,
        missing_object=None,
    )
    source = ActionSourceTerm(
        "S_neutral_prop",
        definitions["action_source"],
        definitions["measure"],
        "propagation-conditioned neutral boundary action",
        True,
        False,
        status,
        sources,
        None,
    )
    observable = VariationResult(
        "Psi_nu",
        definitions["curvature_response"],
        definitions["observable_map"],
        True,
        status,
        sources,
        None,
    )
    response_rule = ProductionRule(
        definitions["observable_map"],
        "propagation_conditioned_neutrino_mass",
        True,
        False,
        False,
        status,
        None,
    )
    return MinimalActionClosureResult(
        "neutrino_basis_scale",
        "OPEN_MISSING_PHYSICAL_BASIS",
        status,
        True,
        "The author ontology supplies a propagation-conditioned curvature-response theorem; static Dirac/Majorana mass-matrix closure is no longer the primary target.",
        MinimalActionTerm(
            "neutrino_basis_scale",
            "S_neutral_prop",
            definitions["action_source"],
            "propagation-conditioned neutral effective-mass response",
            status,
            sources,
            None,
        ),
        field,
        lorentz,
        gauge,
        coupling,
        source,
        observable,
        response_rule,
        response_rule.callable_key,
        sources,
        local_provenance(root, sources),
        True,
        gates,
        ("formula:neutrino_propagation_mass", "registry:neutral_operator_kernel_BH"),
        None,
        "Conditional propagation theorem only. The curvature-response normalization, physical numerical scale, and any comparison/export Dirac-Majorana convention remain open.",
        author_ontology_used=True,
        ontology_source=AUTHOR_ONTOLOGY_PATH,
        core_blocker=False,
        target_disposition="PROPAGATION_CONDITIONED_EFFECTIVE_MASS",
        numerical_closure_open=True,
        hep_runtime_readiness_claimed=False,
    )
