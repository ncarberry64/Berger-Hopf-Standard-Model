"""Review-oriented BHSM geometry, unit, solver, and validation interfaces."""

from .constants import default_bhsm_constants
from .geometry import HypersphericalGeometry
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
from .solver import ParticleMassSolver, SolverResult
from .units import GeometricUnitMapper
from .validation import ExperimentalValue, ValidationComparison, curated_fallback_references

__all__ = [
    "ExperimentalValue",
    "GeometricUnitMapper",
    "HypersphericalGeometry",
    "ParticleMassSolver",
    "PredictionRegistry",
    "PredictionRegistryEntry",
    "PredictionReport",
    "PredictionRunConfig",
    "PredictionRunResult",
    "PredictionStatus",
    "SolverResult",
    "ValidationComparison",
    "curated_fallback_references",
    "default_prediction_registry",
    "default_bhsm_constants",
    "build_prediction_report",
    "load_reference_with_fallback",
]
