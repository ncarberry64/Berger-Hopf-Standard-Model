"""Minimal-action decision for the physical neutrino map."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
from dataclasses import replace

from .action_terms import NU_REPORT, enabled_complete_axiom, load_minimal_action_axioms, missing_variation, neutrino_action_source
from .common import MinimalActionClosureResult, MinimalActionTerm, ProductionRule, local_provenance, repository_path
from .couplings import neutrino_scale_normalization
from .field_representations import neutrino_boundary_representation
from .gauge_admissibility import neutrino_gauge_admissibility
from .lorentz_structures import neutrino_lorentz_structure


MISSING = "map from the neutral boundary channel basis to physical neutrino states"


def close_neutrino_basis_scale(
    repository: str | Path | None = None,
    axioms: Mapping[str, Any] | None = None,
) -> MinimalActionClosureResult:
    root = repository_path(repository)
    axiom = enabled_complete_axiom(load_minimal_action_axioms(root, axioms), "neutrino_basis_scale")
    promoted = axiom is not None
    status = "CONDITIONAL_ACTION_THEOREM" if promoted else "OPEN_MISSING_PHYSICAL_BASIS"
    field = neutrino_boundary_representation()
    lorentz = neutrino_lorentz_structure()
    gauge = neutrino_gauge_admissibility()
    coupling = neutrino_scale_normalization()
    source = neutrino_action_source()
    variation = missing_variation("Psi_nu", status, source.source_artifacts, MISSING)
    gates = {
        "formal_theorem": True,
        "boundary_domain": True,
        "physical_basis": promoted,
        "dimensional_scale": promoted,
        "ordering_policy": promoted,
        "dirac_majorana_convention": promoted,
        "action_source": promoted,
        "observable_map": promoted,
        "callable_theorem": promoted,
        "artifact_output": True,
        "provenance": True,
        "tests": True,
        "registry_update": True,
        "no_empirical_inputs": True,
    }
    if promoted:
        definitions = axiom["definitions"]
        gates = {key: True for key in gates}
        axiom_source = (str(axiom["axiom_key"]),)
        field = replace(field, codomain=str(definitions["physical_basis_map"]), conjugation_rule=str(definitions["dirac_majorana_convention"]), status=status, source_artifacts=axiom_source, missing_object=None)
        lorentz = replace(lorentz, cp_rule=str(definitions["dirac_majorana_convention"]), status=status, source_artifacts=axiom_source, missing_object=None)
        gauge = replace(gauge, gauge_invariant=True, passes=True, status=status, source_artifacts=axiom_source, missing_object=None)
        coupling = replace(coupling, normalization=str(definitions["dimensional_scale"]), value_source=str(axiom["axiom_key"]), status=status, source_artifacts=axiom_source, missing_object=None)
        source = replace(source, expression=str(definitions["action_source"]), integration_measure=str(definitions["measure"]), status=status, source_artifacts=axiom_source, missing_object=None)
        variation = replace(variation, source_expression=str(definitions["ordering_policy"]), equation_or_current=str(definitions["observable_map"]), defined=True, status=status, source_artifacts=axiom_source, missing_object=None)
    production = ProductionRule("not defined" if not promoted else str(axiom["definitions"]["observable_map"]), "neutrino_physical_basis_scale", promoted, promoted, promoted, "ACTION_LEVEL_RUNTIME_GATED" if promoted else status, None if promoted else MISSING)
    sources = tuple(dict.fromkeys((*source.source_artifacts, NU_REPORT)))
    return MinimalActionClosureResult(
        "neutrino_basis_scale",
        "OPEN_MISSING_PHYSICAL_BASIS_AND_SCALE",
        status,
        promoted,
        "Explicit author axiom supplies basis, scale, ordering, and convention." if promoted else "K_nu defines a boundary basis operator but no physical state map.",
        MinimalActionTerm("neutrino_basis_scale", "S_neutral", "Psi_nu_bar K_nu Psi_nu", "neutral physical map", status, sources, None if promoted else MISSING),
        field,
        lorentz,
        gauge,
        coupling,
        source,
        variation,
        production,
        production.callable_key,
        sources,
        local_provenance(root, sources),
        True,
        gates,
        ("formula:neutrino_physical_basis_scale", "registry:neutral_operator_kernel_BH"),
        None if promoted else MISSING,
        "K_nu and PMNS artifacts do not determine a physical neutrino mass basis or scale.",
    )
