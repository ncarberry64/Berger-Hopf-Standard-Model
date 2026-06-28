"""Assemble the BHSM neutral radius/curvature closure report."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .boundary_stiffness import search_boundary_stiffness
from .common import repository_path
from .neutral_mass_candidate import compute_dimensionful_neutrino_mass_candidate
from .neutral_physical_curvature import search_neutral_physical_curvature_map
from .propagation_radius_search import search_neutral_propagation_radius
from .radius_curvature_common import (
    NeutralRadiusCurvatureClosureResult,
    clean_provenance,
    common_guard_fields,
)
from .transport_normalization import search_transport_normalization


ARTIFACT_PATHS = {
    "manifest": "artifacts/BHSM_neutral_radius_curvature_manifest_v1_2.json",
    "radius": "artifacts/BHSM_neutral_propagation_radius_search_v1_2.json",
    "curvature": "artifacts/BHSM_neutral_physical_curvature_map_v1_2.json",
    "closure": "artifacts/BHSM_neutral_radius_curvature_closure_v1_2.json",
    "mass": "artifacts/BHSM_dimensionful_neutrino_mass_candidate_v1_2.json",
    "report": "artifacts/BHSM_neutral_radius_curvature_report_v1_2.json",
    "claims": "artifacts/BHSM_neutral_radius_curvature_claim_policy_v1_2.json",
}

REQUIRED_STATEMENTS = (
    "The curvature mass bridge requires both a propagation/localization radius and a physical neutral curvature map.",
    "A symbolic propagation radius does not by itself produce a physical neutrino mass.",
    "A dimensionless neutral kernel response is not by itself a curvature in m^-2.",
    "BHSM does not use neutrino limits, PDG values, W calibration, or legacy particle threshold tables to set r_prop or k_neutral,eff.",
)


def build_neutral_radius_curvature_closure(
    repository: str | Path | None = None,
) -> NeutralRadiusCurvatureClosureResult:
    root = repository_path(repository)
    radius = search_neutral_propagation_radius(root)
    curvature = search_neutral_physical_curvature_map(root)
    stiffness = search_boundary_stiffness(root)
    transport = search_transport_normalization(root)
    sources = tuple(dict.fromkeys((*radius.source_artifacts, *curvature.source_artifacts)))
    symbolic = radius.symbolic_candidate_found and curvature.symbolic_candidate_found
    numeric = radius.numeric_metres_found and curvature.numeric_per_m2_found
    # K=-nabla^2 ln rho has L^-2, so the documented r^2 k functional
    # leaves c^2/G with dimension mass/length rather than mass.
    dimension_ok = False
    return NeutralRadiusCurvatureClosureResult(
        candidate_key="neutral_radius_curvature_closure",
        status="DIMENSIONFUL_MASS_NOT_AVAILABLE",
        value="(r_prop, k_neutral,eff)",
        unit="(m, m^-2), symbolic only",
        dimension="length x inverse_length_squared",
        source_type="author-ontology conditional candidates plus artifact search",
        source_artifacts=sources,
        provenance=clean_provenance(sources),
        author_ontology_dependency="physical neutral boundary field and propagation-locked curvature response",
        claim_boundary=(
            "Symbolic domains exist, but no numeric unit map exists. In addition, the legacy r^2 k functional has output dimension mass/length under its stated curvature definition."
        ),
        remaining_missing_object=(
            f"{radius.remaining_missing_object}; {curvature.remaining_missing_object}; "
            "action-derived dimensionally consistent mass normalization or additional length factor"
        ),
        radius=radius,
        curvature_map=curvature,
        boundary_stiffness=stiffness,
        transport_normalization=transport,
        symbolic_bridge_available=symbolic,
        numeric_bridge_available=numeric,
        dimensional_consistency_passed=dimension_ok,
        legacy_functional_output_dimension="mass_per_length",
        **common_guard_fields(),
    )


def build_neutral_radius_curvature_report(
    repository: str | Path | None = None,
) -> dict[str, Any]:
    closure = build_neutral_radius_curvature_closure(repository)
    mass = compute_dimensionful_neutrino_mass_candidate(closure, repository=repository)
    return {
        "report_name": "BHSM Neutral Propagation Radius and Physical Curvature Mapping",
        "version": "1.2",
        "public_status": "structural architecture integrated conditional; numerical closure open",
        "closure": closure.to_dict(),
        "dimensionful_mass_candidate": mass.to_dict(),
        "preferred_particle_mass_route": "conditional action-normalized neutral spectral gap",
        "legacy_gravitational_formula_used_as_mass_formula": False,
        "frozen_predictions_changed": False,
        "production_physics_model_logic_changed": False,
        "internet_required": False,
        "external_hep_tools_required": False,
    }


def neutral_radius_curvature_report_to_markdown(report: dict[str, Any]) -> str:
    closure = report["closure"]
    radius = closure["radius"]
    curvature = closure["curvature_map"]
    mass = report["dimensionful_mass_candidate"]
    lines = [
        "# BHSM Neutral Radius and Physical Curvature Closure",
        "",
        f"Overall status: `{closure['status']}`.",
        "",
        *REQUIRED_STATEMENTS,
        "",
        "| Gate | Status | Numeric physical value |",
        "| --- | --- | --- |",
        f"| `r_prop` | `{radius['status']}` | {'yes' if radius['numeric_metres_found'] else 'no'} |",
        f"| `k_neutral,eff` | `{curvature['status']}` | {'yes' if curvature['numeric_per_m2_found'] else 'no'} |",
        f"| Dimensionful mass | `{mass['status']}` | {'yes' if mass['dimensionful_mass_available'] else 'no'} |",
        f"| Legacy functional unit check | `{'PASS' if closure['dimensional_consistency_passed'] else 'FAIL: mass_per_length'}` | no |",
        "",
        f"Remaining object: {closure['remaining_missing_object']}.",
        "",
    ]
    return "\n".join(lines)


def _claim_policy() -> dict[str, Any]:
    return {
        "artifact_name": "BHSM Neutral Radius/Curvature Claim Policy",
        "version": "1.2",
        "allowed": [
            "BHSM includes an artifact-backed curvature mass bridge as a documented legacy functional.",
            "BHSM searches separately for the neutral propagation radius and the physical neutral curvature map.",
            "A dimensionful neutrino mass candidate requires r_prop in metres, k_neutral,eff in m^-2, and a dimensionally consistent mass functional.",
            "Conditional symbolic candidates do not produce eV/GeV mass by themselves.",
        ],
        "forbidden": [
            "BHSM empirically validates neutrino mass.",
            "BHSM centrally measures electron-neutrino mass.",
            "The electron-neutrino upper limit is used to set r_prop or k_neutral,eff.",
            "PDG/reference values are theorem inputs.",
            "W calibration is used as the neutral scale.",
            "Legacy particle threshold tables are no-fit BHSM derivations.",
            "Dimensionless radius or curvature proxies produce physical eV/GeV mass by themselves.",
        ],
        "dimensional_audit": {
            "K_dimension": "length^-2",
            "legacy_mass_formula": "(c^2/(2G)) r^2 k",
            "formula_output_dimension": "mass_per_length",
            "physical_mass_dimension_passed": False,
        },
        "required_statements": list(REQUIRED_STATEMENTS),
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
    }


def write_neutral_radius_curvature_artifacts(
    repository: str | Path | None = None,
) -> dict[str, Any]:
    root = repository_path(repository)
    report = build_neutral_radius_curvature_report(root)
    closure = report["closure"]
    payloads: dict[str, Any] = {
        "manifest": {
            "artifact_name": "BHSM Neutral Radius/Curvature Manifest",
            "version": "1.2",
            "artifact_paths": list(ARTIFACT_PATHS.values()),
            "status": closure["status"],
            "dimensionful_mass_output_produced": False,
            "frozen_predictions_changed": False,
        },
        "radius": closure["radius"],
        "curvature": closure["curvature_map"],
        "closure": closure,
        "mass": report["dimensionful_mass_candidate"],
        "report": report,
        "claims": _claim_policy(),
    }
    for key, relative in ARTIFACT_PATHS.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payloads[key], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
