"""Assemble and export the neutral action/stiffness closure audit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..neutrino_scale.common import repository_path
from ..neutrino_spectral.positivity_report import build_neutral_positivity_report
from .action_source_search import search_neutral_action_sources
from .common import NeutralActionClosureReport, NeutralActionSpectralClosureResult, guard_fields, provenance
from .curvature_unit_map import derive_or_locate_physical_neutral_curvature_map
from .response_cone_derivation import derive_response_cone_from_neutral_action
from .stiffness_extraction import derive_neutral_stiffness_length


HBAR_SI = 1.054_571_817e-34
LIGHT_SPEED_SI = 299_792_458.0
EV_PER_JOULE = 1.0 / 1.602_176_634e-19
PUBLIC_STATUS = (
    "structural architecture integrated conditional; physical eV/GeV neutrino mass closure remains open "
    "unless numeric stiffness length and physical curvature map are derived"
)

ARTIFACT_PATHS = {
    "manifest": "artifacts/BHSM_neutral_action_closure_manifest_v1_5.json",
    "source_search": "artifacts/BHSM_neutral_action_source_search_v1_5.json",
    "terms": "artifacts/BHSM_neutral_action_terms_v1_5.json",
    "stiffness": "artifacts/BHSM_neutral_stiffness_length_v1_5.json",
    "curvature": "artifacts/BHSM_physical_neutral_curvature_map_v1_5.json",
    "cone": "artifacts/BHSM_action_derived_response_cone_v1_5.json",
    "closure": "artifacts/BHSM_neutral_action_spectral_closure_v1_5.json",
    "report": "artifacts/BHSM_neutral_action_closure_report_v1_5.json",
    "claims": "artifacts/BHSM_neutral_action_claim_policy_v1_5.json",
}

REQUIRED_STATEMENTS = (
    "BHSM has conditional dimensionless neutrino propagation closure, a conditional neutral spectral-mass theorem, and conditional measurement-supported admissible neutral positivity.",
    "Physical eV/GeV neutrino mass closure requires a numeric neutral stiffness length sqrt(A_nu/Z_nu) and a physical K_neutral,eff map in m^-2.",
    "An ontology-supported response cone is not the same as a complete-action-derived response cone.",
    "BHSM does not use neutrino limits, PDG values, W calibration, empirical fitting, or legacy particle threshold tables to set the neutral action scale.",
    "The admissible response cone is currently measurement/interaction-supported and conditionally positive, but its derivation from the complete neutral action remains open.",
)


def build_neutral_action_spectral_closure(
    repository: str | Path | None = None,
    *,
    stiffness_length_m: float | None = None,
    curvature_per_m2: float | None = None,
) -> NeutralActionSpectralClosureResult:
    root = repository_path(repository)
    stiffness = derive_neutral_stiffness_length(root)
    curvature = derive_or_locate_physical_neutral_curvature_map(root)
    cone = derive_response_cone_from_neutral_action(root)
    positivity = build_neutral_positivity_report(root)
    if stiffness_length_m is not None and stiffness_length_m < 0:
        raise ValueError("stiffness_length_m must be nonnegative")
    if curvature_per_m2 is not None and curvature_per_m2 < 0:
        raise ValueError("curvature_per_m2 must be nonnegative")
    numeric = stiffness_length_m is not None and curvature_per_m2 is not None
    gap = stiffness_length_m * curvature_per_m2 if numeric else None
    energy = HBAR_SI * LIGHT_SPEED_SI * gap if gap is not None else None
    mass_kg = HBAR_SI * gap / LIGHT_SPEED_SI if gap is not None else None
    mass_ev = energy * EV_PER_JOULE if energy is not None else None
    sources = tuple(dict.fromkeys((*stiffness.source_artifacts, *curvature.source_artifacts, *cone.source_artifacts)))
    return NeutralActionSpectralClosureResult(
        candidate_key="neutral_action_spectral_closure",
        status="DIMENSIONFUL_MASS_AVAILABLE" if numeric else "CONDITIONAL_NEUTRAL_SPECTRAL_MASS_CANDIDATE",
        value="m_nu c^2=hbar c sqrt(A_nu_gap/Z_nu) K_neutral,eff",
        unit="kg and eV/c^2" if numeric else "symbolic; physical units unavailable",
        dimension="mass via inverse_length gap",
        numeric_value=mass_ev,
        symbolic_value="mu_nu=sqrt(A_nu_gap/Z_nu)K_neutral,eff",
        source_type="partial neutral action, unit gates, and conditional admissible cone",
        source_artifacts=sources,
        source_equations=(
            "mu_nu=sqrt(A_nu_gap/Z_nu)K_neutral,eff",
            "E_nu=hbar c mu_nu",
            "m_nu=(hbar/c)mu_nu",
        ),
        provenance=provenance(sources),
        author_ontology_dependency="interaction-supported and propagation-locked neutral response",
        claim_boundary=(
            "Repository defaults remain symbolic and produce no mass. Optional explicit dimensional arguments test "
            "the unit path only and are not BHSM-derived or fitted values."
        ),
        remaining_missing_object=(
            "none for explicit unit-path inputs"
            if numeric
            else "numeric action-derived stiffness length in metres and physical K_neutral,eff in m^-2"
        ),
        stiffness=stiffness,
        curvature_map=curvature,
        response_cone=cone,
        admissible_positivity_status=positivity.status,
        inverse_length_gap_per_m=gap,
        energy_joule=energy,
        mass_kg=mass_kg,
        mass_eV=mass_ev,
        mass_GeV=mass_ev / 1.0e9 if mass_ev is not None else None,
        dimensionful_mass_available=numeric,
        dimensionful_mass_status="DIMENSIONFUL_MASS_AVAILABLE" if numeric else "DIMENSIONFUL_MASS_NOT_AVAILABLE",
        **guard_fields(),
    )


def build_neutral_action_closure_report(
    repository: str | Path | None = None,
) -> NeutralActionClosureReport:
    root = repository_path(repository)
    source_search = search_neutral_action_sources(root)
    closure = build_neutral_action_spectral_closure(root)
    sources = tuple(dict.fromkeys((*source_search.source_artifacts, *closure.source_artifacts)))
    return NeutralActionClosureReport(
        candidate_key="neutral_action_closure_report",
        status="DIMENSIONFUL_MASS_NOT_AVAILABLE",
        value="neutral action/stiffness/curvature/cone closure audit",
        unit=None,
        dimension="action and physical-unit closure report",
        numeric_value=None,
        symbolic_value="mu_nu=sqrt(A_nu_gap/Z_nu)K_neutral,eff",
        source_type="offline local neutral action closure package",
        source_artifacts=sources,
        source_equations=closure.source_equations,
        provenance=provenance(sources),
        author_ontology_dependency="interaction-supported and propagation-locked neutral response",
        claim_boundary="Partial action support and a symbolic spectral theorem are reported without physical mass promotion.",
        remaining_missing_object="numeric stiffness length in metres; physical curvature in m^-2; complete normalized neutral action",
        report_name="BHSM Neutral Action, Stiffness, and Physical Curvature Closure",
        version="1.5",
        public_status=PUBLIC_STATUS,
        source_search=source_search,
        stiffness=closure.stiffness,
        curvature_map=closure.curvature_map,
        response_cone=closure.response_cone,
        spectral_closure=closure,
        frozen_predictions_changed=False,
        production_physics_model_logic_changed=False,
        internet_required=False,
        external_hep_tools_required=False,
        libreoffice_required=False,
        **guard_fields(),
    )


def neutral_action_closure_report_to_markdown(report: NeutralActionClosureReport) -> str:
    rows = (
        ("Neutral action normalization", report.source_search.status),
        ("Kinetic stiffness Z_nu", report.stiffness.kinetic.status),
        ("Curvature penalty A_nu_gap", report.stiffness.curvature_penalty.status),
        ("Stiffness length", report.stiffness.status),
        ("Physical curvature map", report.curvature_map.status),
        ("Action-supported response cone", report.response_cone.status),
        ("Spectral theorem", report.spectral_closure.status),
        ("Dimensionful mass", report.spectral_closure.dimensionful_mass_status),
    )
    lines = [
        "# BHSM Neutral Action Closure",
        "",
        f"Public status: `{report.public_status}`.",
        "",
        *REQUIRED_STATEMENTS,
        "",
        "| Gate | Status |",
        "| --- | --- |",
        *(f"| {name} | `{status}` |" for name, status in rows),
        "",
        f"Remaining action object: {report.source_search.remaining_missing_object}.",
        f"Remaining mass object: {report.spectral_closure.remaining_missing_object}.",
        "",
    ]
    return "\n".join(lines)


def _claim_policy() -> dict[str, Any]:
    return {
        "artifact_name": "BHSM Neutral Action Claim Policy",
        "version": "1.5",
        "allowed": [
            "BHSM has a conditional neutral spectral mass theorem.",
            "BHSM distinguishes dimensionless propagation closure from physical eV/GeV mass closure.",
            "BHSM distinguishes ontology-supported response cones from action-derived response cones.",
            "A physical eV/GeV neutrino mass requires a numeric neutral stiffness length and a physical neutral curvature map.",
        ],
        "forbidden": [
            "BHSM empirically validates neutrino mass.",
            "BHSM centrally measures electron-neutrino mass.",
            "The electron-neutrino upper limit is used to set the neutral action scale.",
            "PDG/reference values are theorem inputs.",
            "W calibration is used.",
            "Legacy particle tables are derivation inputs.",
            "A symbolic stiffness length produces a physical eV/GeV mass by itself.",
            "A dimensionless neutral response is a physical m^-2 curvature by itself.",
            "The response cone is action-derived if it is only ontology-supported.",
        ],
        "required_statements": list(REQUIRED_STATEMENTS),
        "frozen_predictions_changed": False,
    }


def write_neutral_action_artifacts(
    repository: str | Path | None = None,
) -> NeutralActionClosureReport:
    root = repository_path(repository)
    report = build_neutral_action_closure_report(root)
    payloads: dict[str, Any] = {
        "manifest": {
            "artifact_name": "BHSM Neutral Action Closure Manifest",
            "version": "1.5",
            "artifact_paths": list(ARTIFACT_PATHS.values()),
            "public_status": report.public_status,
            "dimensionful_mass_output_produced": False,
            "frozen_predictions_changed": False,
        },
        "source_search": report.source_search.to_dict(),
        "terms": {"terms": [term.to_dict() for term in report.source_search.terms]},
        "stiffness": report.stiffness.to_dict(),
        "curvature": report.curvature_map.to_dict(),
        "cone": report.response_cone.to_dict(),
        "closure": report.spectral_closure.to_dict(),
        "report": report.to_dict(),
        "claims": _claim_policy(),
    }
    for key, relative in ARTIFACT_PATHS.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payloads[key], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
