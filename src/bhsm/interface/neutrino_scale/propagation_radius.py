"""Search the local BHSM corpus for a neutral propagation localization radius."""

from __future__ import annotations

from pathlib import Path

from .common import repository_path
from .legacy_curvature_threshold import PropagationLocalizationRadius


RADIUS_SOURCE_CANDIDATES = (
    "artifacts/BHSM_author_ontology_v0_8.json",
    "artifacts/neutral_operator_no_fit_output_v1.json",
    "artifacts/BHSM_neutrino_numerical_closure_report_v0_9.json",
    "theory/theorem_discharge_neutral_effective_action.md",
    "theory/theorem_discharge_scalar_topographic_profile_input_classification.md",
    "artifacts/internal_profile_radius_normalization_v1.json",
)


def derive_or_locate_neutrino_propagation_radius(
    repository: str | Path | None = None,
) -> PropagationLocalizationRadius:
    root = repository_path(repository)
    checked = tuple(path for path in RADIUS_SOURCE_CANDIDATES if (root / path).is_file())
    return PropagationLocalizationRadius(
        symbol="r_prop",
        status="OPEN_MISSING_PROPAGATION_LOCALIZATION_RADIUS",
        value_m=None,
        source_file=None,
        candidates_checked=checked,
        empirical_radius_rejected=True,
        claim_boundary=(
            "BHSM names internal/profile radii, but no artifact identifies one as the physical neutral propagation or localization radius. "
            "The illustrative 10^-15 m legacy table radius and experimental de Broglie scales are not theorem inputs."
        ),
        remaining_missing_object="artifact-backed neutral propagation/localization radius in metres and its coupling to the neutral boundary mode",
    )

