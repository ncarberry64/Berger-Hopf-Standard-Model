"""Offline source inventory for a BHSM neutral unit anchor."""

from __future__ import annotations

from pathlib import Path

from .common import NeutralScaleSource, repository_path


ARTIFACT_SOURCES_CHECKED = (
    "artifacts/BHSM_boundary_no_fit_prediction_package_v1.json",
    "artifacts/neutral_operator_no_fit_output_v1.json",
    "artifacts/BHSM_author_ontology_v0_8.json",
    "artifacts/canonical_profile_hessian_theorem_v1.json",
    "artifacts/frozen_constants_v2.json",
    "artifacts/BHSM_prediction_report_example_v0_1.json",
    "src/bhsm/interface/constants.py",
    "src/bhsm/interface/units.py",
    "theory/theorem_discharge_neutral_effective_action.md",
    "theory/collective_curvature_threshold_layer.md",
)


def search_neutral_scale_sources(
    repository: str | Path | None = None,
) -> tuple[NeutralScaleSource, ...]:
    """Classify known local scale sources without promoting prose into a unit theorem."""

    root = repository_path(repository)
    rows = (
        ("boundary_profile", ARTIFACT_SOURCES_CHECKED[0], "DIMENSIONLESS_ARTIFACT", False,
         "Contains tau, sigma, and kappa_H without eV/GeV units."),
        ("neutral_kernel", ARTIFACT_SOURCES_CHECKED[1], "DIMENSIONLESS_ARTIFACT", True,
         "Contains K_nu, g_nu, beta_nu, and kappa_nu as dimensionless boundary data."),
        ("author_ontology", ARTIFACT_SOURCES_CHECKED[2], "AUTHOR_ONTOLOGY_CONDITIONAL", True,
         "Defines propagation-locked curvature response and symbolic dmu_boundary dt, but no physical unit anchor."),
        ("profile_hessian", ARTIFACT_SOURCES_CHECKED[3], "DIMENSIONLESS_ARTIFACT", False,
         "Identifies kappa_H and mu_H internally; it supplies no neutral threshold-to-energy map."),
        ("frozen_constants", ARTIFACT_SOURCES_CHECKED[4], "DIMENSIONLESS_ARTIFACT", False,
         "Lists internal constants without an eV/GeV neutral conversion."),
        ("w_anchored_example", ARTIFACT_SOURCES_CHECKED[5], "EMPIRICAL_FORBIDDEN", False,
         "Uses the W mass as a calibration anchor and is forbidden as neutral-scale theorem input."),
        ("unit_conversions", ARTIFACT_SOURCES_CHECKED[6], "REFERENCE_ONLY_FOR_COMPARISON", False,
         "Defines exact conversion constants but no BHSM energy magnitude."),
        ("empirical_mapper", ARTIFACT_SOURCES_CHECKED[7], "EMPIRICAL_FORBIDDEN", False,
         "Can map a calibrated tension to GeV only after an empirical anchor."),
        ("neutral_action_note", ARTIFACT_SOURCES_CHECKED[8], "AUTHOR_ONTOLOGY_CONDITIONAL", True,
         "Supplies symbolic neutral-action structure, not a normalized physical boundary measure."),
        ("curvature_threshold_note", ARTIFACT_SOURCES_CHECKED[9], "AUTHOR_ONTOLOGY_CONDITIONAL", True,
         "Supplies threshold structure, not a physical threshold energy."),
    )
    return tuple(
        NeutralScaleSource(
            source_key=key,
            source_path=path,
            source_category=category,
            discovered=(root / path).is_file(),
            machine_readable=path.endswith((".json", ".py")),
            neutral_scale_link_present=linked,
            notes=notes,
        )
        for key, path, category, linked, notes in rows
    )

