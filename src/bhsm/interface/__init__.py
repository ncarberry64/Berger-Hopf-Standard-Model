"""Review-oriented BHSM geometry, unit, solver, and validation interfaces."""

from .constants import default_bhsm_constants
from .artifact_adapters import artifact_prediction_values, compute_artifact
from .artifact_report import ArtifactPredictionReport, build_artifact_prediction_report
from .artifact_sources import ArtifactSource, ArtifactSourceIndex, discover_bhsm_artifacts
from .formula_registry import FormulaCallableEntry, FormulaRegistry, evaluate_formula
from .geometry import HypersphericalGeometry
from .gallery import PredictionGallery, PredictionGalleryEntry, build_prediction_gallery
from .live_pdg import LivePDGProvider, PDGCache, PDGFetchResult
from .notebook_pack import check_notebook_pack, notebook_pack_manifest
from .pdg_interface import load_reference_with_fallback
from .predictions import (
    PredictionRegistry,
    PredictionRegistryEntry,
    PredictionRunConfig,
    PredictionRunResult,
    PredictionStatus,
    default_prediction_registry,
)
from .report import PredictionReport, build_prediction_report
from .provenance import ProvenanceChain, ProvenanceRecord, ValueWithProvenance
from .speculative import SpeculativeCandidate, SpeculativeCandidateRegistry
from .theorem_blockers import TheoremBlocker, TheoremBlockerRegistry, attempt_theorem_closure
from .theorem_closure import TheoremClosureReport, TheoremClosureResult, build_theorem_closure_report, evaluate_theorem
from .minimal_action import MinimalActionClosureReport, MinimalActionClosureResult, build_minimal_action_report, close_minimal_action
from .neutrino_propagation import (
    NeutrinoNumericalClosureReport,
    NeutrinoPropagationClosureResult,
    build_neutrino_propagation_report,
    build_numerical_closure,
    compute_neutrino_propagation_mass,
)
from .solver import ParticleMassSolver, SolverResult
from .units import GeometricUnitMapper
from .validation import ExperimentalValue, ValidationComparison, curated_fallback_references

__all__ = [
    "ExperimentalValue",
    "ArtifactPredictionReport",
    "ArtifactSource",
    "ArtifactSourceIndex",
    "FormulaCallableEntry",
    "FormulaRegistry",
    "GeometricUnitMapper",
    "HypersphericalGeometry",
    "LivePDGProvider",
    "PDGCache",
    "PDGFetchResult",
    "ParticleMassSolver",
    "PredictionRegistry",
    "PredictionRegistryEntry",
    "PredictionReport",
    "PredictionRunConfig",
    "PredictionRunResult",
    "PredictionStatus",
    "ProvenanceChain",
    "ProvenanceRecord",
    "PredictionGallery",
    "PredictionGalleryEntry",
    "SpeculativeCandidate",
    "SpeculativeCandidateRegistry",
    "TheoremBlocker",
    "TheoremBlockerRegistry",
    "TheoremClosureReport",
    "TheoremClosureResult",
    "MinimalActionClosureReport",
    "MinimalActionClosureResult",
    "NeutrinoNumericalClosureReport",
    "NeutrinoPropagationClosureResult",
    "SolverResult",
    "ValidationComparison",
    "ValueWithProvenance",
    "artifact_prediction_values",
    "curated_fallback_references",
    "default_prediction_registry",
    "default_bhsm_constants",
    "build_prediction_report",
    "build_prediction_gallery",
    "build_artifact_prediction_report",
    "compute_artifact",
    "discover_bhsm_artifacts",
    "evaluate_formula",
    "evaluate_theorem",
    "attempt_theorem_closure",
    "build_theorem_closure_report",
    "build_minimal_action_report",
    "close_minimal_action",
    "build_neutrino_propagation_report",
    "build_numerical_closure",
    "compute_neutrino_propagation_mass",
    "check_notebook_pack",
    "notebook_pack_manifest",
    "load_reference_with_fallback",
]
