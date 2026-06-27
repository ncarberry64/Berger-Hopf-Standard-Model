"""Compatibility entry point for the historical v1.1 neutral-scale candidate.

The v1.2 radius/curvature closure supersedes this candidate for physical mass
output because it adds explicit unit and dimensional-consistency gates.
"""

from .legacy_scale_report import build_legacy_neutral_scale_candidate
from .neutral_radius_curvature_report import build_neutral_radius_curvature_closure

__all__ = [
    "build_legacy_neutral_scale_candidate",
    "build_neutral_radius_curvature_closure",
]
