"""One-way comparison of model outputs with provenance-tagged references."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from math import isfinite
from typing import Any, Literal

ReferenceKind = Literal["central_value", "upper_limit", "lower_limit", "range"]


@dataclass
class ExperimentalValue:
    """External reference that is never used as a derivation input."""

    particle_key: str
    reference_kind: ReferenceKind
    source_label: str
    value_gev: float | None = None
    uncertainty_gev: float | None = None
    lower_gev: float | None = None
    upper_gev: float | None = None
    source_url: str | None = None
    confidence_level: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.reference_kind == "central_value" and self.value_gev is None:
            raise ValueError("central_value references require value_gev")
        if self.reference_kind == "upper_limit" and self.upper_gev is None:
            raise ValueError("upper_limit references require upper_gev")
        if self.reference_kind == "lower_limit" and self.lower_gev is None:
            raise ValueError("lower_limit references require lower_gev")
        if self.reference_kind == "range" and (self.lower_gev is None or self.upper_gev is None):
            raise ValueError("range references require lower_gev and upper_gev")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationComparison:
    """Structured result of a one-way experimental comparison."""

    particle_key: str
    predicted_mass_gev: float
    reference: ExperimentalValue
    delta_gev: float | None = None
    absolute_delta_gev: float | None = None
    relative_delta: float | None = None
    sigma_delta: float | None = None
    below_upper_limit: bool | None = None
    upper_limit_margin_gev: float | None = None
    above_lower_limit: bool | None = None
    lower_limit_margin_gev: float | None = None
    inside_range: bool | None = None
    distance_to_range: float | None = None
    comparison_status: str = "COMPARISON_ONLY_NOT_EMPIRICAL_VALIDATION"

    @classmethod
    def compare(
        cls, predicted_mass_gev: float, reference: ExperimentalValue
    ) -> "ValidationComparison":
        """Compare without feeding the reference back into model calculation."""

        predicted = float(predicted_mass_gev)
        if not isfinite(predicted):
            raise ValueError("predicted_mass_gev must be finite")
        result = cls(reference.particle_key, predicted, reference)
        if reference.reference_kind == "central_value":
            assert reference.value_gev is not None
            result.delta_gev = predicted - reference.value_gev
            result.absolute_delta_gev = abs(result.delta_gev)
            if reference.value_gev != 0.0:
                result.relative_delta = result.absolute_delta_gev / abs(reference.value_gev)
            if reference.uncertainty_gev and reference.uncertainty_gev > 0.0:
                result.sigma_delta = result.delta_gev / reference.uncertainty_gev
        elif reference.reference_kind == "upper_limit":
            assert reference.upper_gev is not None
            result.below_upper_limit = predicted <= reference.upper_gev
            result.upper_limit_margin_gev = reference.upper_gev - predicted
        elif reference.reference_kind == "lower_limit":
            assert reference.lower_gev is not None
            result.above_lower_limit = predicted >= reference.lower_gev
            result.lower_limit_margin_gev = predicted - reference.lower_gev
        else:
            assert reference.lower_gev is not None and reference.upper_gev is not None
            result.inside_range = reference.lower_gev <= predicted <= reference.upper_gev
            if result.inside_range:
                result.distance_to_range = 0.0
            else:
                result.distance_to_range = min(
                    abs(predicted - reference.lower_gev), abs(predicted - reference.upper_gev)
                )
        return result

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["reference"] = self.reference.to_dict()
        payload["reference_used_as_derivation_input"] = False
        return payload


def curated_fallback_references() -> dict[str, ExperimentalValue]:
    """Return offline references with primary-source provenance metadata."""

    return {
        "W_boson": ExperimentalValue(
            particle_key="W_boson",
            reference_kind="central_value",
            value_gev=80.3692,
            uncertainty_gev=0.0133,
            source_label="Particle Data Group 2024 W-boson listing",
            source_url="https://pdg.lbl.gov/2024/listings/rpp2024-list-w-boson.pdf",
            metadata={"reference_role": "comparison_or_explicit_calibration_only"},
        ),
        "electron_neutrino": ExperimentalValue(
            particle_key="electron_neutrino",
            reference_kind="upper_limit",
            upper_gev=0.45e-9,
            source_label="KATRIN latest-result kinematic upper limit",
            source_url="https://www.katrin.kit.edu/1271.php",
            confidence_level="90% CL",
            metadata={
                "reference_role": "upper_limit_comparison_only",
                "not_a_measured_central_mass": True,
            },
        ),
    }
