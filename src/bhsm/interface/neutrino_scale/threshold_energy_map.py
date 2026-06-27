"""Attempt the BHSM neutral curvature-threshold to energy map."""

from __future__ import annotations

from pathlib import Path

from .boundary_measure import analyze_neutral_boundary_measure
from .common import ThresholdEnergyMap


def build_threshold_energy_map(
    repository: str | Path | None = None,
) -> ThresholdEnergyMap:
    measure = analyze_neutral_boundary_measure(repository)
    return ThresholdEnergyMap(
        map_key="neutral_curvature_threshold_to_energy",
        formula="m_eff[eV] = neutral_scale[eV] * dimensionless_response",
        status="OPEN_MISSING_THRESHOLD_TO_ENERGY_MAP",
        threshold_source="artifacts/neutral_operator_no_fit_output_v1.json:kappa_nu",
        energy_scale_source=None,
        neutral_scale_eV=None,
        neutral_scale_GeV=None,
        unit_anchor_available=False,
        transport_normalization_available=False,
        missing_object=(
            "artifact-backed threshold-to-energy map, neutral unit anchor, and transport normalization; "
            f"boundary measure also lacks {measure.missing_object}"
        ),
        claim_boundary="The dimensionless curvature threshold is not promoted to an energy without a sourced unit map.",
    )

