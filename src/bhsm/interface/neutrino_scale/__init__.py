"""BHSM neutral dimensionful-scale theorem audit."""

from .artifact_search import ARTIFACT_SOURCES_CHECKED, search_neutral_scale_sources
from .boundary_measure import analyze_neutral_boundary_measure
from .common import (
    BoundaryMeasureCandidate,
    NeutralDimensionfulScaleResult,
    NeutralScaleCandidate,
    NeutralScaleClosureReport,
    NeutralScaleClosureResult,
    NeutralScaleSource,
    NeutralUnitMap,
    ThresholdEnergyMap,
)
from .neutral_scale_candidates import build_neutral_scale_candidates
from .curvature_mass_functional import (
    load_curvature_activation_from_legacy_artifacts,
    load_curvature_mass_functional_from_legacy_artifacts,
)
from .legacy_artifact_parser import index_legacy_curvature_artifacts
from .legacy_curvature_threshold import (
    CurvatureActivation,
    CurvatureMassFunctional,
    LegacyCurvatureArtifact,
    LegacyCurvatureScaleReport,
    LegacyCurvatureScaleResult,
    LegacyNeutralScaleCandidate,
    NeutralCurvatureMapping,
    PropagationLocalizationRadius,
)
from .legacy_scale_report import (
    ARTIFACT_PATHS as LEGACY_ARTIFACT_PATHS,
    REQUIRED_STATEMENTS as LEGACY_REQUIRED_STATEMENTS,
    build_legacy_curvature_scale_report,
    build_legacy_neutral_scale_candidate,
    legacy_curvature_scale_report_to_markdown,
    write_legacy_curvature_scale_artifacts,
)
from .neutral_curvature_mapping import derive_or_locate_neutral_curvature_mapping
from .propagation_radius import derive_or_locate_neutrino_propagation_radius
from .scale_report import (
    ARTIFACT_PATHS,
    REQUIRED_STATEMENTS,
    build_neutral_scale_report,
    neutral_scale_report_to_markdown,
    write_neutral_scale_artifacts,
)
from .threshold_energy_map import build_threshold_energy_map
from .unit_map import derive_neutral_scale_law, map_dimensionless_response

__all__ = [
    "ARTIFACT_PATHS",
    "ARTIFACT_SOURCES_CHECKED",
    "BoundaryMeasureCandidate",
    "CurvatureActivation",
    "CurvatureMassFunctional",
    "LEGACY_ARTIFACT_PATHS",
    "LEGACY_REQUIRED_STATEMENTS",
    "LegacyCurvatureArtifact",
    "LegacyCurvatureScaleReport",
    "LegacyCurvatureScaleResult",
    "LegacyNeutralScaleCandidate",
    "NeutralDimensionfulScaleResult",
    "NeutralScaleCandidate",
    "NeutralScaleClosureReport",
    "NeutralScaleClosureResult",
    "NeutralScaleSource",
    "NeutralUnitMap",
    "NeutralCurvatureMapping",
    "PropagationLocalizationRadius",
    "REQUIRED_STATEMENTS",
    "ThresholdEnergyMap",
    "analyze_neutral_boundary_measure",
    "build_neutral_scale_candidates",
    "build_legacy_curvature_scale_report",
    "build_legacy_neutral_scale_candidate",
    "build_neutral_scale_report",
    "build_threshold_energy_map",
    "derive_neutral_scale_law",
    "derive_or_locate_neutral_curvature_mapping",
    "derive_or_locate_neutrino_propagation_radius",
    "index_legacy_curvature_artifacts",
    "legacy_curvature_scale_report_to_markdown",
    "load_curvature_activation_from_legacy_artifacts",
    "load_curvature_mass_functional_from_legacy_artifacts",
    "map_dimensionless_response",
    "neutral_scale_report_to_markdown",
    "search_neutral_scale_sources",
    "write_neutral_scale_artifacts",
    "write_legacy_curvature_scale_artifacts",
]
