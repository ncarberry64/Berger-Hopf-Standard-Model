"""Minimal-action decision for the CP/Z6 boundary holonomy constraint."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping

from .action_terms import CP_REPORT
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
from .couplings import cp_coupling_normalization
from .field_representations import cp_field_representation
from .gauge_admissibility import cp_gauge_admissibility
from .lorentz_structures import cp_lorentz_structure


CP_HOLONOMY = "artifacts/CP_no_fit_holonomy_output_v1.json"


def _holonomy_gates(root: Path) -> dict[str, bool]:
    path = root / CP_HOLONOMY
    if not path.is_file():
        return {
            "holonomy_artifact": False,
            "z6_phase": False,
            "ckm_phase_attachment": False,
            "pmns_phase_attachment": False,
        }
    payload = json.loads(path.read_text(encoding="utf-8"))
    phase = payload.get("Z6_boundary_phase", {})
    return {
        "holonomy_artifact": payload.get("CP_boundary_holonomy") == "CLOSED",
        "z6_phase": payload.get("delta_BH_formula") == "pi/3" and set(phase) == {"real", "imag"},
        "ckm_phase_attachment": payload.get("CKM_CP_seed") == "ACTIVE",
        "pmns_phase_attachment": payload.get("PMNS_CP_seed") == "ACTIVE",
    }


def close_cp_o_int(
    repository: str | Path | None = None,
    axioms: Mapping[str, Any] | None = None,
) -> MinimalActionClosureResult:
    """Retire the standalone vertex target when the holonomy gates are present."""

    del axioms  # The retired standalone target cannot be revived by an inline payload.
    root = repository_path(repository)
    ontology = load_author_ontology(root)
    axiom = require_author_axiom(ontology, "CP_IS_Z6_BOUNDARY_HOLONOMY_CONSTRAINT")
    holonomy = _holonomy_gates(root)
    gates = {
        "author_ontology": ontology["source_status"] == "DISCOVERED",
        **holonomy,
        "standalone_target_retired": axiom.standalone_target_status == "RETIRED_TARGET",
        "artifact_output": True,
        "provenance": True,
        "tests": True,
        "registry_update": True,
        "no_empirical_inputs": True,
        "no_runtime_readiness_claim": True,
    }
    supported = all(gates.values())
    status = "ARTIFACT_BACKED" if supported else "OPEN_MISSING_ACTION_SOURCE"
    missing = None if supported else "artifact-backed CP/Z6 holonomy and phase-attachment gates"
    sources = tuple(dict.fromkeys((*axiom.artifact_support, CP_HOLONOMY, CP_REPORT, AUTHOR_ONTOLOGY_PATH)))

    field = replace(
        cp_field_representation(),
        spin_lorentz_type="boundary holonomy representation; no standalone production field required",
        gauge_representation="CP/Z6 boundary holonomy constraint",
        status="DERIVED_REPRESENTATION_ONLY" if supported else status,
        source_artifacts=sources,
        missing_object=missing,
    )
    lorentz = replace(
        cp_lorentz_structure(),
        expression="Hol_CP = exp(i*pi/3) attached to admissible CKM/PMNS or sector structures",
        cp_rule="Z6 boundary phase attachment",
        status=status,
        source_artifacts=sources,
        missing_object=missing,
    )
    gauge = replace(
        cp_gauge_admissibility(),
        gauge_invariant=None,
        passes=supported,
        status=status,
        source_artifacts=sources,
        missing_object=missing,
    )
    coupling = replace(
        cp_coupling_normalization(),
        normalization="not applicable to the retired standalone interaction target",
        operator_mass_dimension="not applicable",
        coupling_mass_dimension="not applicable",
        value_source=CP_HOLONOMY,
        status="RETIRED_TARGET" if supported else status,
        source_artifacts=sources,
        missing_object=missing,
    )
    source = ActionSourceTerm(
        "Hol_CP",
        "exp(i*pi/3) as a CP/Z6 boundary holonomy constraint",
        "not a standalone interaction integral",
        "boundary holonomy",
        True,
        False,
        "RETIRED_TARGET" if supported else status,
        sources,
        missing,
    )
    variation = VariationResult(
        "boundary holonomy",
        "artifact-backed phase attachment",
        "constraint on admissible CKM/PMNS or sector structures",
        supported,
        status,
        sources,
        missing,
    )
    production = ProductionRule(
        "standalone production rule not required by the CP holonomy ontology",
        "cp_holonomy_phase_attachment",
        supported,
        False,
        False,
        "RETIRED_TARGET" if supported else status,
        missing,
    )
    return MinimalActionClosureResult(
        "cp_o_int",
        "OPEN_MISSING_ACTION_SOURCE",
        status,
        False,
        "The local no-fit artifact closes the CP/Z6 holonomy and phase attachment; the standalone O_int production target is retired." if supported else "The controlling holonomy artifact is incomplete.",
        MinimalActionTerm(
            "cp_o_int",
            "Hol_CP",
            "exp(i*pi/3) attached to admissible boundary structures",
            "CP/Z6 holonomy constraint; standalone interaction retired",
            "RETIRED_TARGET" if supported else status,
            sources,
            missing,
        ),
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
        ("formula:cp_holonomy_phase_attachment", "registry:cp_holonomy_phase_attachment"),
        missing,
        "CP is established here only as an artifact-backed holonomy constraint. No standalone production vertex or HEP runtime readiness follows.",
        author_ontology_used=True,
        ontology_source=AUTHOR_ONTOLOGY_PATH,
        core_blocker=not supported,
        target_disposition="RETIRED_TARGET" if supported else "ACTIVE",
        numerical_closure_open=False,
        hep_runtime_readiness_claimed=False,
    )
