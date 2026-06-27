"""Assemble and export the legacy curvature-threshold neutral scale audit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .common import repository_path
from .curvature_mass_functional import (
    load_curvature_activation_from_legacy_artifacts,
    load_curvature_mass_functional_from_legacy_artifacts,
)
from .legacy_artifact_parser import index_legacy_curvature_artifacts
from .legacy_curvature_threshold import (
    LegacyCurvatureScaleReport,
    LegacyCurvatureScaleResult,
    LegacyNeutralScaleCandidate,
)
from .neutral_curvature_mapping import derive_or_locate_neutral_curvature_mapping
from .propagation_radius import derive_or_locate_neutrino_propagation_radius


ARTIFACT_PATHS = {
    "manifest": "artifacts/BHSM_legacy_curvature_threshold_manifest_v1_1.json",
    "index": "artifacts/BHSM_legacy_curvature_artifact_index_v1_1.json",
    "functional": "artifacts/BHSM_curvature_mass_functional_v1_1.json",
    "radius": "artifacts/BHSM_neutrino_propagation_radius_search_v1_1.json",
    "mapping": "artifacts/BHSM_neutral_curvature_mapping_v1_1.json",
    "candidate": "artifacts/BHSM_legacy_neutral_scale_candidate_v1_1.json",
    "report": "artifacts/BHSM_legacy_neutral_scale_report_v1_1.json",
    "claims": "artifacts/BHSM_legacy_curvature_claim_policy_v1_1.json",
}

REQUIRED_STATEMENTS = (
    "The legacy curvature-threshold mass functional supplies a candidate mass bridge, not an empirical neutrino mass prediction by itself.",
    "A physical BHSM neutrino mass requires both a propagation/localization scale and a neutral curvature mapping with physical units.",
    "Legacy particle threshold tables are treated as illustrative calibration examples, not no-fit BHSM derivations.",
    "The electron-neutrino upper limit, PDG values, and W mass are not used as theorem inputs.",
)


def build_legacy_neutral_scale_candidate(
    repository: str | Path | None = None,
) -> LegacyNeutralScaleCandidate:
    functional = load_curvature_mass_functional_from_legacy_artifacts(repository)
    radius = derive_or_locate_neutrino_propagation_radius(repository)
    mapping = derive_or_locate_neutral_curvature_mapping(repository)
    complete = radius.value_m is not None and mapping.curvature_value_per_m2 is not None
    status = (
        "CONDITIONAL_DIMENSIONFUL_SCALE_CANDIDATE"
        if complete
        else "OPEN_MISSING_PROPAGATION_LOCALIZATION_RADIUS"
    )
    return LegacyNeutralScaleCandidate(
        candidate_key="legacy_curvature_threshold_neutral_scale",
        candidate_status=status,
        mass_functional_available=functional.candidate_status == "ARTIFACT_BACKED_CURVATURE_MASS_FUNCTIONAL",
        propagation_radius_available=radius.value_m is not None,
        neutral_curvature_mapping_available=mapping.dimensionless_curvature_response_available,
        physical_curvature_units_available=mapping.physical_curvature_units_available,
        dimensionful_mass_possible=complete,
        dimensionful_mass_eV=None,
        dimensionful_mass_GeV=None,
        claim_boundary="The legacy functional is a bridge candidate; radius and physical curvature units are independent required inputs.",
        remaining_missing_object=f"{radius.remaining_missing_object}; {mapping.remaining_missing_object}",
    )


def build_legacy_curvature_scale_report(
    repository: str | Path | None = None,
) -> LegacyCurvatureScaleReport:
    artifacts = index_legacy_curvature_artifacts(repository)
    functional = load_curvature_mass_functional_from_legacy_artifacts(repository)
    activation = load_curvature_activation_from_legacy_artifacts(repository)
    radius = derive_or_locate_neutrino_propagation_radius(repository)
    mapping = derive_or_locate_neutral_curvature_mapping(repository)
    candidate = build_legacy_neutral_scale_candidate(repository)
    result = LegacyCurvatureScaleResult(
        artifact_key="legacy_curvature_threshold_neutral_scale_result",
        source_file=functional.source_file,
        source_document_title=functional.source_document_title,
        source_equation=functional.source_equation,
        extracted_formula=functional.mass_formula,
        candidate_status=candidate.candidate_status,
        mass_functional_available=True,
        curvature_operator_available=True,
        activation_number_available=True,
        mass_gap_action_available=True,
        propagation_radius_available=candidate.propagation_radius_available,
        neutral_curvature_mapping_available=candidate.neutral_curvature_mapping_available,
        dimensionful_mass_possible=candidate.dimensionful_mass_possible,
        dimensionful_mass_eV=None,
        dimensionful_mass_GeV=None,
        empirical_derivation_inputs_used=False,
        reference_values_used_as_theorem_inputs=False,
        electron_neutrino_limit_used_as_derivation_input=False,
        w_mass_used_as_theorem_input=False,
        claim_boundary=(
            "Artifact-backed legacy mass functional plus dimensionless BHSM neutral response only. "
            "No eV/GeV mass follows until r_prop and k_neutral,eff have physical units."
        ),
        remaining_missing_object=candidate.remaining_missing_object,
    )
    return LegacyCurvatureScaleReport(
        report_name="BHSM Legacy Curvature-Threshold Neutral Scale Audit",
        version="1.1",
        artifacts=artifacts,
        curvature_mass_functional=functional,
        curvature_activation=activation,
        propagation_radius=radius,
        neutral_curvature_mapping=mapping,
        scale_candidate=candidate,
        result=result,
        mass_gap_action_support="ARTIFACT_BACKED_LEGACY_SCALAR_EFT_SUPPORT",
        hyperspherical_action_support="ARTIFACT_BACKED_LEGACY_S3_ACTION_SUPPORT",
        legacy_particle_tables_used_as_derivation_inputs=False,
        frozen_predictions_changed=False,
        production_physics_model_logic_changed=False,
        internet_required=False,
        external_hep_tools_required=False,
        public_status="structural architecture integrated conditional; numerical closure open",
    )


def legacy_curvature_scale_report_to_markdown(report: LegacyCurvatureScaleReport) -> str:
    lines = [
        "# BHSM Legacy Curvature-Threshold Neutral Scale Audit",
        "",
        f"Status: `{report.result.candidate_status}`.",
        f"Mass functional: `{report.curvature_mass_functional.candidate_status}`.",
        "",
        *REQUIRED_STATEMENTS,
        "",
        "| Gate | Result |",
        "| --- | --- |",
        f"| Curvature mass functional | `{report.curvature_mass_functional.candidate_status}` |",
        f"| Propagation radius | `{report.propagation_radius.status}` |",
        f"| Neutral physical curvature map | `{report.neutral_curvature_mapping.status}` |",
        f"| Dimensionful mass output | `{'available' if report.result.dimensionful_mass_possible else 'not produced'}` |",
        "",
        f"Remaining object: {report.result.remaining_missing_object}.",
        "",
    ]
    return "\n".join(lines)


def _claim_policy() -> dict[str, Any]:
    return {
        "artifact_name": "BHSM Legacy Curvature-Threshold Claim Policy",
        "version": "1.1",
        "allowed": [
            "BHSM includes legacy curvature-threshold mass artifacts.",
            "The curvature mass functional m = (c^2/(2G)) r^2 k_loc is available as an author-supplied theory artifact.",
            "The legacy curvature functional may serve as a conditional bridge from curvature threshold response to mass if BHSM supplies r_prop and k_neutral,eff.",
            "The sprint distinguishes curvature mass functional support from final neutrino eV/GeV closure.",
        ],
        "forbidden": [
            "BHSM empirically validates neutrino mass.",
            "BHSM centrally measures electron-neutrino mass.",
            "The electron-neutrino upper limit is used to set the scale.",
            "PDG/reference values are theorem inputs.",
            "W calibration is used as the neutral scale.",
            "Legacy particle threshold tables are no-fit BHSM predictions.",
            "A curvature mass functional alone produces a physical neutrino mass without r_prop and k_neutral,eff.",
        ],
        "required_statements": list(REQUIRED_STATEMENTS),
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
    }


def write_legacy_curvature_scale_artifacts(
    repository: str | Path | None = None,
) -> LegacyCurvatureScaleReport:
    root = repository_path(repository)
    report = build_legacy_curvature_scale_report(root)
    payloads: dict[str, Any] = {
        "manifest": {
            "artifact_name": "BHSM Legacy Curvature-Threshold Manifest",
            "version": "1.1",
            "artifact_paths": list(ARTIFACT_PATHS.values()),
            "status": report.result.candidate_status,
            "curvature_mass_functional_status": report.curvature_mass_functional.candidate_status,
            "frozen_predictions_changed": False,
            "internet_required": False,
        },
        "index": {"artifacts": [row.to_dict() for row in report.artifacts]},
        "functional": report.curvature_mass_functional.to_dict(),
        "radius": report.propagation_radius.to_dict(),
        "mapping": report.neutral_curvature_mapping.to_dict(),
        "candidate": report.scale_candidate.to_dict(),
        "report": report.to_dict(),
        "claims": _claim_policy(),
    }
    for key, relative in ARTIFACT_PATHS.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payloads[key], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report

