"""Threshold/RG uncertainty closure helpers for BHSM QCD comparison."""

from __future__ import annotations

from dataclasses import dataclass


UNCERTAINTY_SCAFFOLD = "UNCERTAINTY_SCAFFOLD"
PRECISION_UNCERTAINTIES_REQUIRED = "PRECISION_UNCERTAINTIES_REQUIRED"


@dataclass(frozen=True)
class ThresholdUncertaintyRow:
    """One uncertainty-propagation closure row."""

    reference_set: str
    implemented: bool
    has_input_uncertainties: bool
    status: str
    limitations: tuple[str, ...]


def threshold_uncertainty_rows() -> tuple[ThresholdUncertaintyRow, ...]:
    """Return uncertainty closure rows for the v1.4 reference sets."""

    return (
        ThresholdUncertaintyRow(
            reference_set="MIXED_DEFAULT",
            implemented=True,
            has_input_uncertainties=False,
            status=UNCERTAINTY_SCAFFOLD,
            limitations=("Mixed schemes are not final precision inputs.",),
        ),
        ThresholdUncertaintyRow(
            reference_set="COMMON_SCALE_APPROX",
            implemented=True,
            has_input_uncertainties=False,
            status=UNCERTAINTY_SCAFFOLD,
            limitations=("Approximate running lacks validated common-scale uncertainties.",),
        ),
        ThresholdUncertaintyRow(
            reference_set="THRESHOLD_AWARE_APPROX",
            implemented=True,
            has_input_uncertainties=False,
            status=UNCERTAINTY_SCAFFOLD,
            limitations=("Threshold-aware scaffold is not two-/three-loop precision QCD.",),
        ),
        ThresholdUncertaintyRow(
            reference_set="PRECISION_QCD_PLACEHOLDER",
            implemented=False,
            has_input_uncertainties=False,
            status=PRECISION_UNCERTAINTIES_REQUIRED,
            limitations=("Validated precision-QCD inputs are required before final classification.",),
        ),
    )

