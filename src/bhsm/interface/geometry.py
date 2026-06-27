"""Replaceable hyperspherical/Berger-Hopf geometry interface."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite, sqrt
from typing import Any, Callable, Mapping

DEFAULT_INTERFACE_FORMULA = "DEFAULT_INTERFACE_FORMULA"
PLACEHOLDER_UNTIL_BHSM_THEOREM_SUPPLIED = "PLACEHOLDER_UNTIL_BHSM_THEOREM_SUPPLIED"

MetricFn = Callable[["HypersphericalGeometry"], float]
TensionFn = Callable[["HypersphericalGeometry"], float]
ResidualFn = Callable[[float, "HypersphericalGeometry", Any, float, Mapping[str, float]], float]


@dataclass
class HypersphericalGeometry:
    """Geometry input with explicit placeholder defaults and callable overrides."""

    curvature_indices: tuple[float, ...]
    hopf_coefficients: tuple[float, ...]
    radius: float = 1.0
    anisotropy: float = 1.0
    boundary_coupling: float = 1.0
    sector: str | None = None
    mode_label: str | None = None
    model_constants: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, object] = field(default_factory=dict)
    metric_fn: MetricFn | None = field(default=None, repr=False, compare=False)
    tension_fn: TensionFn | None = field(default=None, repr=False, compare=False)
    residual_fn: ResidualFn | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        self.curvature_indices = tuple(float(value) for value in self.curvature_indices)
        self.hopf_coefficients = tuple(float(value) for value in self.hopf_coefficients)
        for name in ("radius", "anisotropy", "boundary_coupling"):
            value = float(getattr(self, name))
            if not isfinite(value):
                raise ValueError(f"{name} must be finite")
            setattr(self, name, value)
        if self.radius <= 0.0:
            raise ValueError("radius must be positive")

    def mode_norm(self) -> float:
        """Return the Euclidean norm of the curvature-index tuple."""

        return sqrt(sum(value * value for value in self.curvature_indices))

    def hopf_weight(self) -> float:
        """Return the Euclidean norm of the Hopf-coefficient tuple."""

        return sqrt(sum(value * value for value in self.hopf_coefficients))

    def geometric_metric(self) -> float:
        """Evaluate a supplied metric or the labeled interface placeholder."""

        if self.metric_fn is not None:
            value = float(self.metric_fn(self))
        else:
            value = self.radius**2 * (
                self.mode_norm() ** 2 + self.anisotropy**2 * self.hopf_weight() ** 2
            )
        if not isfinite(value) or value < 0.0:
            raise ValueError("geometric metric must be finite and nonnegative")
        return value

    def geometric_tension(self) -> float:
        """Evaluate a supplied tension or the labeled interface placeholder."""

        if self.tension_fn is not None:
            value = float(self.tension_fn(self))
        else:
            value = self.boundary_coupling * sqrt(self.geometric_metric())
        if not isfinite(value):
            raise ValueError("geometric tension must be finite")
        return value

    def equilibrium_residual(
        self,
        mass_gev: float,
        mapper: Any,
        sector_factor: float = 1.0,
        equilibrium_params: Mapping[str, float] | None = None,
        residual_fn: ResidualFn | None = None,
    ) -> float:
        """Return a theorem-supplied or default mass-equilibrium residual."""

        params = equilibrium_params or {}
        selected = residual_fn or self.residual_fn
        if selected is not None:
            return float(selected(float(mass_gev), self, mapper, float(sector_factor), params))
        target = mapper.tension_to_mass_gev(self.geometric_tension() * float(sector_factor))
        return float(mass_gev) - target

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable geometry description."""

        return {
            "curvature_indices": list(self.curvature_indices),
            "hopf_coefficients": list(self.hopf_coefficients),
            "radius": self.radius,
            "anisotropy": self.anisotropy,
            "boundary_coupling": self.boundary_coupling,
            "sector": self.sector,
            "mode_label": self.mode_label,
            "model_constants": dict(self.model_constants),
            "metadata": dict(self.metadata),
            "formula_status": (
                "USER_SUPPLIED_BHSM_THEOREM_MODE"
                if any((self.metric_fn, self.tension_fn, self.residual_fn))
                else f"{DEFAULT_INTERFACE_FORMULA}; {PLACEHOLDER_UNTIL_BHSM_THEOREM_SUPPLIED}"
            ),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any], **callables: Any) -> "HypersphericalGeometry":
        """Restore a geometry record; callables must be supplied explicitly."""

        keys = {
            "curvature_indices",
            "hopf_coefficients",
            "radius",
            "anisotropy",
            "boundary_coupling",
            "sector",
            "mode_label",
            "model_constants",
            "metadata",
        }
        values = {key: payload[key] for key in keys if key in payload}
        values.update(callables)
        return cls(**values)
