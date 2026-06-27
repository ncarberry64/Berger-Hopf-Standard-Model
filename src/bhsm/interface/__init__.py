"""Review-oriented BHSM geometry, unit, solver, and validation interfaces."""

from .constants import default_bhsm_constants
from .geometry import HypersphericalGeometry
from .pdg_interface import load_reference_with_fallback
from .solver import ParticleMassSolver, SolverResult
from .units import GeometricUnitMapper
from .validation import ExperimentalValue, ValidationComparison, curated_fallback_references

__all__ = [
    "ExperimentalValue",
    "GeometricUnitMapper",
    "HypersphericalGeometry",
    "ParticleMassSolver",
    "SolverResult",
    "ValidationComparison",
    "curated_fallback_references",
    "default_bhsm_constants",
    "load_reference_with_fallback",
]
