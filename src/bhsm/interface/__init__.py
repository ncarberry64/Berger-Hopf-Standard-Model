"""Review-oriented BHSM geometry, unit, solver, and validation interfaces."""

from .constants import default_bhsm_constants
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
from .speculative import SpeculativeCandidate, SpeculativeCandidateRegistry
from .theorem_blockers import TheoremBlocker, TheoremBlockerRegistry, attempt_theorem_closure
from .solver import ParticleMassSolver, SolverResult
from .units import GeometricUnitMapper
from .validation import ExperimentalValue, ValidationComparison, curated_fallback_references

__all__ = [
    "ExperimentalValue",
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
    "PredictionGallery",
    "PredictionGalleryEntry",
    "SpeculativeCandidate",
    "SpeculativeCandidateRegistry",
    "TheoremBlocker",
    "TheoremBlockerRegistry",
    "SolverResult",
    "ValidationComparison",
    "curated_fallback_references",
    "default_prediction_registry",
    "default_bhsm_constants",
    "build_prediction_report",
    "build_prediction_gallery",
    "attempt_theorem_closure",
    "check_notebook_pack",
    "notebook_pack_manifest",
    "load_reference_with_fallback",
]
