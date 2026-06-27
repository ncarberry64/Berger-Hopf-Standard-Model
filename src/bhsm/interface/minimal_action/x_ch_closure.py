"""Minimal-action decision for the X_ch charged response."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
from dataclasses import replace

from .action_terms import X_REPORT, enabled_complete_axiom, load_minimal_action_axioms, missing_variation, x_ch_action_source
from .common import MinimalActionClosureResult, MinimalActionTerm, ProductionRule, local_provenance, repository_path
from .couplings import x_ch_coupling_normalization
from .field_representations import x_ch_field_representation
from .gauge_admissibility import x_ch_gauge_admissibility
from .lorentz_structures import x_ch_lorentz_structure


MISSING = "action-derived X_ch field representation"


def close_x_ch(
    repository: str | Path | None = None,
    axioms: Mapping[str, Any] | None = None,
) -> MinimalActionClosureResult:
    root = repository_path(repository)
    axiom = enabled_complete_axiom(load_minimal_action_axioms(root, axioms), "X_ch")
    promoted = axiom is not None
    status = "CONDITIONAL_ACTION_THEOREM" if promoted else "OPEN_MISSING_FIELD_REPRESENTATION"
    field = x_ch_field_representation()
    lorentz = x_ch_lorentz_structure()
    gauge = x_ch_gauge_admissibility()
    coupling = x_ch_coupling_normalization()
    source = x_ch_action_source()
    variation = missing_variation("X_ch", status, source.source_artifacts, MISSING)
    gates = {
        "formal_theorem": True,
        "domain_codomain": False,
        "field_representation": promoted,
        "lorentz_structure": promoted,
        "gauge_admissibility": promoted,
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
    production = ProductionRule("not defined" if not promoted else str(axiom["definitions"]["production_rule"]), "x_ch_production_vertex", promoted, promoted, promoted, "ACTION_LEVEL_RUNTIME_GATED" if promoted else status, None if promoted else MISSING)
    sources = tuple(dict.fromkeys((*source.source_artifacts, X_REPORT)))
    return MinimalActionClosureResult(
        "X_ch",
        "OPEN_EXACT_MISSING_THEOREM",
        status,
        promoted,
        "Explicit author axiom supplies the X_ch action theorem." if promoted else "The source matrix does not determine a physical X_ch field.",
        MinimalActionTerm("x_ch", "S_charged", "Psi_ch_bar C_ch_boundary Psi_ch X_ch", "charged response", status, sources, None if promoted else MISSING),
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
        ("formula:x_ch_production_vertex", "registry:charged_boundary_response_matrix"),
        None if promoted else MISSING,
        "C_ch_boundary is an artifact-backed source matrix, not an X_ch field theorem.",
    )
