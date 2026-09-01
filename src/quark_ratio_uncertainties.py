"""Uncertainty and tolerance scaffolds for BHSM quark-ratio comparisons."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from bhsm_v1 import declared_tolerance_bands


@dataclass(frozen=True)
class RatioUncertainty:
    """Uncertainty propagation result for a ratio."""

    ratio: float
    uncertainty: float | None
    pull: float | None
    notes: tuple[str, ...]


def propagate_ratio_uncertainty(
    numerator: float,
    denominator: float,
    numerator_uncertainty: float | None,
    denominator_uncertainty: float | None,
    predicted: float | None = None,
) -> RatioUncertainty:
    """Propagate independent relative uncertainties for numerator/denominator."""

    if denominator == 0:
        raise ValueError("denominator must be nonzero")
    ratio = float(numerator) / float(denominator)
    if numerator_uncertainty is None or denominator_uncertainty is None:
        return RatioUncertainty(
            ratio=ratio,
            uncertainty=None,
            pull=None,
            notes=("Input uncertainties are incomplete; pull is not computed.",),
        )
    rel = sqrt((numerator_uncertainty / numerator) ** 2 + (denominator_uncertainty / denominator) ** 2)
    uncertainty = abs(ratio) * rel
    pull = None if predicted is None or uncertainty == 0 else (float(predicted) - ratio) / uncertainty
    return RatioUncertainty(
        ratio=ratio,
        uncertainty=uncertainty,
        pull=pull,
        notes=("Independent uncertainty propagation scaffold.",),
    )


def quark_tolerance_band() -> float:
    """Return the fixed scheme-aware quark-ratio tolerance band."""

    return float(declared_tolerance_bands()["quark_ratios_scheme_aware"])


def classify_tolerance(
    relative_error: float | None,
    scheme_consistent: bool,
    final: bool,
    approximate: bool,
) -> str:
    """Classify a quark-ratio comparison against fixed tolerance rules."""

    if relative_error is None:
        return "NO_NUMERICAL_REFERENCE"
    passes = relative_error <= quark_tolerance_band()
    if final and scheme_consistent:
        return "PASS" if passes else "REAL_BHSM_TENSION"
    if scheme_consistent and approximate:
        return "APPROX_PASS" if passes else "APPROX_SCAFFOLD_TENSION"
    if not scheme_consistent:
        return "SCHEME_SENSITIVE"
    return "OPEN"
