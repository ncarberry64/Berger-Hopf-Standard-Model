"""BHSM neutrino propagation-mass numerical closure candidate."""

from .closure_report import (
    ARTIFACT_PATHS,
    build_neutrino_propagation_report,
    neutrino_propagation_report_to_markdown,
    write_neutrino_propagation_artifacts,
)
from .common import (
    BackgroundCoupling,
    CurvatureThreshold,
    EffectivePropagationMass,
    NeutralBoundaryField,
    NeutralKernelArtifact,
    NeutralScaleLaw,
    NeutrinoNumericalClosureReport,
    NeutrinoObservableMap,
    NeutrinoPropagationClosureResult,
    PropagationState,
    STATUS_TAXONOMY,
)
from .curvature_threshold import build_curvature_threshold, threshold_response
from .effective_mass import compute_neutrino_propagation_mass
from .neutral_kernel import build_neutral_boundary_field, load_neutral_kernel
from .numerical_closure import build_numerical_closure
from .observable_map import build_neutrino_observable_map
from .propagation_state import canonical_channel_states, normalized_state
from .validation_policy import neutrino_validation_policy

__all__ = [
    "ARTIFACT_PATHS",
    "BackgroundCoupling",
    "CurvatureThreshold",
    "EffectivePropagationMass",
    "NeutralBoundaryField",
    "NeutralKernelArtifact",
    "NeutralScaleLaw",
    "NeutrinoNumericalClosureReport",
    "NeutrinoObservableMap",
    "NeutrinoPropagationClosureResult",
    "PropagationState",
    "STATUS_TAXONOMY",
    "build_curvature_threshold",
    "build_neutral_boundary_field",
    "build_neutrino_observable_map",
    "build_neutrino_propagation_report",
    "build_numerical_closure",
    "canonical_channel_states",
    "compute_neutrino_propagation_mass",
    "load_neutral_kernel",
    "neutrino_propagation_report_to_markdown",
    "neutrino_validation_policy",
    "normalized_state",
    "threshold_response",
    "write_neutrino_propagation_artifacts",
]
