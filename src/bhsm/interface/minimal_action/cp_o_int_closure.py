"""Minimal-action decision for standalone CP O_int."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
from dataclasses import replace

from .action_terms import CP_REPORT, cp_action_source, enabled_complete_axiom, load_minimal_action_axioms, missing_variation
from .common import MinimalActionClosureResult, MinimalActionTerm, ProductionRule, local_provenance, repository_path
from .couplings import cp_coupling_normalization
from .field_representations import cp_field_representation
from .gauge_admissibility import cp_gauge_admissibility
from .lorentz_structures import cp_lorentz_structure


MISSING = "action-derived CP O_int source with normalized coupling, measure, variation, and production rule"


def close_cp_o_int(
    repository: str | Path | None = None,
    axioms: Mapping[str, Any] | None = None,
) -> MinimalActionClosureResult:
    root = repository_path(repository)
    axiom = enabled_complete_axiom(load_minimal_action_axioms(root, axioms), "cp_o_int")
    promoted = axiom is not None
    status = "CONDITIONAL_ACTION_THEOREM" if promoted else "OPEN_MISSING_ACTION_SOURCE"
    field = cp_field_representation()
    lorentz = cp_lorentz_structure()
    gauge = cp_gauge_admissibility()
    coupling = cp_coupling_normalization()
    source = cp_action_source()
    variation = missing_variation("O_int", status, source.source_artifacts, MISSING)
    gates = {
        "formal_theorem": True,
        "domain_codomain": True,
        "field_representation_candidate": True,
        "lorentz_structure_candidate": True,
        "sector_admissibility_candidate": True,
        "coupling_normalization": promoted,
        "action_source": promoted,
        "variation_rule": promoted,
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
        field = replace(field, spin_lorentz_type=str(definitions["field_representation"]), gauge_representation=str(definitions["gauge_representation"]), status=status, source_artifacts=axiom_source, missing_object=None)
        lorentz = replace(lorentz, expression=str(definitions["lorentz_structure"]), status=status, source_artifacts=axiom_source, missing_object=None)
        gauge = replace(gauge, gauge_invariant=True, passes=True, status=status, source_artifacts=axiom_source, missing_object=None)
        coupling = replace(coupling, normalization=str(definitions["coupling_normalization"]), operator_mass_dimension=str(definitions["operator_mass_dimension"]), coupling_mass_dimension=str(definitions["coupling_mass_dimension"]), value_source=str(axiom["axiom_key"]), status=status, source_artifacts=axiom_source, missing_object=None)
        source = replace(source, expression=str(definitions["action_source"]), integration_measure=str(definitions["measure"]), locality=str(definitions["locality"]), status=status, source_artifacts=axiom_source, missing_object=None)
        variation = replace(variation, source_expression=str(definitions["variation"]), equation_or_current=str(definitions["production_rule"]), defined=True, status=status, source_artifacts=axiom_source, missing_object=None)
    production = ProductionRule(
        variation.equation_or_current,
        "cp_o_int_production_theorem",
        promoted,
        promoted,
        promoted,
        "ACTION_LEVEL_RUNTIME_GATED" if promoted else status,
        None if promoted else MISSING,
    )
    sources = tuple(dict.fromkeys((*source.source_artifacts, CP_REPORT)))
    return MinimalActionClosureResult(
        "cp_o_int",
        "OPEN_MISSING_ACTION_SOURCE",
        status,
        promoted,
        "Explicit author axiom supplies every action object." if promoted else "Local artifacts stop at a symbolic density; no action-derived source or variation exists.",
        MinimalActionTerm("cp_o_int", "S_phase", "G_raw exp(i delta_BH) O_int + h.c.", "standalone CP interaction", status, sources, None if promoted else MISSING),
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
        ("formula:cp_o_int_standalone_attachment", "registry:cp_holonomy_phase_attachment"),
        None if promoted else MISSING,
        "The artifact-backed phase and symbolic candidate do not supply an action theorem by themselves.",
    )
